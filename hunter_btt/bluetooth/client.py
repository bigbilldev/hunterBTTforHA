"""Low-level Hunter BLE client.

Connection and GATT enumeration follow the Android flow: connect to the
Bluetooth device, wait for GATT service discovery, then inspect services and
characteristics before selecting a protocol.
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
    """Low-level BLE I/O and discovered GATT inventory."""

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
    def characteristic_uuids(self) -> set[str]:
        if self._client is None:
            return set()
        return {
            str(characteristic.uuid).strip().lower()
            for service in self._client.services
            for characteristic in service.characteristics
        }

    def characteristic_properties(self, uuid: str) -> set[str]:
        """Return properties reported by the connected GATT database."""
        target = str(uuid).strip().lower()
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

    async def connect(self) -> None:
        """Connect and let Bleak perform GATT service discovery."""
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
                    name=f"Hunter BTT - {self._address}",
                )
            except Exception:
                self._client = None
                raise

            # Bleak's connected client exposes the GATT database only after
            # service discovery. Log the exact inventory used for generation.
            _LOGGER.debug(
                "Hunter GATT discovered address=%s services=%s characteristics=%s",
                self._address,
                sorted(self.service_uuids),
                sorted(self.characteristic_uuids),
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

            if target == COMMAND_UUID:
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

            _LOGGER.debug(
                "Hunter BLE write uuid=%s response=%s properties=%s payload=%s",
                uuid,
                selected_response,
                sorted(properties),
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

    def register_notification_callback(self, callback) -> None:
        self._notification_callback = callback

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
            _LOGGER.debug("Unable to unsubscribe %s", uuid, exc_info=True)

    async def subscribe(self, callback=None) -> None:
        if callback is not None:
            self._notification_callback = callback
        if not self.connected:
            await self.connect()
        for uuid in (NOTIFY_UUID, COUNTDOWN_UUID, STATUS_NOTIFY_UUID):
            if uuid in self.characteristic_uuids:
                await self.start_notify(uuid)

    async def unsubscribe(self) -> None:
        if not self.connected:
            return
        for uuid in (NOTIFY_UUID, COUNTDOWN_UUID, STATUS_NOTIFY_UUID):
            if uuid in self.characteristic_uuids:
                await self.stop_notify(uuid)

    async def authenticate(self, passcode: bytes) -> None:
        await self.write(PASSCODE_UUID, passcode, response=True)

    async def read_rssi(self) -> int | None:
        if self._client is None:
            return None
        return getattr(self._client, "rssi", None)

    async def _ensure_connected(self) -> None:
        if not self.connected:
            await self.connect()
