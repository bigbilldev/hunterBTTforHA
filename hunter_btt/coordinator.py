"""
coordinator.py

Home Assistant DataUpdateCoordinator for the Hunter BTT integration.

Architecture

Entities
    │
    ▼
HunterDataUpdateCoordinator
    │
    ▼
HunterBLEManager
    │
    ▼
BLE Stack
"""

from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from homeassistant.components import bluetooth

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
    """
    Coordinates all communication with the Hunter controller.
    """

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
    ) -> None:

        self.hass = hass
        self.entry = entry

        self.address: str = entry.data["address"]
        self.name: str = entry.data.get(
            "name",
            "Hunter BTT",
        )

        #
        # Locate BLE discovery information.
        #

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
                int(
                    DEFAULT_SCAN_INTERVAL.total_seconds()
                ),
            )
        )

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=interval,
        )

    # ------------------------------------------------------------------
    # Coordinator update
    # ------------------------------------------------------------------

    async def _async_update_data(
        self,
    ) -> dict[str, Any]:
        """
        Refresh state from the controller.
        """

        try:

            data = await self.manager.refresh()

            return data

        except Exception as err:

            raise UpdateFailed(
                str(err),
            ) from err

    # ------------------------------------------------------------------
    # Manager callback
    # ------------------------------------------------------------------

    async def _manager_updated(self) -> None:
        """
        Called whenever the BLE manager updates state from
        notifications or writes.

        This avoids waiting for the polling interval.
        """

        self.async_set_updated_data(
            self.manager.state,
        )

    # ------------------------------------------------------------------
    # Connection helpers
    # ------------------------------------------------------------------

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
        """
        Called from __init__.py during unload.
        """

        await self.manager.shutdown()

    # ------------------------------------------------------------------
    # Convenience accessors
    # ------------------------------------------------------------------

    @property
    def battery(self):
        return self.data.get("battery")

    @property
    def running(self):
        return self.data.get(
            "running",
            False,
        )

    @property
    def active_zone(self):
        return self.data.get(
            "active_zone",
            0,
        )

    @property
    def remaining_seconds(self):
        return self.data.get(
            "remaining_seconds",
            0,
        )

    def zone(self, zone: int):
        return (
            self.data
            .get("zones", {})
            .get(zone, {})
        )
    # ------------------------------------------------------------------
    # Manual irrigation
    # ------------------------------------------------------------------

    async def async_start_zone(
        self,
        zone: int,
        runtime: int,
    ) -> None:
        """
        Start manual watering for a zone.
        """

        await self.manager.start_zone(
            zone,
            runtime,
        )

        await self.async_request_refresh()

    async def async_stop(self) -> None:
        """
        Stop all watering.
        """

        await self.manager.stop()

        await self.async_request_refresh()

    async def async_set_manual_runtime(
        self,
        zone: int,
        runtime: int,
    ) -> None:
        """
        Update the cached runtime for a zone.
        """

        await self.manager.set_manual_runtime(
            zone,
            runtime,
        )

        self.async_set_updated_data(
            self.manager.state,
        )

    # ------------------------------------------------------------------
    # Timer scheduling
    # ------------------------------------------------------------------

    async def async_write_timer(
        self,
        zone: int,
        schedule,
    ) -> None:
        """
        Write a complete timer schedule.
        """

        await self.manager.write_timer(
            zone,
            schedule,
        )

        await self.async_request_refresh()

    async def async_enable_timer(
        self,
        zone: int,
        enabled: bool,
    ) -> None:
        """
        Enable or disable timer mode.
        """

        await self.manager.enable_timer(
            zone,
            enabled,
        )

        await self.async_request_refresh()

    # ------------------------------------------------------------------
    # Cycling scheduling
    # ------------------------------------------------------------------

    async def async_write_cycling(
        self,
        zone: int,
        schedule,
    ) -> None:
        """
        Write a complete cycling schedule.
        """

        await self.manager.write_cycling(
            zone,
            schedule,
        )

        await self.async_request_refresh()

    async def async_enable_cycling(
        self,
        zone: int,
        enabled: bool,
    ) -> None:
        """
        Enable or disable cycling mode.
        """

        await self.manager.enable_cycling(
            zone,
            enabled,
        )

        await self.async_request_refresh()

    # ------------------------------------------------------------------
    # Characteristic passthrough
    # ------------------------------------------------------------------

    async def async_read_characteristic(
        self,
        uuid: str,
    ) -> bytes:
        """
        Read a raw GATT characteristic.
        """

        return await self.manager.read_characteristic(
            uuid,
        )

    async def async_write_characteristic(
        self,
        uuid: str,
        payload: bytes,
    ) -> None:
        """
        Write a raw GATT characteristic.
        """

        await self.manager.write_characteristic(
            uuid,
            payload,
        )

        await self.async_request_refresh()

    # ------------------------------------------------------------------
    # Refresh helpers
    # ------------------------------------------------------------------

    async def async_refresh_zone(
        self,
        zone: int,
    ):
        """
        Refresh a single zone.
        """

        await self.manager.refresh_zone(
            zone,
        )

        self.async_set_updated_data(
            self.manager.state,
        )

        return self.zone(zone)

    async def async_refresh_battery(
        self,
    ) -> int | None:
        """
        Refresh only the battery level.
        """

        battery = await self.manager.refresh_battery()

        self.async_set_updated_data(
            self.manager.state,
        )

        return battery

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    @property
    def diagnostics(self) -> dict[str, Any]:
        """
        Data exposed through diagnostics.py.
        """

        return self.manager.diagnostics

    @property
    def device_info(self) -> dict[str, Any]:
        """
        Convenience values used by entities.
        """

        return {
            "address": self.address,
            "name": self.name,
            "connected": self.connected,
            "battery": self.battery,
            "running": self.running,
            "active_zone": self.active_zone,
            "remaining_seconds": (
                self.remaining_seconds
            ),
        }

    # ------------------------------------------------------------------
    # Entity helpers
    # ------------------------------------------------------------------

    def is_zone_running(
        self,
        zone: int,
    ) -> bool:
        """
        True if the specified zone is currently watering.
        """

        return (
            self.running
            and self.active_zone == zone
        )

    def zone_runtime(
        self,
        zone: int,
    ) -> int:
        """
        Configured runtime for a zone.
        """

        zone_state = self.zone(zone)

        return zone_state.get(
            "runtime",
            0,
        )

    def timer_enabled(
        self,
        zone: int,
    ) -> bool:
        """
        Timer mode enabled.
        """

        return (
            self.zone(zone)
            .get("timer_enabled", False)
        )

    def cycling_enabled(
        self,
        zone: int,
    ) -> bool:
        """
        Cycling mode enabled.
        """

        return (
            self.zone(zone)
            .get("cycling_enabled", False)
        )

    # ------------------------------------------------------------------
    # Reload support
    # ------------------------------------------------------------------

    async def async_reconnect(self) -> None:
        """
        Force a BLE reconnect.
        """

        await self.manager.disconnect()
        await self.manager.connect()

        await self.async_request_refresh()

    async def async_reset(self) -> None:
        """
        Clear cached data and perform a full refresh.
        """

        self.manager.clear_cache()

        await self.async_request_refresh()
