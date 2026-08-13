"""Connection layer between the manager and HunterBLEClient.

This module intentionally does not own a second BleakClient. The project
architecture is:

    HunterBLEManager
        -> HunterConnection
            -> HunterBLEClient
                -> BleakClientWithServiceCache
"""

from __future__ import annotations

import logging
from collections.abc import Callable

from homeassistant.core import HomeAssistant

from .client import HunterBLEClient

_LOGGER = logging.getLogger(__name__)


class HunterConnectionError(Exception):
    """Raised when the Hunter connection layer cannot communicate."""


class HunterConnection:
    """Serialize and expose BLE operations through HunterBLEClient."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: HunterBLEClient,
    ) -> None:
        self._hass = hass
        self.client = client
        self._notification_callback = None

    @property
    def connected(self) -> bool:
        return self.client.connected

    @property
    def service_uuids(self) -> set[str]:
        return self.client.service_uuids

    @property
    def characteristic_uuids(self) -> set[str]:
        return self.client.characteristic_uuids

    def register_notification_callback(
        self,
        callback: Callable[[str, bytes], object],
    ) -> None:
        self._notification_callback = callback
        self.client.register_notification_callback(callback)

    async def connect(self) -> None:
        await self.client.connect()

    async def disconnect(self) -> None:
        await self.client.disconnect()

    async def ensure_connection(self) -> None:
        await self.client.connect()

    async def read(self, uuid: str) -> bytes:
        try:
            return await self.client.read(uuid)
        except Exception as err:
            raise HunterConnectionError(
                f"Read failed for {uuid}: {err}"
            ) from err

    async def write(
        self,
        uuid: str,
        payload: bytes,
        *,
        response: bool = True,
    ) -> None:
        try:
            await self.client.write(
                uuid,
                payload,
                response=response,
            )
        except Exception as err:
            raise HunterConnectionError(
                f"Write failed for {uuid}: {err}"
            ) from err

    async def start_notify(self, uuid: str) -> None:
        try:
            await self.client.start_notify(uuid)
        except Exception as err:
            raise HunterConnectionError(
                f"Unable to subscribe to {uuid}: {err}"
            ) from err

    async def stop_notify(self, uuid: str) -> None:
        try:
            await self.client.stop_notify(uuid)
        except Exception as err:
            _LOGGER.debug(
                "Unable to unsubscribe %s: %s",
                uuid,
                err,
            )

    async def read_rssi(self) -> int | None:
        return await self.client.read_rssi()
