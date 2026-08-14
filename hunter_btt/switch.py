"""Switch platform."""

from __future__ import annotations

from homeassistant.components.switch import (
    SwitchEntity,
    SwitchEntityDescription,
)

from .entity import HunterEntity


TIMER_ENABLED_DESCRIPTION = SwitchEntityDescription(
    key="timer_enabled",
)

CYCLING_ENABLED_DESCRIPTION = SwitchEntityDescription(
    key="cycling_enabled",
)


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up Hunter BTT switches."""

    coordinator = entry.runtime_data

    async_add_entities(
        [
            HunterTimerEnabled(coordinator),
            HunterCyclingEnabled(coordinator),
        ]
    )


class HunterTimerEnabled(HunterEntity, SwitchEntity):
    """Timer-enabled switch for Zone 1."""

    _attr_name = "Timer Enabled"

    def __init__(self, coordinator):
        self.entity_description = TIMER_ENABLED_DESCRIPTION
        super().__init__(
            coordinator,
            self.entity_description,
        )
        self._zone = 1

    @property
    def is_on(self):
        """Return whether Zone 1 timer mode is enabled."""
        return self.coordinator.timer_enabled(1)

    async def async_turn_on(self, **kwargs):
        """Enable Zone 1 timer mode."""
        await self.coordinator.async_enable_timer(1, True)

    async def async_turn_off(self, **kwargs):
        """Disable Zone 1 timer mode."""
        await self.coordinator.async_enable_timer(1, False)


class HunterCyclingEnabled(HunterEntity, SwitchEntity):
    """Cycling-enabled switch for Zone 1."""

    _attr_name = "Cycling Enabled"

    def __init__(self, coordinator):
        self.entity_description = CYCLING_ENABLED_DESCRIPTION
        super().__init__(
            coordinator,
            self.entity_description,
        )
        self._zone = 1

    @property
    def is_on(self):
        """Return whether Zone 1 cycling mode is enabled."""
        return self.coordinator.cycling_enabled(1)

    async def async_turn_on(self, **kwargs):
        """Enable Zone 1 cycling mode."""
        await self.coordinator.async_enable_cycling(1, True)

    async def async_turn_off(self, **kwargs):
        """Disable Zone 1 cycling mode."""
        await self.coordinator.async_enable_cycling(1, False)
