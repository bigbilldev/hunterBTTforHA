"""Hunter BTT BLE client.

FF83 is a normal acknowledged GATT write in the Android implementation.
Do not require write-without-response for FF83.

The important distinction is:
- characteristic existence is required;
- for FF83, write-with-response is explicitly selected;
- a peripheral that reports only ``write`` is therefore still usable;
- we never probe FF83 by writing test data merely to determine writability.
"""

from __future__ import annotations

import logging
from typing import Awaitable, Callable

from bleak import BleakClient
from bleak.exc import BleakError

_LOGGER = logging.getLogger(__name__)

FF83_UUID = "0000ff83-0000-1000-8000-00805f9b34fb"


class HunterBLEClient:
    """Thin BLE client wrapper used by the Hunter integration."""

    def __init__(self, hass, discovery_info) -> None:
        self._hass = hass
        self._discovery_info = discovery_info
        self._client: BleakClient | None = None
        self._notification_uuids: set[str] = set()

    @property
    def connected(self) -> bool:
        return bool(self._client and self._client.is_connected)

    @property
    def services(self):
        if self._client is None:
            return None
        return self._client.services

    async def connect(self) -> None:
        if self.connected:
            return

        address = getattr(self._discovery_info, "address", self._discovery_info)

        # Keep this compatible with the existing HA/Bleak connection path.
        from bleak_retry_connector import establish_connection

        self._client = await establish_connection(
            BleakClient,
            address,
            getattr(self._discovery_info, "name", "Hunter BTT"),
            disconnected_callback=self._disconnected,
        )

    async def disconnect(self) -> None:
        if self._client is not None:
            try:
                await self._client.disconnect()
            finally:
                self._client = None
                self._notification_uuids.clear()

    def _disconnected(self, _client) -> None:
        _LOGGER.debug("Hunter BLE device disconnected")

    def _resolve_characteristic(self, uuid: str):
        if self._client is None or not self.connected:
            raise BleakError("Hunter BLE client is not connected")

        wanted = str(uuid).strip().lower()

        for service in self._client.services:
            for characteristic in service.characteristics:
                if str(characteristic.uuid).strip().lower() == wanted:
                    return characteristic

        raise BleakError(f"Characteristic {uuid} was not found")

    def characteristic_properties(self, uuid: str) -> set[str]:
        """Return normalized characteristic properties without performing I/O."""
        characteristic = self._resolve_characteristic(uuid)
        return {
            str(prop).strip().lower()
            for prop in getattr(characteristic, "properties", ())
        }

    def can_write(self, uuid: str) -> bool:
        """Determine whether a characteristic exposes any write capability.

        This is a metadata check only.  It never performs a write.
        """
        properties = self.characteristic_properties(uuid)
        return "write" in properties or "write-without-response" in properties

    def can_write_with_response(self, uuid: str) -> bool:
        """Return whether the characteristic advertises normal GATT write."""
        return "write" in self.characteristic_properties(uuid)

    def can_write_without_response(self, uuid: str) -> bool:
        return "write-without-response" in self.characteristic_properties(uuid)

    async def read(self, uuid: str) -> bytes:
        if not self.connected:
            await self.connect()

        characteristic = self._resolve_characteristic(uuid)
        properties = {
            str(prop).strip().lower()
            for prop in getattr(characteristic, "properties", ())
        }

        if "read" not in properties:
            raise BleakError(
                f"Read not permitted for {uuid}; properties={sorted(properties)}"
            )

        try:
            return bytes(
                await self._client.read_gatt_char(characteristic)
            )
        except Exception as err:
            raise BleakError(f"Read failed for {uuid}: {err}") from err

    async def write(
        self,
        uuid: str,
        payload: bytes,
        *,
        response: bool | None = None,
    ) -> None:
        """Write a characteristic using the Android-compatible mode.

        FF83 MUST use the normal acknowledged write path.  We deliberately
        do not fall back to write-without-response because that would change
        the Android protocol operation being reproduced.
        """
        if not self.connected:
            await self.connect()

        characteristic = self._resolve_characteristic(uuid)
        properties = {
            str(prop).strip().lower()
            for prop in getattr(characteristic, "properties", ())
        }
        normalized = str(uuid).strip().lower()

        if normalized == FF83_UUID:
            if "write" not in properties:
                raise BleakError(
                    "FF83 does not advertise normal write; "
                    f"properties={sorted(properties)}"
                )
            # Force the Android BluetoothGatt.writeCharacteristic() equivalent.
            use_response = True
        else:
            if response is True and "write" not in properties:
                raise BleakError(
                    f"{uuid} does not advertise acknowledged write; "
                    f"properties={sorted(properties)}"
                )
            if response is False and "write-without-response" not in properties:
                raise BleakError(
                    f"{uuid} does not advertise write-without-response; "
                    f"properties={sorted(properties)}"
                )
            if response is None:
                use_response = "write" in properties
            else:
                use_response = response

        try:
            await self._client.write_gatt_char(
                characteristic,
                bytes(payload),
                response=use_response,
            )
        except Exception as err:
            raise BleakError(f"Write failed for {uuid}: {err}") from err

    async def subscribe(
        self,
        callback: Callable[[str, bytes], Awaitable[None] | None],
    ) -> None:
        if not self.connected:
            await self.connect()

        if self._client is None:
            raise BleakError("Hunter BLE client is not connected")

        for service in self._client.services:
            for characteristic in service.characteristics:
                props = {
                    str(prop).strip().lower()
                    for prop in getattr(characteristic, "properties", ())
                }
                if "notify" not in props and "indicate" not in props:
                    continue

                uuid = str(characteristic.uuid).lower()

                def handler(_sender, data, characteristic_uuid=uuid):
                    result = callback(characteristic_uuid, bytes(data))
                    # Async callbacks are scheduled by HA's event loop.
                    if hasattr(result, "__await__"):
                        import asyncio
                        asyncio.create_task(result)

                await self._client.start_notify(characteristic, handler)
                self._notification_uuids.add(uuid)

    async def unsubscribe(self) -> None:
        if self._client is None:
            return

        for uuid in tuple(self._notification_uuids):
            try:
                characteristic = self._resolve_characteristic(uuid)
                await self._client.stop_notify(characteristic)
            except Exception:
                _LOGGER.debug(
                    "Unable to stop notification for %s",
                    uuid,
                    exc_info=True,
                )

        self._notification_uuids.clear()
