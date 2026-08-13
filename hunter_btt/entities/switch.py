"""Switch platform."""

from __future__ import annotations

from homeassistant.components.switch import SwitchEntity

from ..entity import HunterEntity


async def async_setup_entry(hass, entry, async_add_entities):

    async_add_entities(
        [
            HunterTimerEnabled(entry.runtime_data),
            HunterCyclingEnabled(entry.runtime_data),
        ]
    )


class HunterTimerEnabled(HunterEntity, SwitchEntity):

    _attr_name = "Timer Enabled"

    def __init__(self, coordinator):
        self.entity_description = type(
            "Description",
            (),
            {"key": "timer_enabled"},
        )
        super().__init__(
            coordinator,
            self.entity_description,
        )

    @property
    def is_on(self):
        return self.coordinator.state["timer_enabled"]

    async def async_turn_on(self, **kwargs):
        await self.coordinator.async_enable_timer(True)

    async def async_turn_off(self, **kwargs):
        await self.coordinator.async_enable_timer(False)


class HunterCyclingEnabled(HunterEntity, SwitchEntity):

    _attr_name = "Cycling Enabled"

    def __init__(self, coordinator):
        self.entity_description = type(
            "Description",
            (),
            {"key": "cycling_enabled"},
        )
        super().__init__(
            coordinator,
            self.entity_description,
        )

    @property
    def is_on(self):
        return self.coordinator.state["cycling_enabled"]

    async def async_turn_on(self, **kwargs):
        await self.coordinator.async_enable_cycling(True)

    async def async_turn_off(self, **kwargs):
        await self.coordinator.async_enable_cycling(False)