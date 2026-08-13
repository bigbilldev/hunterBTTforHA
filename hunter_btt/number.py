"""Number platform."""

from __future__ import annotations

from homeassistant.components.number import (
    NumberEntity,
)

from .entity import HunterEntity


async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities(
        [HunterRuntimeNumber(entry.runtime_data)]
    )


class HunterRuntimeNumber(HunterEntity, NumberEntity):

    _attr_name = "Manual Runtime"
    _attr_native_min_value = 1
    _attr_native_max_value = 3600
    _attr_native_step = 1
    _attr_native_unit_of_measurement = "s"

    def __init__(self, coordinator):
        self.entity_description = type(
            "Description",
            (),
            {"key": "manual_runtime"},
        )
        super().__init__(
            coordinator,
            self.entity_description,
        )

    @property
    def native_value(self):
        return self.coordinator.state["manual_runtime"]

    async def async_set_native_value(self, value):
        await self.coordinator.async_set_manual_runtime(
            int(value)
        )