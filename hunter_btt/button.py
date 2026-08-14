"""Button platform."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription

from .entity import HunterEntity


@dataclass(frozen=True, kw_only=True)
class HunterButtonDescription(ButtonEntityDescription):
    """Description of a Hunter BTT button."""

    command: str
    zone: int | None = None


BUTTONS = (
    HunterButtonDescription(
        key="start",
        name="Start Watering",
        command="start",
        zone=1,
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
    """Set up Hunter BTT buttons."""

    coordinator = entry.runtime_data
    async_add_entities(
        HunterButton(coordinator, desc)
        for desc in BUTTONS
    )


class HunterButton(HunterEntity, ButtonEntity):
    """Hunter BTT button."""

    entity_description: HunterButtonDescription

    async def async_press(self) -> None:
        """Handle a button press."""

        command = self.entity_description.command

        if command == "start":
            zone = self.entity_description.zone or 1
            runtime = self.coordinator.zone_runtime(zone)

            if runtime <= 0:
                runtime = 60

            await self.coordinator.async_start_zone(
                zone,
                runtime,
            )

        elif command == "stop":
            await self.coordinator.async_stop()

        elif command == "refresh":
            await self.coordinator.async_request_refresh()
