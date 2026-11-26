"""Tests for Home Assistant runtime display units."""

import unittest

from hunter_btt.number import HunterRuntimeNumber, minutes_to_seconds
from types import SimpleNamespace

from hunter_btt.sensor import HunterSensor, SENSORS, seconds_to_minutes


class RuntimeUnitTests(unittest.TestCase):
    def test_manual_runtime_seconds_display_as_minutes(self):
        self.assertEqual(seconds_to_minutes(600), 10)
        self.assertEqual(seconds_to_minutes(90), 1.5)

    def test_remaining_time_seconds_display_as_minutes(self):
        self.assertEqual(seconds_to_minutes(600), 10)
        self.assertEqual(seconds_to_minutes(1), 0.02)

    def test_manual_runtime_sensor_exposes_minutes(self):
        entity = SimpleNamespace(
            entity_description=SENSORS[2],
            coordinator=SimpleNamespace(zone_runtime=lambda zone: 900),
        )
        self.assertEqual(HunterSensor.native_value.fget(entity), 15)

    def test_remaining_time_sensor_exposes_minutes(self):
        entity = SimpleNamespace(
            entity_description=SENSORS[1],
            coordinator=SimpleNamespace(data={"remaining_seconds": 420}),
        )
        self.assertEqual(HunterSensor.native_value.fget(entity), 7)

    def test_number_entity_exposes_manual_runtime_in_minutes(self):
        entity = SimpleNamespace(
            coordinator=SimpleNamespace(zone_runtime=lambda zone: 1200),
        )
        self.assertEqual(HunterRuntimeNumber.native_value.fget(entity), 20)

    def test_invalid_seconds_value_is_not_displayed(self):
        self.assertIsNone(seconds_to_minutes(None))
        self.assertIsNone(seconds_to_minutes(True))
        self.assertIsNone(seconds_to_minutes("600"))

    def test_minutes_are_converted_to_seconds_for_ble_commands(self):
        self.assertEqual(minutes_to_seconds(10), 600)
        self.assertEqual(minutes_to_seconds(1), 60)
        self.assertEqual(minutes_to_seconds(60), 3600)

    def test_home_assistant_entities_advertise_minutes(self):
        self.assertEqual(SENSORS[1].native_unit_of_measurement, "min")
        self.assertEqual(SENSORS[2].native_unit_of_measurement, "min")
        self.assertEqual(HunterRuntimeNumber._attr_native_unit_of_measurement, "min")
        self.assertEqual(HunterRuntimeNumber._attr_native_max_value, 60)


if __name__ == "__main__":
    unittest.main()
