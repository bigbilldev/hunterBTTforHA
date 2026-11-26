"""Tests for Home Assistant runtime display units."""

import unittest

from hunter_btt.number import minutes_to_seconds
from hunter_btt.sensor import seconds_to_minutes


class RuntimeUnitTests(unittest.TestCase):
    def test_manual_runtime_seconds_display_as_minutes(self):
        self.assertEqual(seconds_to_minutes(600), 10)
        self.assertEqual(seconds_to_minutes(90), 1.5)

    def test_remaining_time_seconds_display_as_minutes(self):
        self.assertEqual(seconds_to_minutes(600), 10)
        self.assertEqual(seconds_to_minutes(1), 0.02)

    def test_invalid_seconds_value_is_not_displayed(self):
        self.assertIsNone(seconds_to_minutes(None))
        self.assertIsNone(seconds_to_minutes(True))
        self.assertIsNone(seconds_to_minutes("600"))

    def test_minutes_are_converted_to_seconds_for_ble_commands(self):
        self.assertEqual(minutes_to_seconds(10), 600)
        self.assertEqual(minutes_to_seconds(1), 60)
        self.assertEqual(minutes_to_seconds(60), 3600)


if __name__ == "__main__":
    unittest.main()
