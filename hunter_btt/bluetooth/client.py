"""Hunter BTT BLE client.

FF83 is a command characteristic.  For this integration it must NEVER be
sent as an acknowledged/write-with-response operation.  When FF83 is used,
this client explicitly sends response=False.

All other characteristics are capability-checked before writing.
"""

from __future__ import annotations

import asyncio
import inspect
import logging

from bleak.exc import BleakError
from bleak_retry_connector import BleakClientWithServiceCache, establish_connection
from homeassistant.components import bluetooth
from homeassistant.components.bluetooth import BluetoothServiceInfoBleak
from homeassistant.core import HomeAssistant

from ..protocol.uuids import (
    COUNTDOWN_UUID,
    NOTIFY_UUID,
    PASSCODE_UUID,
    STATUS_NOTIFY_UUID,
)

_LOGGER = logging.getLogger(__name__)

COMMAND_UUID = "0000ff83-0000-1000-8000-00805f9b34fb"


class HunterBLEClient:
    """Low-level BLE client with explicit FF83 write-mode handling."""

    def __init__(
        self,
        hass: HomeAssistant,
        discovery_info: BluetoothServiceInfoBleak,
    ) -> None:
        self._hass = hass
        self._address = discovery_info.address
        self._client: BleakClientWithServiceCache | None = None
        self._lock = asyncio.Lock()
        self._notification_callback = None

    @property
    def connected(self) -> bool:
        return bool(self._client is not None and self._client.is_connected)

    @property
    def service_uuids(self) -> set[str]:
        if self._client is None:
            return set()
        return {str(s.uuid).lower() for s in self._client.services}

    @property
    def characteristic_uuids(self) -> set[str]:
        if self._client is None:
            return set()
        return {
            str(c.uuid).lower()
            for s in self._client.services
            for c in s.characteristics
        }

    def characteristic_properties(self, uuid: str) -> set[str]:
        """Return the properties reported by the discovered characteristic."""
        if self._client is None:
            return set()

        target = str(uuid).strip().lower()
        for service in self._client.services:
            for characteristic in service.characteristics:
                if str(characteristic.uuid).strip().lower() == target:
                    return {
                        str(prop).strip().lower()
                        for prop in characteristic.properties
                    }
        return set()

    def characteristic_is_writable(self, uuid: str) -> bool:
        properties = self.characteristic_properties(uuid)
        return bool({"write", "write-without-response"} & properties)

    @property
    def ff83_writable(self) -> bool:
        return self.characteristic_is_writable(COMMAND_UUID)

    @property
    def rssi(self) -> int | None:
        if self._client is None:
            return None
        return getattr(self._client, "rssi", None)

    def register_notification_callback(self, callback) -> None:
        self._notification_callback = callback

    async def connect(self) -> None:
        async with self._lock:
            if self.connected:
                return

            device = bluetooth.async_ble_device_from_address(
                self._hass,
                self._address,
                connectable=True,
            )
            if inspect.isawaitable(device):
                device = await device

            if device is None:
                raise BleakError(
                    f"Unable to locate BLE device {self._address}"
                )

            try:
                self._client = await establish_connection(
                    BleakClientWithServiceCache,
                    device,
                    name="Hunter BTT",
                )
            except Exception:
                self._client = None
                raise

            _LOGGER.debug(
                "Hunter BLE connected: address=%s FF83 properties=%s",
                self._address,
                sorted(self.characteristic_properties(COMMAND_UUID)),
            )

    async def disconnect(self) -> None:
        async with self._lock:
            if self._client is None:
                return
            try:
                if self._client.is_connected:
                    await self._client.disconnect()
            finally:
                self._client = None

    async def reconnect(self) -> None:
        await self.disconnect()
        await self.connect()

    async def read(self, uuid: str) -> bytes:
        await self._ensure_connected()

        async with self._lock:
            assert self._client is not None
            try:
                return bytes(await self._client.read_gatt_char(uuid))
            except Exception as err:
                raise BleakError(f"Read failed for {uuid}: {err}") from err

    async def write(
        self,
        uuid: str,
        payload: bytes,
        *,
        response: bool | None = None,
    ) -> None:
        """Write after verifying GATT capability.

        FF83 is deliberately hard-coded to response=False.  We do not infer
        its write mode from the advertised properties because the Hunter
        command path must use the write-without-response operation.
        """
        await self._ensure_connected()

        async with self._lock:
            assert self._client is not None

            target = str(uuid).strip().lower()
            properties = self.characteristic_properties(target)

            if not properties:
                raise BleakError(
                    f"Characteristic {uuid} was not discovered; "
                    "write refused."
                )

            _LOGGER.debug(
                "Hunter BLE write check: uuid=%s properties=%s",
                uuid,
                sorted(properties),
            )

            if target == COMMAND_UUID:
                # CRITICAL: FF83 is ALWAYS sent without a GATT response.
                if "write-without-response" not in properties:
                    raise BleakError(
                        "FF83 does not advertise write-without-response; "
                        f"refusing FF83 write. properties={sorted(properties)}"
                    )
                selected_response = False
            else:
                if not (
                    "write" in properties
                    or "write-without-response" in properties
                ):
                    raise BleakError(
                        f"Characteristic {uuid} is not writable; "
                        f"properties={sorted(properties)}"
                    )

                if response is None:
                    selected_response = (
                        "write-without-response" not in properties
                    )
                else:
                    selected_response = response

                if selected_response and "write" not in properties:
                    raise BleakError(
                        f"Characteristic {uuid} does not support "
                        f"write-with-response; properties={sorted(properties)}"
                    )

                if not selected_response and "write-without-response" not in properties:
                    raise BleakError(
                        f"Characteristic {uuid} does not support "
                        f"write-without-response; properties={sorted(properties)}"
                    )

            _LOGGER.debug(
                "Hunter BLE WRITE: uuid=%s response=%s payload=%s",
                uuid,
                selected_response,
                bytes(payload).hex(" "),
            )

            try:
                await self._client.write_gatt_char(
                    uuid,
                    payload,
                    response=selected_response,
                )
            except Exception as err:
                raise BleakError(f"Write failed for {uuid}: {err}") from err

    async def start_notify(self, uuid: str) -> None:
        if not self.connected:
            await self.connect()

        assert self._client is not None

        if self._notification_callback is None:
            raise BleakError("No Hunter notification callback registered.")

        def _callback(characteristic, data) -> None:
            result = self._notification_callback(
                str(characteristic.uuid),
                bytes(data),
            )
            if inspect.isawaitable(result):
                asyncio.create_task(result)

        await self._client.start_notify(uuid, _callback)

    async def stop_notify(self, uuid: str) -> None:
        if not self.connected:
            return

        assert self._client is not None
        try:
            await self._client.stop_notify(uuid)
        except Exception:
            pass

    async def subscribe(self, callback=None) -> None:
        if callback is not None:
            self._notification_callback = callback

        if not self.connected:
            await self.connect()

        for uuid in (NOTIFY_UUID, COUNTDOWN_UUID, STATUS_NOTIFY_UUID):
            await self.start_notify(uuid)

    async def unsubscribe(self) -> None:
        if not self.connected:
            return

        for uuid in (NOTIFY_UUID, COUNTDOWN_UUID, STATUS_NOTIFY_UUID):
            await self.stop_notify(uuid)

    async def authenticate(self, passcode: bytes) -> None:
        await self.write(PASSCODE_UUID, passcode, response=True)

    async def read_rssi(self) -> int | None:
        return self.rssi

    async def _ensure_connected(self) -> None:
        if not self.connected:
            await self.connect()
