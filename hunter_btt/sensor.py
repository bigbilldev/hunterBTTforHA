"""Sensor platform."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.const import PERCENTAGE

from .entity import HunterEntity


def validated_battery_level(value: object) -> int | None:
    """Return a valid BLE battery percentage, or None for invalid data."""
    if isinstance(value, bool) or not isinstance(value, int):
        return None
    return value if 0 <= value <= 100 else None


@dataclass(frozen=True, kw_only=True)
class HunterSensorDescription(SensorEntityDescription):
    """Description of a Hunter BTT sensor."""

    value_key: str
    zone: int | None = None


SENSORS = (
    HunterSensorDescription(
        key="battery",
        name="Battery Level",
        value_key="battery",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.BATTERY,
    ),
    HunterSensorDescription(
        key="remaining_time",
        name="Remaining Time",
        value_key="remaining_seconds",
        native_unit_of_measurement="s",
    ),
    HunterSensorDescription(
        key="runtime",
        name="Manual Runtime",
        value_key="runtime",
        native_unit_of_measurement="s",
        zone=1,
    ),
)


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up Hunter BTT sensors."""

    coordinator = entry.runtime_data

    async_add_entities(
        HunterSensor(coordinator, desc)
        for desc in SENSORS
    )


class HunterSensor(HunterEntity, SensorEntity):
    """Hunter BTT sensor."""

    entity_description: HunterSensorDescription

    @property
    def native_value(self):
        """Return the current sensor value."""

        description = self.entity_description

        if description.zone is not None:
            return self.coordinator.zone_runtime(
                description.zone
            )

        value = self.coordinator.data.get(description.value_key)
        if description.value_key == "battery":
            # BLE Battery Level is a percentage; reject malformed values.
            return validated_battery_level(value)
        return value
