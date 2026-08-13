"""
Parser utilities for the Hunter BTT BLE protocol.

This module converts the raw characteristic payloads into Python data
structures used by the Home Assistant integration.

It intentionally contains no BLE code.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

OFF_TIME: Final = -1

DAY_NAMES: Final = (
    "mon",
    "tue",
    "wed",
    "thu",
    "fri",
    "sat",
    "sun",
)


#
# Dataclasses
#

@dataclass(slots=True)
class TimerConfig:
    enabled: bool
    days_mask: int
    start_times: tuple[int, int, int, int]
    runtime: int


@dataclass(slots=True)
class CyclingConfig:
    enabled: bool
    days_mask: int
    start1: int
    end1: int
    start2: int
    end2: int
    runtime: int
    soak: int


@dataclass(slots=True)
class CountdownState:
    active: bool
    remaining_seconds: int
    zone: int


@dataclass(slots=True)
class Diagnostics:
    battery_mv: int | None = None
    valve_current_ma: int | None = None
    error_code: int | None = None


#
# Helpers
#

def decode_hms(data: bytes) -> int:
    """
    Decode Hunter HH/MM/SS.

    FF FF FF means disabled.
    """
    if len(data) != 3:
        raise ValueError("Expected 3-byte HH/MM/SS value")

    if data == b"\xff\xff\xff":
        return OFF_TIME

    return (
        data[0] * 3600 +
        data[1] * 60 +
        data[2]
    )


def encode_days(mask: int) -> list[str]:
    """
    Convert day bitmask to names.
    """
    days: list[str] = []

    for bit, name in enumerate(DAY_NAMES):
        if mask & (1 << bit):
            days.append(name)

    return days


def decode_days(days: list[str]) -> int:
    """
    Convert day names to Hunter bitmask.
    """
    mask = 0

    lookup = {d: i for i, d in enumerate(DAY_NAMES)}

    for day in days:
        if day.lower() not in lookup:
            raise ValueError(day)

        mask |= 1 << lookup[day.lower()]

    return mask


#
# Timer characteristic (FF87 / FF8C)
#

def parse_timer_characteristic(payload: bytes) -> TimerConfig:
    """
    Parse 15-byte timer payload.
    """
    if len(payload) != 15:
        raise ValueError("Timer payload must be 15 bytes")

    starts = (
        decode_hms(payload[0:3]),
        decode_hms(payload[3:6]),
        decode_hms(payload[6:9]),
        decode_hms(payload[9:12]),
    )

    runtime = decode_hms(payload[12:15])

    return TimerConfig(
        enabled=any(v != OFF_TIME for v in starts),
        days_mask=0,
        start_times=starts,
        runtime=runtime,
    )


#
# Cycling characteristic (FF88 / FF8D)
#

def parse_cycling_characteristic(payload: bytes) -> CyclingConfig:
    """
    Parse 18-byte cycling payload.
    """
    if len(payload) != 18:
        raise ValueError("Cycling payload must be 18 bytes")

    values = [
        decode_hms(payload[i:i + 3])
        for i in range(0, 18, 3)
    ]

    return CyclingConfig(
        enabled=True,
        days_mask=0,
        start1=values[0],
        end1=values[1],
        start2=values[2],
        end2=values[3],
        runtime=values[4],
        soak=values[5],
    )


#
# Config characteristic (FF86 / FF8B)
#

def parse_zone_config(payload: bytes) -> dict:
    """
    Decode the 17-byte zone configuration characteristic.

    The reverse-engineered protocol currently uses only a few bytes.
    Unknown bytes are preserved.
    """
    if len(payload) != 17:
        raise ValueError("Zone config must be 17 bytes")

    return {
        "enabled": bool(payload[0]),
        "days_mask": payload[2],
        "raw": bytes(payload),
    }


#
# Countdown characteristic (FF8A)
#

def parse_countdown(payload: bytes) -> CountdownState:
    """
    Decode countdown notification.

    Minutes = byte 11
    Seconds = byte 12
    Running zone = byte 1
    """
    if len(payload) != 16:
        raise ValueError("Countdown payload must be 16 bytes")

    minutes = payload[11]
    seconds = payload[12]

    remaining = minutes * 60 + seconds

    return CountdownState(
        active=remaining > 0,
        remaining_seconds=remaining,
        zone=payload[1],
    )


#
# Diagnostics
#

def parse_diagnostics(payload: bytes) -> Diagnostics:
    """
    Decode FF89 / FF8E diagnostics.

    Much of this characteristic is still undocumented, so unknown bytes
    are intentionally ignored until more devices are captured.
    """
    if len(payload) < 6:
        return Diagnostics()

    battery = (payload[0] << 8) | payload[1]
    current = (payload[2] << 8) | payload[3]
    error = payload[4]

    return Diagnostics(
        battery_mv=battery,
        valve_current_ma=current,
        error_code=error,
    )


#
# Battery
#

def parse_battery(payload: bytes) -> int:
    """
    Standard GATT Battery Level (0x2A19).
    """
    if len(payload) != 1:
        raise ValueError

    return payload[0]


#
# Utility
#

def seconds_to_hhmm(seconds: int) -> str:
    if seconds == OFF_TIME:
        return "--:--"

    h = seconds // 3600
    m = (seconds % 3600) // 60

    return f"{h:02}:{m:02}"


def seconds_to_hhmmss(seconds: int) -> str:
    if seconds == OFF_TIME:
        return "--:--:--"

    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60

    return f"{h:02}:{m:02}:{s:02}"