"""Low-level Hunter BLE client.

Connection and GATT enumeration follow the Android flow: connect to the
Bluetooth device, wait for GATT service discovery, then inspect services and
characteristics before selecting a protocol.
"""

from __future__ import annotations

import asyncio
import inspect
import logging
from datetime import datetime, timezone

from bleak.exc import BleakError
from bleak.backends.characteristic import BleakGATTCharacteristic
from bleak.backends.descriptor import BleakGATTDescriptor
from bleak_retry_connector import BleakClientWithServiceCache, establish_connection
from homeassistant.components import bluetooth
from homeassistant.core import HomeAssistant

from .gatt_attributes import (
    find_misclassified_characteristic,
    parse_characteristic_declaration,
)
from ..protocol.uuids import (
    BATTERY_LEVEL_UUID,
    CLIENT_ID_UUID,
    COMMAND_UUID,
    COUNTDOWN_UUID,
    NOTIFY_UUID,
    PASSCODE_UUID,
    STATUS_NOTIFY_UUID,
    SECOND_SERVICE_UUID,
)

_LOGGER = logging.getLogger(__name__)



class HunterBLEClient:
    """Low-level BLE I/O and discovered GATT inventory."""

    def __init__(
        self,
        hass: HomeAssistant,
        address: str,
    ) -> None:
        self._hass = hass
        self._address = address
        self._client: BleakClientWithServiceCache | None = None
        self._lock = asyncio.Lock()
        self._notification_callback = None
        self._notification_status: dict[str, str] = {}
        self._recovered_characteristics: dict[str, BleakGATTCharacteristic] = {}

    @property
    def connected(self) -> bool:
        return bool(self._client and self._client.is_connected)

    @property
    def service_uuids(self) -> set[str]:
        if self._client is None:
            return set()
        return {
            str(service.uuid).strip().lower()
            for service in self._client.services
        }

    @property
    def gatt_inventory(self) -> list[dict[str, object]]:
        """Return every discovered characteristic with handle and properties."""
        if self._client is None:
            return []
        inventory: list[dict[str, object]] = []
        for service in self._client.services:
            service_uuid = str(service.uuid).strip().lower()
            for characteristic in service.characteristics:
                inventory.append(
                    {
                        "service_uuid": service_uuid,
                        "uuid": str(characteristic.uuid).strip().lower(),
                        "handle": getattr(characteristic, "handle", None),
                        "properties": sorted(
                            str(prop).strip().lower()
                            for prop in characteristic.properties
                        ),
                        "descriptors": [
                            {
                                "uuid": str(descriptor.uuid).strip().lower(),
                                "handle": getattr(descriptor, "handle", None),
                            }
                            for descriptor in (getattr(characteristic, "descriptors", ()) or ())
                        ],
                    }
                )
        for uuid, characteristic in self._recovered_characteristics.items():
            if not any(item["uuid"] == uuid for item in inventory):
                inventory.append(
                    {
                        "service_uuid": str(characteristic.service_uuid).strip().lower(),
                        "uuid": uuid,
                        "handle": characteristic.handle,
                        "properties": sorted(str(prop).strip().lower() for prop in characteristic.properties),
                        "descriptors": [
                            {"uuid": str(item.uuid).strip().lower(), "handle": item.handle}
                            for item in characteristic.descriptors
                        ],
                        "recovered_from_declaration": True,
                    }
                )
        return sorted(
            inventory,
            key=lambda item: (
                str(item["service_uuid"]),
                item["handle"] if isinstance(item["handle"], int) else -1,
                str(item["uuid"]),
            ),
        )

    @property
    def writable_characteristics(self) -> list[dict[str, object]]:
        """Return discovered characteristics that advertise a write property."""
        return [
            item
            for item in self.gatt_inventory
            if {"write", "write-without-response"} & set(item["properties"])
        ]

    @property
    def notification_status(self) -> dict[str, str]:
        """Return the latest per-characteristic notification subscription result."""
        return dict(self._notification_status)

    @property
    def characteristic_uuids(self) -> set[str]:
        if self._client is None:
            return set()
        found = {
            str(characteristic.uuid).strip().lower()
            for service in self._client.services
            for characteristic in service.characteristics
        }
        return found | set(self._recovered_characteristics)

    def characteristic_object(self, uuid: str):
        """Return the exact characteristic object from the active GATT database."""
        target = str(uuid).strip().lower()
        if target in self._recovered_characteristics:
            return self._recovered_characteristics[target]
        if self._client is None:
            return None
        for service in self._client.services:
            for characteristic in service.characteristics:
                if str(characteristic.uuid).strip().lower() == target:
                    return characteristic
        return None

    def characteristic_handle(self, uuid: str) -> int | None:
        """Return the discovered ATT value handle for a characteristic UUID."""
        characteristic = self.characteristic_object(uuid)
        handle = getattr(characteristic, "handle", None)
        return handle if isinstance(handle, int) else None

    def characteristic_properties(self, uuid: str) -> set[str]:
        """Return properties reported by the connected GATT database."""
        target = str(uuid).strip().lower()
        recovered = self._recovered_characteristics.get(target)
        if recovered is not None:
            return {str(prop).strip().lower() for prop in recovered.properties}
        if self._client is None:
            return set()
        for service in self._client.services:
            for characteristic in service.characteristics:
                if str(characteristic.uuid).strip().lower() == target:
                    return {
                        str(prop).strip().lower()
                        for prop in characteristic.properties
                    }
        return set()

    @property
    def ff83_writable(self) -> bool:
        props = self.characteristic_properties(COMMAND_UUID)
        return bool({"write", "write-without-response"} & props)

    async def _resolve_device(self):
        """Resolve the current proxy-backed BLEDevice for this address."""
        device = bluetooth.async_ble_device_from_address(
            self._hass,
            self._address,
            connectable=True,
        )
        if inspect.isawaitable(device):
            device = await device
        if device is None:
            raise BleakError(f"Unable to locate BLE device {self._address}")
        return device

    async def connect(self) -> None:
        """Connect through HA Bluetooth and refresh incomplete cached GATT data."""
        async with self._lock:
            if self.connected:
                return

            self._notification_status = {}
            self._recovered_characteristics = {}
            device = await self._resolve_device()
            try:
                self._client = await establish_connection(
                    BleakClientWithServiceCache,
                    device,
                    name=f"Hunter BTT - {self._address}",
                    use_services_cache=True,
                )
                self._log_gatt_inventory()
                await self._recover_misclassified_characteristic(CLIENT_ID_UUID)
                self._log_gatt_inventory()

                # FFA5 is mandatory for the Android 6.1.49 FF81 serializer.
                # Android's database has FFA5 at value handle 0x0064, between
                # declaration 0x0063 and CCCD 0x0065. HA must not proceed using
                # an incomplete cached service collection.
                if (
                    SECOND_SERVICE_UUID in self.service_uuids
                    and self.characteristic_object(CLIENT_ID_UUID) is None
                ):
                    await self._refresh_gatt_services()
                    self._log_gatt_inventory()
            except Exception:
                active_client = self._client
                self._client = None
                self._recovered_characteristics = {}
                if active_client is not None:
                    try:
                        if active_client.is_connected:
                            await active_client.disconnect()
                    except Exception:
                        _LOGGER.debug(
                            "Unable to clean up failed Hunter BLE connection",
                            exc_info=True,
                        )
                raise

    async def _refresh_gatt_services(self) -> None:
        """Clear a suspect GATT cache and reconnect once with fresh discovery.

        This is scoped to the Android-known FFA5 characteristic. It does not
        switch transport: the refreshed BLEDevice is resolved through HA's
        Bluetooth integration, so ESPHome proxy routing remains in use.
        """
        stale_client = self._client
        if stale_client is None:
            return

        clear_cache = getattr(stale_client, "clear_cache", None)
        cache_cleared = False
        if callable(clear_cache):
            try:
                result = clear_cache()
                if inspect.isawaitable(result):
                    result = await result
                cache_cleared = bool(result)
            except Exception as err:
                _LOGGER.warning(
                    "Hunter GATT cache clear failed; forcing uncached discovery "
                    "on reconnect: %s",
                    err,
                )

        try:
            if stale_client.is_connected:
                await stale_client.disconnect()
        except Exception as err:
            _LOGGER.warning(
                "Hunter stale GATT client disconnect failed; continuing with "
                "an uncached proxy connection: %s",
                err,
            )
        finally:
            self._client = None
            self._notification_status = {}
            self._recovered_characteristics = {}

        # Re-resolve via Home Assistant so the ESPHome proxy's current BLE
        # device path is used, rather than carrying a potentially stale object.
        fresh_device = await self._resolve_device()
        _LOGGER.warning(
            "Hunter FFA5 missing after cached GATT discovery; retrying once "
            "with fresh service discovery (cache_cleared=%s)",
            cache_cleared,
        )
        self._client = await establish_connection(
            BleakClientWithServiceCache,
            fresh_device,
            name=f"Hunter BTT - {self._address} (fresh GATT discovery)",
            use_services_cache=False,
        )
        await self._recover_misclassified_characteristic(CLIENT_ID_UUID)
        if self.characteristic_object(CLIENT_ID_UUID) is None:
            _LOGGER.error(
                "Hunter FFA5 remains unavailable after uncached GATT discovery "
                "and declaration-based reconstruction through Home Assistant Bluetooth"
            )

    async def _recover_misclassified_characteristic(self, uuid: str) -> bool:
        """Rebuild a characteristic when Bleak grouped its declaration as a descriptor.

        The declaration is read through Bleak's characteristic-read API using
        a temporary characteristic object with the declaration's ATT handle.
        The returned bytes, not a hard-coded property list, establish the value
        handle, UUID, and properties. The reconstructed official Bleak object
        is passed directly to Bleak I/O methods, avoiding UUID/handle lookup
        against the malformed service collection.
        """
        target = str(uuid).strip().lower()
        if self._client is None or target in self._recovered_characteristics:
            return target in self._recovered_characteristics

        candidate = find_misclassified_characteristic(self._client.services, target)
        if candidate is None:
            _LOGGER.debug(
                "Hunter GATT declaration parser found no misclassified %s entry",
                target,
            )
            return False

        try:
            # 0x2803 is a GATT characteristic declaration attribute, not a
            # descriptor. Use the backend's characteristic-read operation
            # with a temporary Bleak object carrying the discovered handle;
            # the ESPHome backend forwards that handle as a raw GATT read.
            declaration_probe = BleakGATTCharacteristic(
                obj=getattr(candidate.declaration, "obj", None),
                handle=candidate.declaration.handle,
                uuid=str(candidate.declaration.uuid),
                properties=["read"],
                max_write_without_response_size=20,
                service=candidate.service,
            )
            declaration_bytes = bytes(
                await self._client.read_gatt_char(declaration_probe)
            )
            _LOGGER.info(
                "Hunter GATT raw characteristic declaration handle=0x%04X "
                "bytes=%s",
                candidate.declaration.handle,
                declaration_bytes.hex(" ").upper(),
            )
            parsed = parse_characteristic_declaration(declaration_bytes, target)

            # Validate the declaration against all three adjacent attributes
            # exposed by this connection's ESPHome-proxy GATT inventory.
            if candidate.declaration.handle != 0x0063:
                raise ValueError(
                    "FFA5 declaration handle differs from Android capture: "
                    f"0x{candidate.declaration.handle:04X} != 0x0063"
                )
            if parsed.value_handle != candidate.value_attribute.handle:
                raise ValueError(
                    "declaration value handle does not match discovered FFA5 "
                    f"attribute ({parsed.value_handle:#06x} != "
                    f"{candidate.value_attribute.handle:#06x})"
                )
            if parsed.value_handle != 0x0064:
                raise ValueError(
                    "FFA5 value handle differs from Android capture: "
                    f"0x{parsed.value_handle:04X} != 0x0064"
                )
            if not {"read", "notify"}.issubset(parsed.properties):
                raise ValueError(
                    "FFA5 declaration must advertise read and notify; "
                    f"properties={parsed.properties}"
                )
            if candidate.cccd is None or candidate.cccd.handle != 0x0065:
                raise ValueError(
                    "FFA5 CCCD must be discovered at handle 0x0065; "
                    f"found={getattr(candidate.cccd, 'handle', None)}"
                )

            characteristic = BleakGATTCharacteristic(
                obj=getattr(candidate.value_attribute, "obj", None),
                handle=parsed.value_handle,
                uuid=parsed.uuid,
                properties=list(parsed.properties),
                max_write_without_response_size=20,
                service=candidate.service,
            )
            if candidate.cccd is not None:
                characteristic.add_descriptor(
                    BleakGATTDescriptor(
                        obj=getattr(candidate.cccd, "obj", None),
                        handle=candidate.cccd.handle,
                        uuid=str(candidate.cccd.uuid),
                        characteristic=characteristic,
                    )
                )
            self._recovered_characteristics[target] = characteristic

            _LOGGER.warning(
                "Hunter GATT recovered misclassified characteristic uuid=%s "
                "declaration_handle=%s value_handle=%s properties=%s cccd_handle=%s "
                "parent_characteristic=%s parent_handle=%s; "
                "live value read is still required before FF81",
                target,
                candidate.declaration.handle,
                characteristic.handle,
                parsed.properties,
                getattr(candidate.cccd, "handle", None),
                candidate.parent_characteristic.uuid,
                candidate.parent_characteristic.handle,
            )
            return True
        except Exception as err:
            _LOGGER.warning(
                "Hunter GATT declaration reconstruction failed for %s "
                "(declaration_handle=%s value_attribute_handle=%s): %s",
                target,
                getattr(candidate.declaration, "handle", None),
                getattr(candidate.value_attribute, "handle", None),
                err,
                exc_info=True,
            )
            return False

    def _log_gatt_inventory(self) -> None:
        """Log GATT inventory and the Android FFA5 declaration/value/CCCD area."""
        inventory = self.gatt_inventory
        writable = self.writable_characteristics
        ffa5 = next(
            (item for item in inventory if item["uuid"] == CLIENT_ID_UUID),
            None,
        )
        ff83 = next(
            (item for item in inventory if item["uuid"] == COMMAND_UUID),
            None,
        )
        _LOGGER.info(
            "Hunter GATT discovery complete: services=%d characteristics=%d "
            "writable=%d FF83=%s FFA5=%s",
            len(self.service_uuids),
            len(inventory),
            len(writable),
            "present" if ff83 else "missing",
            "present" if ffa5 else "missing",
        )
        for item in inventory:
            _LOGGER.debug(
                "Hunter GATT characteristic service=%s uuid=%s handle=%s "
                "properties=%s descriptors=%s",
                item["service_uuid"],
                item["uuid"],
                item["handle"],
                item["properties"],
                item.get("descriptors", []),
            )

        handle_window = [
            item for item in inventory
            if isinstance(item.get("handle"), int)
            and 0x0060 <= item["handle"] <= 0x0068
        ]
        descriptor_window = [
            {
                "characteristic_uuid": item["uuid"],
                **descriptor,
            }
            for item in inventory
            for descriptor in item.get("descriptors", [])
            if isinstance(descriptor.get("handle"), int)
            and 0x0060 <= descriptor["handle"] <= 0x0068
        ]
        _LOGGER.info(
            "Hunter GATT FFA5 handle-window 0x0060-0x0068: "
            "characteristics=%s descriptors=%s",
            handle_window,
            descriptor_window,
        )
        if ffa5 is None:
            if SECOND_SERVICE_UUID in self.service_uuids:
                _LOGGER.warning(
                    "Hunter GATT discovery omitted FFA5. Android 6.1.49 exposes "
                    "declaration=0x0063, value=0x0064, CCCD=0x0065; "
                    "neighboring HA characteristics=%s",
                    handle_window,
                )
        else:
            value_handle = ffa5.get("handle")
            descriptors = ffa5.get("descriptors", [])
            cccd = next(
                (
                    descriptor for descriptor in descriptors
                    if descriptor.get("uuid") == "00002902-0000-1000-8000-00805f9b34fb"
                ),
                None,
            )
            _LOGGER.info(
                "Hunter FFA5 discovery details: declaration_handle=%s "
                "value_handle=%s properties=%s cccd=%s",
                value_handle - 1 if isinstance(value_handle, int) else None,
                value_handle,
                ffa5.get("properties"),
                cccd,
            )
            if value_handle != 0x0064 or cccd is None or cccd.get("handle") != 0x0065:
                _LOGGER.warning(
                    "Hunter FFA5 GATT layout differs from Android 6.1.49 "
                    "capture: expected declaration/value/CCCD=0x0063/0x0064/0x0065"
                )

        for item in writable:
            _LOGGER.info(
                "Hunter GATT writable characteristic uuid=%s handle=%s properties=%s",
                item["uuid"],
                item["handle"],
                item["properties"],
            )

    async def disconnect(self) -> None:
        async with self._lock:
            if self._client is None:
                self._notification_status = {}
                return
            try:
                if self._client.is_connected:
                    await self._client.disconnect()
            finally:
                self._client = None
                self._notification_status = {}
                self._recovered_characteristics = {}

    async def reconnect(self) -> None:
        await self.disconnect()
        await self.connect()

    async def read(self, uuid: str) -> bytes:
        await self._ensure_connected()
        async with self._lock:
            assert self._client is not None
            try:
                characteristic = self.characteristic_object(uuid)
                if characteristic is None:
                    raise BleakError(f"Characteristic {uuid} was not discovered")
                return bytes(await self._client.read_gatt_char(characteristic))
            except Exception as err:
                raise BleakError(f"Read failed for {uuid}: {err}") from err

    async def write(
        self,
        uuid: str,
        payload: bytes,
        *,
        response: bool | None = None,
    ) -> None:
        """Write only when the connected GATT database permits it."""
        await self._ensure_connected()
        async with self._lock:
            assert self._client is not None
            target = str(uuid).strip().lower()
            properties = self.characteristic_properties(target)
            if not properties:
                raise BleakError(
                    f"Characteristic {uuid} was not discovered; write refused."
                )

            writable = {"write", "write-without-response"} & properties
            if not writable:
                raise BleakError(
                    f"Characteristic {uuid} is not writable; "
                    f"properties={sorted(properties)}"
                )

            if target == COMMAND_UUID and response is not None:
                if response and "write" not in properties:
                    raise BleakError(
                        f"FF83 does not support write-with-response; "
                        f"properties={sorted(properties)}"
                    )
                if not response and "write-without-response" not in properties:
                    raise BleakError(
                        f"FF83 does not support write-without-response; "
                        f"properties={sorted(properties)}"
                    )
                selected_response = response
            elif target == COMMAND_UUID:
                if "write-without-response" in properties:
                    selected_response = False
                elif "write" in properties:
                    selected_response = True
                else:
                    raise BleakError(
                        f"FF83 is not writable; properties={sorted(properties)}"
                    )
            elif response is None:
                selected_response = "write-without-response" not in properties
            else:
                if response and "write" not in properties:
                    raise BleakError(
                        f"{uuid} does not support write-with-response; "
                        f"properties={sorted(properties)}"
                    )
                if not response and "write-without-response" not in properties:
                    raise BleakError(
                        f"{uuid} does not support write-without-response; "
                        f"properties={sorted(properties)}"
                    )
                selected_response = response

            try:
                await self._client.write_gatt_char(
                    uuid,
                    payload,
                    response=selected_response,
                )
            except Exception as err:
                raise BleakError(f"Write failed for {uuid}: {err}") from err

    def register_notification_callback(self, callback) -> None:
        self._notification_callback = callback

    async def start_notify(self, uuid: str) -> None:
        if not self.connected:
            await self.connect()
        assert self._client is not None
        active_client = self._client
        expected_characteristic = self.characteristic_object(uuid)
        if expected_characteristic is None:
            raise BleakError(
                f"Characteristic {uuid} is absent from the active GATT database."
            )
        properties = {
            str(prop).strip().lower()
            for prop in expected_characteristic.properties
        }
        if not ({"notify", "indicate"} & properties):
            raise BleakError(
                f"Characteristic {uuid} does not support notifications or indications; "
                f"properties={sorted(properties)}"
            )
        if self._notification_callback is None:
            raise BleakError("No Hunter notification callback registered.")

        expected_uuid = str(expected_characteristic.uuid).strip().lower()
        expected_handle = getattr(expected_characteristic, "handle", None)
        expected_id = id(expected_characteristic)
        connection_id = id(active_client)

        _LOGGER.info(
            "Hunter notification handler attaching uuid=%s handle=%s "
            "characteristic_id=%s connection_id=%s properties=%s",
            expected_uuid,
            expected_handle,
            expected_id,
            connection_id,
            sorted(properties),
        )

        def _callback(characteristic, data) -> None:
            received_at = datetime.now(timezone.utc).isoformat(timespec="milliseconds")
            payload = bytes(data)
            received_uuid = str(characteristic.uuid).strip().lower()
            same_connection = self._client is active_client
            same_characteristic = characteristic is expected_characteristic

            if received_uuid == "0000ff82-0000-1000-8000-00805f9b34fb":
                _LOGGER.info(
                    "Hunter FF82 notification received at=%s uuid=%s handle=%s "
                    "payload_len=%d payload=%s callback_characteristic_id=%s "
                    "subscribed_characteristic_id=%s same_characteristic=%s "
                    "same_connection=%s connection_id=%s",
                    received_at,
                    received_uuid,
                    getattr(characteristic, "handle", None),
                    len(payload),
                    payload.hex(" "),
                    id(characteristic),
                    expected_id,
                    same_characteristic,
                    same_connection,
                    connection_id,
                )
            else:
                _LOGGER.debug(
                    "Hunter BLE notification received at=%s uuid=%s handle=%s "
                    "payload_len=%d connection_id=%s",
                    received_at,
                    received_uuid,
                    getattr(characteristic, "handle", None),
                    len(payload),
                    connection_id,
                )

            if not same_connection or not same_characteristic:
                _LOGGER.error(
                    "Ignoring notification from unexpected GATT object: uuid=%s "
                    "same_characteristic=%s same_connection=%s expected_handle=%s "
                    "received_handle=%s",
                    received_uuid,
                    same_characteristic,
                    same_connection,
                    expected_handle,
                    getattr(characteristic, "handle", None),
                )
                return

            result = self._notification_callback(received_uuid, payload)
            if inspect.isawaitable(result):
                asyncio.create_task(result)

        # The ESPHome Bleak backend receives this exact characteristic object.
        # On REMOTE_CACHING proxies it obtains the CCCD from this object's
        # descriptor list and writes that descriptor handle itself. Keep the
        # recovered CCCD attached to this object; do not synthesize a write to
        # the characteristic value handle.
        cccd_descriptor = next(
            (
                descriptor
                for descriptor in (
                    getattr(expected_characteristic, "descriptors", ()) or ()
                )
                if str(descriptor.uuid).strip().lower()
                == "00002902-0000-1000-8000-00805f9b34fb"
            ),
            None,
        )
        backend = getattr(active_client, "_backend", None)
        backend_name = type(backend or active_client).__qualname__
        backend_feature_flags = getattr(backend, "_feature_flags", None)
        backend_services = getattr(active_client, "services", None)
        backend_characteristics = [
            characteristic
            for service in (backend_services or ())
            for characteristic in (getattr(service, "characteristics", ()) or ())
        ]
        backend_service_match = any(
            getattr(characteristic, "handle", None) == expected_handle
            and str(getattr(characteristic, "uuid", "")).strip().lower()
            == expected_uuid
            for characteristic in backend_characteristics
        )
        backend_descriptors = [
            (descriptor, characteristic)
            for service in (backend_services or ())
            for characteristic in (getattr(service, "characteristics", ()) or ())
            for descriptor in (getattr(characteristic, "descriptors", ()) or ())
        ]
        backend_descriptor_100 = next(
            (
                f"{descriptor.uuid}@{owner.uuid}@{owner.handle}"
                for descriptor, owner in backend_descriptors
                if getattr(descriptor, "handle", None) == 0x0064
            ),
            None,
        )
        backend_descriptor_101 = next(
            (
                f"{descriptor.uuid}@{owner.uuid}@{owner.handle}"
                for descriptor, owner in backend_descriptors
                if getattr(descriptor, "handle", None) == 0x0065
            ),
            None,
        )
        backend_characteristic_100 = next(
            (
                f"{item.uuid}@{item.handle}"
                for item in backend_characteristics
                if getattr(item, "handle", None) == 0x0064
            ),
            None,
        )
        proxy_device_info = getattr(backend, "_device_info", None)
        proxy_esphome_version = getattr(proxy_device_info, "esphome_version", None)

        if expected_uuid == CLIENT_ID_UUID:
            _LOGGER.info(
                "Hunter FFA5 notify path: characteristic_handle=%s "
                "cccd_handle=%s recovered_service_uuid=%s backend=%s "
                "backend_feature_flags=%s proxy_esphome_version=%s "
                "backend_service_match=%s backend_characteristic_count=%s "
                "backend_characteristic_100=%s backend_descriptor_100=%s "
                "backend_descriptor_101=%s",
                expected_handle,
                getattr(cccd_descriptor, "handle", None),
                getattr(expected_characteristic, "service_uuid", None),
                backend_name,
                backend_feature_flags,
                proxy_esphome_version,
                backend_service_match,
                len(backend_characteristics),
                backend_characteristic_100,
                backend_descriptor_100,
                backend_descriptor_101,
            )

        try:
            # Bleak resolves this object and passes it to ESPHomeClient.start_notify.
            # When REMOTE_CACHING is advertised, that backend writes CCCD 0x2902
            # using cccd_descriptor.handle (expected 0x0065 for FFA5).
            await active_client.start_notify(expected_characteristic, _callback)
        except Exception:
            if expected_uuid == CLIENT_ID_UUID:
                _LOGGER.warning(
                    "Hunter FFA5 notify activation failed: characteristic_handle=%s "
                    "cccd_handle=%s backend=%s backend_feature_flags=%s "
                    "proxy_esphome_version=%s backend_service_match=%s "
                    "backend_characteristic_count=%s backend_characteristic_100=%s "
                    "backend_descriptor_100=%s backend_descriptor_101=%s",
                    expected_handle,
                    getattr(cccd_descriptor, "handle", None),
                    backend_name,
                    backend_feature_flags,
                    proxy_esphome_version,
                    backend_service_match,
                    len(backend_characteristics),
                    backend_characteristic_100,
                    backend_descriptor_100,
                    backend_descriptor_101,
                    exc_info=True,
                )
            raise

    async def stop_notify(self, uuid: str) -> None:
        if not self.connected:
            return
        assert self._client is not None
        try:
            characteristic = self.characteristic_object(uuid)
            await self._client.stop_notify(characteristic or uuid)
        except Exception:
            _LOGGER.debug("Unable to unsubscribe %s", uuid, exc_info=True)

    async def subscribe(
        self,
        callback=None,
        *,
        notification_uuids: tuple[str, ...] | None = None,
    ) -> dict[str, str]:
        """Subscribe to notifications independently, preserving Android order.

        Second-generation initialization supplies the nine captured CCCD
        characteristics explicitly. Other callers retain the legacy core
        notification set. Battery Level remains an optional extra subscription.
        """
        if callback is not None:
            self._notification_callback = callback
        if not self.connected:
            await self.connect()

        self._notification_status = {}
        include_legacy_battery_notify = notification_uuids is None
        if notification_uuids is None:
            notification_uuids = (
                NOTIFY_UUID,
                COUNTDOWN_UUID,
                STATUS_NOTIFY_UUID,
            )
        # Android 6.1.49 enables exactly the nine proprietary CCCDs. It reads
        # Battery Level (2A19) separately and does not enable its CCCD.
        subscription_order = (
            (*notification_uuids, BATTERY_LEVEL_UUID)
            if include_legacy_battery_notify
            else tuple(notification_uuids)
        )
        for uuid in subscription_order:
            properties = self.characteristic_properties(uuid)
            if not properties:
                self._notification_status[uuid] = "missing"
                continue
            if not ({"notify", "indicate"} & properties):
                self._notification_status[uuid] = (
                    f"unsupported properties={','.join(sorted(properties))}"
                )
                continue
            handle = self.characteristic_handle(uuid)
            try:
                await self.start_notify(uuid)
                self._notification_status[uuid] = "subscribed"
                _LOGGER.info(
                    "Hunter notification subscription successful uuid=%s handle=%s properties=%s",
                    uuid,
                    handle,
                    sorted(properties),
                )
            except Exception as err:
                self._notification_status[uuid] = f"failed: {err}"
                _LOGGER.warning(
                    "Hunter notification subscription failed uuid=%s handle=%s properties=%s: %s",
                    uuid,
                    handle,
                    sorted(properties),
                    err,
                )
        for uuid, status in self._notification_status.items():
            if status != "subscribed" and not status.startswith("failed:"):
                _LOGGER.info(
                    "Hunter notification subscription unavailable uuid=%s status=%s",
                    uuid,
                    status,
                )
        return self.notification_status

    async def unsubscribe(self) -> None:
        if not self.connected:
            return
        for uuid, status in tuple(self._notification_status.items()):
            if status == "subscribed":
                await self.stop_notify(uuid)
        self._notification_status = {}

    async def authenticate(self, passcode: bytes) -> None:
        await self.write(PASSCODE_UUID, passcode, response=True)

    async def read_rssi(self) -> int | None:
        if self._client is None:
            return None
        return getattr(self._client, "rssi", None)

    async def _ensure_connected(self) -> None:
        if not self.connected:
            await self.connect()
