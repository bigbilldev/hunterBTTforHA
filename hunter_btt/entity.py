"""
Base entity classes for the Hunter BTT integration.

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
        description: EntityDescription,
    ) -> None:
        super().__init__(coordinator)

        self.entity_description = description

        self._zone = getattr(description, "zone", None)

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
