"""
Base entity classes for the Hunter BTT201 integration.

Every Home Assistant platform entity derives from HunterEntity,
which exposes the shared DataUpdateCoordinator and zone information.

Platforms:
    - sensor
    - binary_sensor
    - switch
    - number
    - button
    - select (future)
"""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import EntityDescription
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
)

from .const import (
    DOMAIN,
    MANUFACTURER,
    MODEL,
)


@dataclass(slots=True, frozen=True)
class HunterEntityDescription(EntityDescription):
    """Entity description."""

    zone: int | None = None


class HunterEntity(CoordinatorEntity):
    """
    Base entity for every Hunter platform.

    The coordinator owns all state. Entities only expose
    coordinator data to Home Assistant.
    """

    entity_description: HunterEntityDescription

    def __init__(
        self,
        coordinator,
        description: HunterEntityDescription,
    ) -> None:
        super().__init__(coordinator)

        self.entity_description = description

        self._zone = description.zone

        unique = coordinator.address.replace(":", "").lower()

        if self._zone is None:
            self._attr_unique_id = (
                f"{unique}_{description.key}"
            )
        else:
            self._attr_unique_id = (
                f"{unique}_zone{self._zone}_{description.key}"
            )

        self._attr_has_entity_name = True

    #
    # Convenience
    #

    @property
    def manager(self):
        return self.coordinator.manager

    @property
    def state(self):
        return self.coordinator.data

    @property
    def zone(self):
        return self._zone

    @property
    def available(self) -> bool:
        return (
            self.coordinator.last_update_success
            and self.manager.connected
        )

    #
    # Device
    #

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={
                (
                    DOMAIN,
                    self.coordinator.address,
                )
            },
            manufacturer=MANUFACTURER,
            model=MODEL,
            name=self.coordinator.name,
        )

    #
    # Helpers
    #

    def zone_data(self) -> dict:
        """
        Return state for this zone.

        coordinator.data layout:

            {
                "zones": {
                    1: {...},
                    2: {...},
                }
            }
        """

        if self._zone is None:
            return {}

        return (
            self.coordinator.data
            .get("zones", {})
            .get(self._zone, {})
        )

    #
    # Frequently-used properties
    #

    @property
    def battery(self):
        return self.coordinator.data.get("battery")

    @property
    def running(self):
        return self.coordinator.data.get("running")

    @property
    def active_zone(self):
        return self.coordinator.data.get("active_zone")

    @property
    def remaining_seconds(self):
        return self.coordinator.data.get(
            "remaining_seconds",
            0,
        )

    @property
    def timer_enabled(self):
        return (
            self.zone_data()
            .get("timer", {})
            .get("enabled", False)
        )

    @property
    def cycling_enabled(self):
        return (
            self.zone_data()
            .get("cycling", {})
            .get("enabled", False)
        )

    @property
    def timer_days(self):
        return (
            self.zone_data()
            .get("timer", {})
            .get("days", [])
        )

    @property
    def cycling_days(self):
        return (
            self.zone_data()
            .get("cycling", {})
            .get("days", [])
        )

    @property
    def runtime(self):
        return (
            self.zone_data()
            .get("runtime", 0)
        )

    #
    # Coordinator wrappers
    #

    async def async_refresh(self):
        await self.coordinator.async_request_refresh()

    async def async_start_zone(
        self,
        runtime: int | None = None,
    ):
        await self.coordinator.async_start_zone(
            self.zone,
            runtime,
        )

    async def async_stop(self):
        await self.coordinator.async_stop()

    async def async_set_runtime(
        self,
        runtime: int,
    ):
        await self.coordinator.async_set_runtime(
            self.zone,
            runtime,
        )

    async def async_enable_timer(
        self,
        enabled: bool,
    ):
        await self.coordinator.async_enable_timer(
            self.zone,
            enabled,
        )

    async def async_enable_cycling(
        self,
        enabled: bool,
    ):
        await self.coordinator.async_enable_cycling(
            self.zone,
            enabled,
        )

    async def async_set_timer_days(
        self,
        days: list[str],
    ):
        await self.coordinator.async_set_timer_days(
            self.zone,
            days,
        )

    async def async_set_cycling_days(
        self,
        days: list[str],
    ):
        await self.coordinator.async_set_cycling_days(
            self.zone,
            days,
        )

    #
    # Debug
    #

    @property
    def extra_state_attributes(self):
        attrs = {}

        if self._zone is not None:
            attrs["zone"] = self._zone

        attrs["connected"] = self.manager.connected
        attrs["address"] = self.coordinator.address

        return attrs