"""Home Assistant DataUpdateCoordinator for Hunter BTT."""

from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from homeassistant.components import bluetooth
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .bluetooth.manager import HunterBLEManager
from .const import (
    CONF_POLL_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


class HunterDataUpdateCoordinator(
    DataUpdateCoordinator[dict[str, Any]]
):
    """Coordinate Hunter BLE state and Home Assistant entities."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
    ) -> None:
        self.hass = hass
        self.entry = entry

        self.address = entry.data["address"]
        self.name = entry.data.get(
            "name",
            "Hunter BTT",
        )

        discovery = bluetooth.async_last_service_info(
            hass,
            self.address,
            connectable=True,
        )
        if discovery is None:
            raise UpdateFailed(
                f"Hunter controller {self.address} "
                "is not currently discoverable."
            )

        self.manager = HunterBLEManager(
            hass,
            discovery,
        )
        self.manager.register_callback(
            self._manager_updated,
        )

        interval = timedelta(
            seconds=entry.options.get(
                CONF_POLL_INTERVAL,
                int(DEFAULT_SCAN_INTERVAL.total_seconds()),
            )
        )

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=interval,
        )

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            return await self.manager.refresh()
        except Exception as err:
            raise UpdateFailed(str(err)) from err

    async def _manager_updated(self) -> None:
        """Publish manager state immediately after notification/command."""
        self.async_set_updated_data(self.manager.state)

    @property
    def connected(self) -> bool:
        return self.manager.connected

    @property
    def available(self) -> bool:
        return (
            self.last_update_success
            and self.manager.connected
        )

    async def async_connect(self) -> None:
        await self.manager.connect()

    async def async_disconnect(self) -> None:
        await self.manager.disconnect()

    async def async_shutdown(self) -> None:
        await self.manager.shutdown()

    @property
    def battery(self):
        return self.data.get("battery")

    @property
    def running(self):
        return self.data.get("running", False)

    @property
    def active_zone(self):
        return self.data.get("active_zone", 0)

    @property
    def remaining_seconds(self):
        return self.data.get("remaining_seconds", 0)

    def zone(self, zone: int):
        return self.data.get("zones", {}).get(zone, {})

    async def async_start_zone(self, zone: int, runtime: int) -> None:
        await self.manager.start_zone(zone, runtime)
        self.async_set_updated_data(self.manager.state)

    async def async_stop(self) -> None:
        await self.manager.stop()
        self.async_set_updated_data(self.manager.state)

    async def async_set_manual_runtime(
        self,
        zone: int,
        runtime: int,
    ) -> None:
        await self.manager.set_manual_runtime(zone, runtime)
        self.async_set_updated_data(self.manager.state)

    async def async_write_timer(self, zone: int, schedule) -> None:
        await self.manager.write_timer(zone, schedule)
        self.async_set_updated_data(self.manager.state)

    async def async_enable_timer(
        self,
        zone: int,
        enabled: bool,
    ) -> None:
        await self.manager.enable_timer(zone, enabled)
        self.async_set_updated_data(self.manager.state)

    async def async_write_cycling(
        self,
        zone: int,
        schedule,
    ) -> None:
        await self.manager.write_cycling(zone, schedule)
        self.async_set_updated_data(self.manager.state)

    async def async_enable_cycling(
        self,
        zone: int,
        enabled: bool,
    ) -> None:
        await self.manager.enable_cycling(zone, enabled)
        self.async_set_updated_data(self.manager.state)

    async def async_read_characteristic(self, uuid: str) -> bytes:
        return await self.manager.read_characteristic(uuid)

    async def async_write_characteristic(
        self,
        uuid: str,
        payload: bytes,
    ) -> None:
        await self.manager.write_characteristic(uuid, payload)
        self.async_set_updated_data(self.manager.state)

    async def async_refresh_zone(self, zone: int):
        value = await self.manager.refresh_zone(zone)
        self.async_set_updated_data(self.manager.state)
        return value

    async def async_refresh_battery(self) -> int | None:
        battery = await self.manager.refresh_battery()
        self.async_set_updated_data(self.manager.state)
        return battery

    @property
    def diagnostics(self) -> dict[str, Any]:
        return self.manager.diagnostics

    @property
    def device_info(self) -> dict[str, Any]:
        return {
            "address": self.address,
            "name": self.name,
            "connected": self.connected,
            "battery": self.battery,
            "running": self.running,
            "active_zone": self.active_zone,
            "remaining_seconds": self.remaining_seconds,
        }
