"""Hunter BTT BLE manager."""

from __future__ import annotations

import inspect
import logging
from typing import Any

from homeassistant.core import HomeAssistant

from ..models import HunterState
from ..protocol.uuids import BATTERY_LEVEL_UUID
from ..protocol.generation import (
    FCC0_SERVICE_UUID,
    SECOND_SERVICE_UUID,
    HunterCapabilities,
    HunterGeneration,
    detect_generation,
    detect_zone_count,
    normalize_android_device_name,
)
from .client import HunterBLEClient
from .connection import HunterConnection
from .transaction import HunterTransactionEngine

_LOGGER = logging.getLogger(__name__)


class HunterManagerError(Exception):
    """Raised for Hunter manager errors."""


class HunterBLEManager:
    """Manage BLE connection, GATT identification and transactions."""

    def __init__(
        self,
        hass: HomeAssistant,
        address: str,
        passcode: str = "0000",
    ) -> None:
        self._hass = hass
        self.address = address
        self.name = "Hunter BTT"
        self.passcode = passcode
        self.client = HunterBLEClient(hass, address)
        self.connection = HunterConnection(hass, self.client)
        self.transaction = HunterTransactionEngine(self.connection)

        self._generation = HunterGeneration.UNKNOWN
        self._capabilities = HunterCapabilities(
            generation=HunterGeneration.UNKNOWN,
            zone_count=0,
        )
        self.connected = False
        self._state_callback = None
        self._listeners: set[Any] = set()
        self.state = HunterState()

    @property
    def generation(self) -> HunterGeneration:
        return self._generation

    @property
    def capabilities(self) -> HunterCapabilities:
        return self._capabilities

    @property
    def available(self) -> bool:
        return self.connected

    def add_listener(self, callback):
        """Register a state listener and return an unsubscribe callback."""
        self._listeners.add(callback)

        def remove_listener() -> None:
            self._listeners.discard(callback)

        return remove_listener

    def register_callback(self, callback) -> None:
        """Compatibility alias for integrations using a single callback."""
        self._state_callback = callback

    async def _notify_state_changed(self) -> None:
        callbacks = set(self._listeners)
        if self._state_callback is not None:
            callbacks.add(self._state_callback)
        for callback in callbacks:
            try:
                result = callback(self.state)
                if inspect.isawaitable(result):
                    await result
            except Exception:
                _LOGGER.exception("Hunter state listener failed")

    async def connect(self) -> None:
        """Connect, enumerate GATT, then identify protocol and zones."""
        if self.connected and self.connection.connected:
            return

        try:
            await self.connection.connect()

            services = set(self.connection.service_uuids)
            characteristics = set(self.connection.characteristic_uuids)

            _LOGGER.debug(
                "Hunter post-connect GATT inventory address=%s services=%s chars=%s",
                self.address,
                sorted(services),
                sorted(characteristics),
            )

            self._generation = detect_generation(
                service_uuids=services,
                device_name=self.name,
                characteristic_uuids=characteristics,
            )
            if self._generation is HunterGeneration.UNKNOWN:
                raise HunterManagerError(
                    "Unable to identify Hunter protocol generation from "
                    "connected GATT services/characteristics."
                )

            zone_count = detect_zone_count(
                characteristics,
                self._generation,
            )
            if zone_count < 1:
                raise HunterManagerError(
                    f"No supported zones found for "
                    f"{self._generation.value} generation."
                )

            self._capabilities = HunterCapabilities(
                generation=self._generation,
                zone_count=zone_count,
                service_uuid=(
                    SECOND_SERVICE_UUID
                    if self._generation is HunterGeneration.SECOND
                    else FCC0_SERVICE_UUID
                ),
            )

            self.transaction.set_generation(self._generation)

            # Android initializes the characteristic map and notification
            # handlers after GATT service discovery. Mirror that ordering.
            try:
                await self.client.subscribe(self.transaction.notification)
            except Exception as err:
                _LOGGER.debug(
                    "Hunter notification subscription incomplete: %s",
                    err,
                )

            self.connected = True
            await self._notify_state_changed()

            _LOGGER.info(
                "Hunter connected: address=%s name=%r generation=%s zones=%d "
                "services=%s",
                self.address,
                normalize_android_device_name(self.name),
                self._generation.value,
                zone_count,
                sorted(services),
            )

        except HunterManagerError:
            self.connected = False
            try:
                await self.connection.disconnect()
            except Exception:
                pass
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
        try:
            await self.client.unsubscribe()
        except Exception:
            pass
        await self.connection.disconnect()
        self.connected = False
        self.transaction.set_generation(HunterGeneration.UNKNOWN)
        await self._notify_state_changed()

    async def ensure_connected(self) -> None:
        if not self.connected or not self.connection.connected:
            await self.connect()

    async def reconnect(self) -> None:
        await self.connection.reconnect()
        self.connected = False
        await self.connect()

    async def start_zone(self, zone: int, runtime: int) -> None:
        await self.ensure_connected()
        if runtime <= 0:
            raise HunterManagerError("Runtime must be greater than zero.")
        if zone < 1 or zone > self._capabilities.zone_count:
            raise HunterManagerError(f"Zone {zone} is not supported.")
        await self.transaction.start_zone(zone, runtime)
        self.state["running"] = True
        self.state["active_zone"] = zone
        self.state["remaining_seconds"] = runtime
        await self._notify_state_changed()

    async def stop(self) -> None:
        await self.ensure_connected()
        await self.transaction.stop()
        self.state["running"] = False
        self.state["active_zone"] = 0
        self.state["remaining_seconds"] = 0
        await self._notify_state_changed()

    async def refresh(self) -> HunterState:
        await self.ensure_connected()
        return self.state

    async def refresh_battery(self) -> int | None:
        """Read the standard BLE Battery Level characteristic."""
        await self.ensure_connected()
        try:
            value = await self.connection.read(BATTERY_LEVEL_UUID)
            battery = int(value[0]) if value else None
        except Exception as err:
            raise HunterManagerError(f"Unable to read battery level: {err}") from err
        self.state["battery"] = battery
        await self._notify_state_changed()
        return battery

    async def shutdown(self) -> None:
        await self.disconnect()
