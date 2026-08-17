"""High-level Hunter BTT BLE manager."""

from __future__ import annotations

import asyncio
import inspect
import logging
from datetime import datetime
from typing import Any

from homeassistant.components.bluetooth import BluetoothServiceInfoBleak
from homeassistant.core import HomeAssistant

from ..protocol.generation import (
    HunterCapabilities,
    HunterGeneration,
    detect_generation,
    detect_zone_count,
)
from .client import HunterBLEClient
from .connection import HunterConnection
from .transaction import HunterTransactionEngine

_LOGGER = logging.getLogger(__name__)

FF80_SERVICE_UUID = "0000ff80-0000-1000-8000-00805f9b34fb"
FF83_UUID = "0000ff83-0000-1000-8000-00805f9b34fb"


class HunterManagerError(Exception):
    """Raised for Hunter manager errors."""


class HunterBLEManager:
    """Manage the Hunter controller connection and protocol selection."""

    def __init__(
        self,
        hass: HomeAssistant,
        discovery_info: BluetoothServiceInfoBleak,
    ) -> None:
        self._hass = hass
        self.address = discovery_info.address
        self.name = discovery_info.name or ""

        self.client = HunterBLEClient(hass, discovery_info)
        self.connection = HunterConnection(hass, self.client)
        self.transaction = HunterTransactionEngine(self.connection)

        self._generation = HunterGeneration.UNKNOWN
        self._capabilities = HunterCapabilities(
            generation=HunterGeneration.UNKNOWN,
            zone_count=0,
        )
        self.connected = False
        self._state_callback = None
        self.state: dict[str, Any] = {
            "battery": None,
            "running": False,
            "active_zone": 0,
            "remaining_seconds": 0,
            "zones": {1: {}, 2: {}},
        }

    @property
    def generation(self) -> HunterGeneration:
        """Return the detected generation."""
        return self._generation

    @property
    def capabilities(self) -> HunterCapabilities:
        """Return controller capabilities."""
        return self._capabilities

    @property
    def available(self) -> bool:
        """Return whether the controller is connected."""
        return self.connected

    def register_callback(self, callback) -> None:
        """Register a state callback."""
        self._state_callback = callback

    async def _notify_state_changed(self) -> None:
        if self._state_callback is None:
            return
        result = self._state_callback()
        if inspect.isawaitable(result):
            await result

    async def connect(self) -> None:
        """Connect and determine the controller generation."""
        if self.connected:
            return

        try:
            await self.connection.connect()

            services = set(self.connection.service_uuids)
            characteristics = set(self.connection.characteristic_uuids)

            self._generation = detect_generation(
                services,
                characteristics,
                device_name=self.name,
            )

            _LOGGER.warning(
                "PROTOCOL DEBUG: name=%s services=%s "
                "characteristics=%s generation=%s",
                self.name,
                sorted(services),
                sorted(characteristics),
                self._generation,
            )

            if self._generation is HunterGeneration.UNKNOWN:
                await self.connection.disconnect()
                raise HunterManagerError(
                    "Unable to identify Hunter BLE protocol generation."
                )

            zone_count = detect_zone_count(
                characteristics,
                self._generation,
            )

            self._capabilities = HunterCapabilities(
                generation=self._generation,
                zone_count=zone_count,
                service_uuid=(
                    FF80_SERVICE_UUID
                    if FF80_SERVICE_UUID in services
                    else None
                ),
            )

            self.connected = True

            _LOGGER.info(
                "Connected to Hunter %s: generation=%s zones=%d",
                self.address,
                self._generation.value,
                zone_count,
            )

        except HunterManagerError:
            self.connected = False
            raise
        except Exception as err:
            self.connected = False
            try:
                await self.connection.disconnect()
            except Exception:
                pass
            raise HunterManagerError(
                f"Unable to connect to Hunter controller: {err}"
            ) from err

    async def disconnect(self) -> None:
        """Disconnect from the controller."""
        await self.connection.disconnect()
        self.connected = False
        await self._notify_state_changed()

    async def ensure_connected(self) -> None:
        """Ensure the controller is connected."""
        if not self.connected or not self.connection.connected:
            await self.connect()

    async def reconnect(self) -> None:
        """Reconnect the controller."""
        await self.connection.reconnect()
        self.connected = True

    async def start_zone(self, zone: int, runtime: int) -> None:
        """Start a watering zone using the selected protocol."""
        await self.ensure_connected()

        if runtime <= 0:
            raise HunterManagerError(
                "Runtime must be greater than zero."
            )

        if zone < 1 or zone > self._capabilities.zone_count:
            raise HunterManagerError(
                f"Zone {zone} is not supported."
            )

        _LOGGER.warning(
            "PROTOCOL DEBUG START: generation=%s connected=%s "
            "zone=%s runtime=%s",
            self._generation,
            self.connected,
            zone,
            runtime,
        )

        if self._generation is HunterGeneration.FIRST:
            raise HunterManagerError(
                "BTT100 first-generation protocol selected. "
                "FF83 transaction path is disabled; the "
                "first-generation FFAx command mapping is not "
                "yet connected to start_zone()."
            )

        _LOGGER.warning(
            "PROTOCOL DEBUG: ENTERING FF83 TRANSACTION PATH"
        )
        await self.transaction.start_zone(zone, runtime)

    async def stop(self) -> None:
        """Stop watering using the selected protocol."""
        await self.ensure_connected()

        if self._generation is HunterGeneration.FIRST:
            raise HunterManagerError(
                "BTT100 first-generation protocol selected. "
                "FF83 transaction path is disabled; the "
                "first-generation FFAx stop mapping is not "
                "yet connected to stop()."
            )

        await self.transaction.stop()

    async def refresh(self) -> dict[str, Any]:
        """Refresh cached state."""
        await self.ensure_connected()
        return self.state

    async def shutdown(self) -> None:
        """Shut down the manager."""
        await self.disconnect()
