"""Connection layer between the manager and HunterBLEClient."""

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
        """Return whether the BLE client is connected."""
        return self.client.connected

    @property
    def service_uuids(self) -> set[str]:
        """Return discovered service UUIDs."""
        return self.client.service_uuids

    @property
    def characteristic_uuids(self) -> set[str]:
        """Return discovered characteristic UUIDs."""
        return self.client.characteristic_uuids

    def register_notification_callback(
        self,
        callback: Callable[[str, bytes], object],
    ) -> None:
        """Register the notification callback."""
        self._notification_callback = callback
        self.client.register_notification_callback(callback)

    async def connect(self) -> None:
        """Connect to the controller."""
        await self.client.connect()

    async def disconnect(self) -> None:
        """Disconnect from the controller."""
        await self.client.disconnect()

    async def reconnect(self) -> None:
        """Disconnect and establish a fresh BLE connection."""
        _LOGGER.debug("Reconnecting Hunter controller")
        await self.disconnect()
        await self.connect()

    async def ensure_connection(self) -> None:
        """Ensure the BLE client is connected."""
        if not self.connected:
            await self.connect()

    async def read(self, uuid: str) -> bytes:
        """Read a characteristic."""
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
        """Write a characteristic."""
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
        """Subscribe to a notification characteristic."""
        try:
            await self.client.start_notify(uuid)
        except Exception as err:
            raise HunterConnectionError(
                f"Unable to subscribe to {uuid}: {err}"
            ) from err

    async def stop_notify(self, uuid: str) -> None:
        """Stop notifications."""
        try:
            await self.client.stop_notify(uuid)
        except Exception:
            _LOGGER.debug(
                "Unable to unsubscribe %s",
                uuid,
                exc_info=True,
            )

    async def read_rssi(self) -> int | None:
        """Read the current RSSI when supported."""
        return await self.client.read_rssi()
