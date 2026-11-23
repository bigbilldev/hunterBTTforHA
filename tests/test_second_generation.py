"""Tests for second-generation Hunter protocol codecs and initialization."""

from datetime import datetime, timezone
import unittest

from hunter_btt.protocol.second_generation import (
    FF83Config,
    build_ff83,
    build_ff84,
    merge_android_ff83,
    parse_ff82,
    parse_ff83,
    parse_ff84,
    weekday_bit,
)


FF82_CAPTURE = bytes.fromhex(
    "01 00 01 01 00 00 01 01 00 00 01 01 80 00"
)
FF83_READ_CAPTURE = bytes.fromhex(
    "01 00 02 01 00 02 01 00 00 00 00 00"
)
FF83_INIT_CAPTURE = bytes.fromhex(
    "01 00 01 01 00 01 01 00 00 00 00 00"
)


class SecondGenerationCodecTests(unittest.TestCase):
    def test_ff82_capture_decodes_all_fields_and_preserves_raw_bytes(self):
        status = parse_ff82(FF82_CAPTURE)
        self.assertTrue(status.enabled)
        self.assertEqual(status.suspend_watering, 0)
        self.assertEqual(status.zone1_enabled, 1)
        self.assertEqual(status.zone1_mode, 1)
        self.assertFalse(status.zone1_enable_manual)
        self.assertFalse(status.zone1_enable_ext_manual)
        self.assertEqual(status.zone2_enabled, 1)
        self.assertEqual(status.zone2_mode, 1)
        self.assertFalse(status.zone2_enable_manual)
        self.assertFalse(status.zone2_enable_ext_manual)
        self.assertEqual((status.zone1_state, status.zone2_state), (1, 1))
        self.assertEqual((status.zone1_conflict, status.zone2_conflict), (0x80, 0))

    def test_ff82_rejects_wrong_length(self):
        with self.assertRaisesRegex(ValueError, "FF82 payload must be 14 bytes"):
            parse_ff82(b"\x00" * 13)

    def test_ff83_capture_round_trips(self):
        config = parse_ff83(FF83_READ_CAPTURE)
        self.assertEqual(build_ff83(config), FF83_READ_CAPTURE)
        self.assertEqual(config.zone1_enabled, 2)
        self.assertEqual(config.zone2_enabled, 2)

    def test_ff83_rejects_wrong_length(self):
        with self.assertRaisesRegex(ValueError, "FF83 payload must be 12 bytes"):
            parse_ff83(b"\x00" * 11)

    def test_android_ff83_merge_matches_initialization_capture(self):
        status = parse_ff82(FF82_CAPTURE)
        current = parse_ff83(FF83_READ_CAPTURE)
        merged = merge_android_ff83(current, status)
        self.assertEqual(build_ff83(merged), FF83_INIT_CAPTURE)
        self.assertTrue(merged.enabled)
        self.assertEqual(merged.suspend_watering, 0)
        self.assertEqual(merged.zone1_mode, 1)
        self.assertEqual(merged.zone2_mode, 1)
        self.assertEqual(merged.special_setting, 0)

    def test_android_manual_flag_asymmetry_is_preserved(self):
        status = parse_ff82(
            bytes.fromhex("01 00 01 01 00 00 01 01 00 00 11 01 00 00")
        )
        current = FF83Config(
            enabled=True,
            suspend_watering=0,
            zone1_enabled=1,
            zone1_mode=1,
            zone1_enable_manual=False,
            zone2_enabled=1,
            zone2_mode=1,
            zone2_enable_manual=False,
            run_all_hh=0,
            run_all_mm=0,
            run_all_ss=0,
            special_setting=9,
        )
        merged = merge_android_ff83(current, status)
        self.assertTrue(merged.zone1_enable_manual)
        self.assertFalse(merged.zone2_enable_manual)
        self.assertEqual(merged.special_setting, 9)

    def test_zone_enable_settings_are_preserved_as_bytes(self):
        merged = merge_android_ff83(
            parse_ff83(FF83_READ_CAPTURE),
            parse_ff82(FF82_CAPTURE),
            zone1_enabled=2,
            zone2_enabled=0,
        )
        self.assertEqual((merged.zone1_enabled, merged.zone2_enabled), (2, 0))

    def test_ff84_capture_decodes_and_serializer_matches_layout(self):
        capture = bytes.fromhex("07 ea 08 03 0c 0f 22 01")
        clock = parse_ff84(capture)
        self.assertEqual(
            (clock.year, clock.month, clock.day, clock.hour,
             clock.minute, clock.second, clock.week),
            (2026, 8, 3, 12, 15, 34, 1),
        )
        value = datetime(2026, 8, 3, 12, 15, 34, tzinfo=timezone.utc)
        self.assertEqual(build_ff84(value), capture)

    def test_ff84_weekday_is_android_bitmask(self):
        monday = datetime(2026, 8, 3, tzinfo=timezone.utc)
        sunday = datetime(2026, 8, 9, tzinfo=timezone.utc)
        self.assertEqual(weekday_bit(monday), 1)
        self.assertEqual(weekday_bit(sunday), 64)

    def test_ff84_requires_timezone_aware_datetime(self):
        with self.assertRaisesRegex(ValueError, "timezone-aware"):
            build_ff84(datetime(2026, 8, 3, 12, 15, 34))

