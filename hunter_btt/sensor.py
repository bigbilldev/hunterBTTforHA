"""Sensor platform."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    SensorDeviceClass,
)
from homeassistant.const import PERCENTAGE

from ..entity import HunterEntity


@dataclass(frozen=True, kw_only=True)
class HunterSensorDescription(SensorEntityDescription):
    value_key: str


SENSORS = (
    HunterSensorDescription(
        key="battery",
        name="Battery",
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
        value_key="manual_runtime",
        native_unit_of_measurement="s",
    ),
)


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = entry.runtime_data

    async_add_entities(
        HunterSensor(coordinator, desc)
        for desc in SENSORS
    )


class HunterSensor(HunterEntity, SensorEntity):

    entity_description: HunterSensorDescription

    @property
    def native_value(self):
        return self.coordinator.state.get(
            self.entity_description.value_key
        )