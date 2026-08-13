"""Text entities."""

from __future__ import annotations

from homeassistant.components.text import TextEntity

from ..entity import HunterEntity


async def async_setup_entry(hass, entry, async_add_entities):

    async_add_entities(
        [
            HunterTimerDays(entry.runtime_data),
            HunterCyclingDays(entry.runtime_data),
        ]
    )


class HunterTimerDays(HunterEntity, TextEntity):

    _attr_name = "Timer Days"

    def __init__(self, coordinator):
        self.entity_description = type(
            "Description",
            (),
            {"key": "timer_days"},
        )
        super().__init__(
            coordinator,
            self.entity_description,
        )

    @property
    def native_value(self):
        return self.coordinator.state["timer_days"]

    async def async_set_value(self, value):
        await self.coordinator.async_set_timer_days(
            value
        )


class HunterCyclingDays(HunterEntity, TextEntity):

    _attr_name = "Cycling Days"

    def __init__(self, coordinator):
        self.entity_description = type(
            "Description",
            (),
            {"key": "cycling_days"},
        )
        super().__init__(
            coordinator,
            self.entity_description,
        )

    @property
    def native_value(self):
        return self.coordinator.state["cycling_days"]

    async def async_set_value(self, value):
        await self.coordinator.async_set_cycling_days(
            value
        )