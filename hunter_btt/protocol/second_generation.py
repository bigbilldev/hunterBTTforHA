"""Second-generation Hunter FF82/FF83/FF84 protocol codecs.

Field layouts and FF83 startup merge behavior are derived from the Android
Second_82_Protocol, Second_83_Protocol, Second_84_Protocol and
connectTwoInit implementations. Unknown byte values are preserved.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime


def _require_length(payload: bytes, expected: int, characteristic: str) -> None:
    if len(payload) != expected:
        raise ValueError(
            f"{characteristic} payload must be {expected} bytes; got {len(payload)}"
        )


@dataclass(frozen=True, slots=True)
class FF82Status:
    """Live controller status reported by FF82 (14 bytes)."""

    enabled: bool
    suspend_watering: int
    zone1_enabled: int
    zone1_mode: int
    zone1_enable_manual: bool
    zone1_enable_ext_manual: bool
    zone2_enabled: int
    zone2_mode: int
    zone2_enable_manual: bool
    zone2_enable_ext_manual: bool
    zone1_state: int
    zone2_state: int
    zone1_conflict: int
    zone2_conflict: int


def parse_ff82(payload: bytes) -> FF82Status:
    """Decode the exact 14-byte FF82 status record."""
    _require_length(payload, 14, "FF82")
    return FF82Status(
        enabled=payload[0] != 0,
        suspend_watering=payload[1],
        zone1_enabled=payload[2],
        zone1_mode=payload[3],
        zone1_enable_manual=payload[4] != 0,
        zone1_enable_ext_manual=payload[5] != 0,
        zone2_enabled=payload[6],
        zone2_mode=payload[7],
        zone2_enable_manual=payload[8] != 0,
        zone2_enable_ext_manual=payload[9] != 0,
        zone1_state=payload[10],
        zone2_state=payload[11],
        zone1_conflict=payload[12],
        zone2_conflict=payload[13],
    )


@dataclass(frozen=True, slots=True)
class FF83Config:
    """Writable FF83 controller configuration (12 bytes)."""

    enabled: bool
    suspend_watering: int
    zone1_enabled: int
    zone1_mode: int
    zone1_enable_manual: bool
    zone2_enabled: int
    zone2_mode: int
    zone2_enable_manual: bool
    run_all_hh: int
    run_all_mm: int
    run_all_ss: int
    special_setting: int


def parse_ff83(payload: bytes) -> FF83Config:
    """Decode the exact 12-byte FF83 configuration record."""
    _require_length(payload, 12, "FF83")
    return FF83Config(
        enabled=payload[0] != 0,
        suspend_watering=payload[1],
        zone1_enabled=payload[2],
        zone1_mode=payload[3],
        zone1_enable_manual=payload[4] != 0,
        zone2_enabled=payload[5],
        zone2_mode=payload[6],
        zone2_enable_manual=payload[7] != 0,
        run_all_hh=payload[8],
        run_all_mm=payload[9],
        run_all_ss=payload[10],
        special_setting=payload[11],
    )


def build_ff83(config: FF83Config) -> bytes:
    """Serialize FF83 fields in Android's exact 12-byte order."""
    values = (
        int(config.enabled),
        config.suspend_watering,
        config.zone1_enabled,
        config.zone1_mode,
        int(config.zone1_enable_manual),
        config.zone2_enabled,
        config.zone2_mode,
        int(config.zone2_enable_manual),
        config.run_all_hh,
        config.run_all_mm,
        config.run_all_ss,
        config.special_setting,
    )
    if any(not 0 <= value <= 0xFF for value in values):
        raise ValueError("FF83 fields must fit in one byte")
    return bytes(values)


def merge_android_ff83(
    current: FF83Config,
    status: FF82Status,
    *,
    zone1_enabled: int = 1,
    zone2_enabled: int = 1,
) -> FF83Config:
    """Apply Android connectTwoInit's FF82-to-FF83 state merge.

    The zone-1 manual flag intentionally preserves Android's observed
    condition (zone1State == 17 OR zone2State == 5), including its asymmetry.
    """
    if not 0 <= zone1_enabled <= 0xFF or not 0 <= zone2_enabled <= 0xFF:
        raise ValueError("Zone enable settings must fit in one byte")

    zone1_manual = status.zone1_state == 17 or status.zone2_state == 5
    zone2_manual = status.zone2_state == 17 or status.zone2_state == 5
    special_setting = (
        0
        if status.zone1_state != 17 and status.zone2_state != 17
        else current.special_setting
    )
    return replace(
        current,
        enabled=True,
        suspend_watering=status.suspend_watering,
        zone1_enabled=zone1_enabled,
        zone2_enabled=zone2_enabled,
        zone1_enable_manual=zone1_manual,
        zone2_enable_manual=zone2_manual,
        special_setting=special_setting,
    )


@dataclass(frozen=True, slots=True)
class FF84Clock:
    """Controller clock read from FF84."""

    year: int
    month: int
    day: int
    hour: int
    minute: int
    second: int
    week: int


def parse_ff84(payload: bytes) -> FF84Clock:
    """Decode the eight-byte FF84 clock record."""
    _require_length(payload, 8, "FF84")
    return FF84Clock(
        year=int.from_bytes(payload[0:2], "big"),
        month=payload[2],
        day=payload[3],
        hour=payload[4],
        minute=payload[5],
        second=payload[6],
        week=payload[7],
    )


def weekday_bit(value: datetime) -> int:
    """Return Android's weekday bit: Monday=1 ... Sunday=64."""
    return 1 << value.weekday()


def build_ff84(value: datetime) -> bytes:
    """Build Android's eight-byte local-clock payload for FF84."""
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("FF84 time must be timezone-aware")
    if not 1 <= value.year <= 0xFFFF:
        raise ValueError("FF84 year must fit in an unsigned 16-bit field")
    return bytes(
        (
            (value.year >> 8) & 0xFF,
            value.year & 0xFF,
            value.month,
            value.day,
            value.hour,
            value.minute,
            value.second,
            weekday_bit(value),
        )
    )
