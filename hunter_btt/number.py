"""Number platform."""

from __future__ import annotations

from homeassistant.components.number import (
    NumberEntity,
    NumberEntityDescription,
)

from .entity import HunterEntity


RUNTIME_DESCRIPTION = NumberEntityDescription(
    key="manual_runtime",
)


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up Hunter BTT number entities."""

    async_add_entities(
        [HunterRuntimeNumber(entry.runtime_data)]
    )


class HunterRuntimeNumber(HunterEntity, NumberEntity):
    """Manual runtime for Zone 1."""

    _attr_name = "Manual Runtime"
    _attr_native_min_value = 1
    _attr_native_max_value = 3600
    _attr_native_step = 1
    _attr_native_unit_of_measurement = "s"

    def __init__(self, coordinator):
        self.entity_description = RUNTIME_DESCRIPTION
        super().__init__(
            coordinator,
            self.entity_description,
        )
        self._zone = 1

    @property
    def native_value(self):
        """Return the configured Zone 1 runtime."""
        return self.coordinator.zone_runtime(1)

    async def async_set_native_value(self, value):
        """Set the configured Zone 1 runtime."""
        await self.coordinator.async_set_manual_runtime(
            1,
            int(value),
        )
