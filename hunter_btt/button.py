"""Button platform."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.button import (
    ButtonEntity,
    ButtonEntityDescription,
)

from ..entity import HunterEntity


@dataclass(frozen=True, kw_only=True)
class HunterButtonDescription(ButtonEntityDescription):
    command: str


BUTTONS = (
    HunterButtonDescription(
        key="start",
        name="Start Watering",
        command="start",
    ),
    HunterButtonDescription(
        key="stop",
        name="Stop Watering",
        command="stop",
    ),
    HunterButtonDescription(
        key="refresh",
        name="Refresh",
        command="refresh",
    ),
)


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = entry.runtime_data

    async_add_entities(
        HunterButton(coordinator, desc)
        for desc in BUTTONS
    )


class HunterButton(HunterEntity, ButtonEntity):

    entity_description: HunterButtonDescription

    async def async_press(self):

        if self.entity_description.command == "start":
            await self.coordinator.async_start_zone()

        elif self.entity_description.command == "stop":
            await self.coordinator.async_stop_zone()

        elif self.entity_description.command == "refresh":
            await self.coordinator.async_request_refresh()