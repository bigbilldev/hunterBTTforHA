"""
Connection manager for Hunter BLE.

Handles:

    reconnect
    retry
    notification registration

Higher-level protocol operations belong in manager.py.
"""

from __future__ import annotations

import asyncio
import logging

from bleak.exc import BleakError

from homeassistant.core import HomeAssistant

from .client import HunterBLEClient

_LOGGER = logging.getLogger(__name__)


class HunterConnection:
    """Persistent BLE connection."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: HunterBLEClient,
    ) -> None:

        self._hass = hass
        self.client = client

        self._connected = False

        self._callbacks: list = []

    @property
    def connected(self) -> bool:
        return self._connected

    def register_notification_callback(
        self,
        callback,
    ) -> None:
        self._callbacks.append(callback)

    async def connect(self) -> None:
        if self._connected:
            return

        await self.client.connect()

        await self.client.subscribe(
            self._notification_received,
        )

        self._connected = True

        _LOGGER.info("Hunter connected")

    async def disconnect(self) -> None:
        if not self._connected:
            return

        try:
            await self.client.unsubscribe()
        finally:
            await self.client.disconnect()

        self._connected = False

    async def ensure_connection(self) -> None:
        if self._connected:
            return

        await self.connect()

    async def reconnect(self) -> None:
        _LOGGER.debug("Reconnecting Hunter")

        try:
            await self.disconnect()
        except Exception:
            pass

        await asyncio.sleep(1)

        await self.connect()

    async def execute(
        self,
        coro,
    ):
        """
        Execute a BLE operation.

        Automatically reconnects once if connection
        dropped.
        """

        await self.ensure_connection()

        try:
            return await coro()

        except BleakError:

            _LOGGER.warning(
                "BLE operation failed, reconnecting..."
            )

            await self.reconnect()

            return await coro()

    async def _notification_received(
        self,
        characteristic,
        payload: bytearray,
    ) -> None:
        uuid = str(characteristic.uuid)

        data = bytes(payload)

        _LOGGER.debug(
            "NOTIFY %s : %s",
            uuid,
            data.hex(),
        )

        for callback in self._callbacks:
            try:
                await callback(
                    uuid,
                    data,
                )
            except Exception:
                _LOGGER.exception(
                    "Notification callback failed"
                )