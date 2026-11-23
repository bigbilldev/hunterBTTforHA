"""Home Assistant coordinator for Hunter BTT."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .bluetooth.manager import HunterBLEManager, HunterManagerError
from .const import CONF_ADDRESS, CONF_NAME, CONF_PASSCODE, DEFAULT_RUNTIME, DEFAULT_SCAN_INTERVAL
from .models import HunterState

_LOGGER = logging.getLogger(__name__)


class HunterDataUpdateCoordinator(DataUpdateCoordinator[HunterState]):
    """Own the controller manager and expose its state to HA entities."""

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry) -> None:
        self.config_entry = config_entry
        self._address = config_entry.data[CONF_ADDRESS]
        self.name = config_entry.data.get(CONF_NAME, "Hunter BTT")
        self._manager = HunterBLEManager(
            hass=hass,
            address=self._address,
            passcode=config_entry.data.get(CONF_PASSCODE, "0000"),
            zone1_enabled=int(
                config_entry.options.get(
                    "zone1_enabled",
                    config_entry.data.get("zone1_enabled", 1),
                )
            ),
            zone2_enabled=int(
                config_entry.options.get(
                    "zone2_enabled",
                    config_entry.data.get("zone2_enabled", 1),
                )
            ),
        )
        self.data = self._manager.state
        self._remove_listener = None

        super().__init__(
            hass,
            _LOGGER,
            name=self.name,
            update_interval=DEFAULT_SCAN_INTERVAL,
        )
        self._remove_listener = self._manager.add_listener(self._manager_state_updated)

    @property
    def manager(self) -> HunterBLEManager:
        return self._manager

    @property
    def address(self) -> str:
        return self._address

    @property
    def connected(self) -> bool:
        return self._manager.connected

    @property
    def available(self) -> bool:
        return self._manager.connected

    @property
    def state(self) -> HunterState:
        return self.data

    @property
    def battery(self) -> int | None:
        return self.data.battery

    @property
    def active_zone(self) -> int | None:
        return self.data.active_zone

    @property
    def remaining_seconds(self) -> int:
        return self.data.remaining_seconds

    def zone_runtime(self, zone: int) -> int:
        return int(self.data.get("zones", {}).get(zone, {}).get("runtime", DEFAULT_RUNTIME))

    def timer_enabled(self, zone: int) -> bool:
        return bool(self.data.get("zones", {}).get(zone, {}).get("timer", {}).get("enabled", False))

    def cycling_enabled(self, zone: int) -> bool:
        return bool(self.data.get("zones", {}).get(zone, {}).get("cycling", {}).get("enabled", False))

    def _manager_state_updated(self, state: HunterState) -> None:
        self.data = state
        self.async_set_updated_data(state)

    async def _async_update_data(self) -> HunterState:
        try:
            if not self._manager.connected:
                await self._manager.connect()
            return await self._manager.refresh()
        except ConfigEntryAuthFailed:
            raise
        except HunterManagerError as err:
            raise UpdateFailed(str(err)) from err
        except Exception as err:
            raise UpdateFailed(f"Unexpected Hunter refresh failure: {err}") from err

    async def async_connect(self) -> None:
        if not self._manager.connected:
            await self._manager.connect()
        self.data = self._manager.state
        self.async_set_updated_data(self.data)

    async def async_disconnect(self) -> None:
        await self._manager.disconnect()
        self.data = self._manager.state
        self.async_set_updated_data(self.data)

    async def async_start_zone(self, zone: int, runtime: int | None = None) -> None:
        selected_runtime = runtime or self.zone_runtime(zone) or 60
        await self._manager.start_zone(zone, selected_runtime)
        self.data = self._manager.state
        self.async_set_updated_data(self.data)

    async def async_stop(self) -> None:
        await self._manager.stop()
        self.data = self._manager.state
        self.async_set_updated_data(self.data)

    async def async_refresh_battery(self) -> int | None:
        battery = await self._manager.refresh_battery()
        self.data = self._manager.state
        self.async_set_updated_data(self.data)
        return battery

    async def async_set_manual_runtime(self, zone: int, runtime: int) -> None:
        """Set the local manual-start runtime used by the START button."""
        if zone not in (1, 2) or not 1 <= runtime <= 3600:
            raise ValueError("Zone must be 1 or 2 and runtime must be 1..3600 seconds.")
        self.data.setdefault("zones", {}).setdefault(zone, {})["runtime"] = runtime
        self.async_set_updated_data(self.data)

    async def async_shutdown(self) -> None:
        if self._remove_listener is not None:
            self._remove_listener()
            self._remove_listener = None
        await self._manager.shutdown()

    async def async_refresh_all(self) -> None:
        await self.async_request_refresh()
