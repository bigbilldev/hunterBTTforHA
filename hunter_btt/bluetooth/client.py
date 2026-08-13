class HunterBLEClient:

    async def connect()
"""
Low-level BLE client for the Hunter BTT201.

Responsible only for BLE I/O.

No Home Assistant entities or coordinator logic belongs here.
"""

from __future__ import annotations

import asyncio
import logging

from bleak.exc import BleakError

from homeassistant.components import bluetooth
from homeassistant.components.bluetooth import (
    BluetoothServiceInfoBleak,
)
from homeassistant.components.bluetooth.match import (
    BleakClientWithServiceCache,
)
from homeassistant.core import HomeAssistant

from ..protocol.uuids import (
    COMMAND_UUID,
    COUNTDOWN_UUID,
    NOTIFY_UUID,
    PASSCODE_UUID,
    STATUS_NOTIFY_UUID,
)

_LOGGER = logging.getLogger(__name__)


class HunterBLEClient:
    """Low level BLE client."""

    def __init__(
        self,
        hass: HomeAssistant,
        discovery_info: BluetoothServiceInfoBleak,
    ) -> None:
        self._hass = hass
        self._address = discovery_info.address

        self._client: BleakClientWithServiceCache | None = None

        self._lock = asyncio.Lock()

    @property
    def connected(self) -> bool:
        return (
            self._client is not None
            and self._client.is_connected
        )

    async def connect(self) -> None:
        """Connect to controller."""

        if self.connected:
            return

        device = bluetooth.async_ble_device_from_address(
            self._hass,
            self._address,
            connectable=True,
        )

        if device is None:
            raise BleakError(
                f"Unable to locate BLE device {self._address}"
            )

        self._client = BleakClientWithServiceCache(
            device,
        )

        await self._client.connect()

        _LOGGER.debug("Connected to %s", self._address)

    async def disconnect(self) -> None:
        if self._client is None:
            return

        try:
            await self._client.disconnect()
        finally:
            self._client = None

    async def read(self, uuid: str) -> bytes:
        async with self._lock:
            await self.connect()
            assert self._client is not None

            return await self._client.read_gatt_char(uuid)

    async def write(
        self,
        uuid: str,
        payload: bytes,
        response: bool = True,
    ) -> None:

        async with self._lock:
            await self.connect()
            assert self._client is not None

            _LOGGER.debug(
                "WRITE %s : %s",
                uuid,
                payload.hex(),
            )

            await self._client.write_gatt_char(
                uuid,
                payload,
                response=response,
            )

    async def subscribe(
        self,
        callback,
    ) -> None:
        """Subscribe to all Hunter notifications."""

        assert self._client is not None

        await self._client.start_notify(
            NOTIFY_UUID,
            callback,
        )

        await self._client.start_notify(
            COUNTDOWN_UUID,
            callback,
        )

        await self._client.start_notify(
            STATUS_NOTIFY_UUID,
            callback,
        )

    async def unsubscribe(self) -> None:
        if not self.connected:
            return

        assert self._client is not None

        for uuid in (
            NOTIFY_UUID,
            COUNTDOWN_UUID,
            STATUS_NOTIFY_UUID,
        ):
            try:
                await self._client.stop_notify(uuid)
            except Exception:
                pass

    async def authenticate(
        self,
        passcode: bytes,
    ) -> None:
        """
        Write passcode to FF81.

        Older Hunter firmware expects this immediately after
        connection.
        """

        await self.write(
            PASSCODE_UUID,
            passcode,
        )
    async def disconnect()

    async def read()

    async def write()

    async def start_notifications()

    async def stop_notifications()