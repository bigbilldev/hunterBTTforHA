"""Tests for Home Assistant sensor value formatting."""

import unittest

from hunter_btt.sensor import validated_battery_level


class BatteryLevelSensorTests(unittest.TestCase):
    def test_accepts_valid_percentage_values(self):
        for value in (0, 1, 50, 100):
            with self.subTest(value=value):
                self.assertEqual(validated_battery_level(value), value)

    def test_rejects_diagnostic_or_out_of_range_values(self):
        for value in (None, True, False, -1, 101, b"\x50", {"battery": 80}, "80"):
            with self.subTest(value=value):
                self.assertIsNone(validated_battery_level(value))


if __name__ == "__main__":
    unittest.main()
