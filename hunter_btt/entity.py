"""Shared Home Assistant entity behavior for Hunter BTT."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import EntityDescription
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER, MODEL


class HunterEntity(CoordinatorEntity):
    """Base class for entities backed by the Hunter data coordinator."""

    entity_description: EntityDescription

    def __init__(self, coordinator, description: EntityDescription) -> None:
        super().__init__(coordinator)
        self.entity_description = description

        zone = getattr(description, "zone", None)
        address_id = coordinator.address.replace(":", "").lower()
        if zone is None:
            self._attr_unique_id = f"{address_id}_{description.key}"
        else:
            self._attr_unique_id = f"{address_id}_zone{zone}_{description.key}"

        self._attr_has_entity_name = True

    @property
    def device_info(self) -> DeviceInfo:
        """Return the shared Hunter controller device information."""
        return DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.address)},
            manufacturer=MANUFACTURER,
            model=MODEL,
            name=self.coordinator.name,
        )
