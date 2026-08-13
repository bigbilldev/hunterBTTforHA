"""
Packet builders for the Hunter BTT201 BLE protocol.

Translated directly from the reverse-engineered ESP32 bridge.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

MAX_WATERING_SECONDS: Final = 3600
OFF_TIME: Final = -1


class PacketError(ValueError):
    """Raised when an invalid packet would be generated."""


@dataclass(slots=True)
class TimerSchedule:
    enabled: bool
    days_mask: int
    start_times: tuple[int, int, int, int]
    run_seconds: int


@dataclass(slots=True)
class CyclingSchedule:
    enabled: bool
    days_mask: int
    start1: int
    end1: int
    start2: int
    end2: int
    run_seconds: int
    soak_seconds: int


def _validate_seconds(value: int) -> None:
    if value == OFF_TIME:
        return
    if not 0 <= value <= 86399:
        raise PacketError("time must be OFF or between 00:00:00 and 23:59:59")


def _encode_hms(value: int) -> bytes:
    """
    Encodes seconds into Hunter HH/MM/SS format.

    OFF is encoded as FF FF FF.
    """
    _validate_seconds(value)

    if value == OFF_TIME:
        return b"\xff\xff\xff"

    hours = value // 3600
    minutes = (value % 3600) // 60
    seconds = value % 60

    return bytes((hours, minutes, seconds))


#
# Manual watering packets
#

def build_prepare_packet(zone: int, hint: int = 0x0A) -> bytes:
    if zone not in (1, 2):
        raise PacketError("zone must be 1 or 2")

    return bytes(
        (
            0x01,
            0x00,
            zone,
            0x02,
            0x00,
            zone,
            0x02,
            0x00,
            hint,
            0x00,
            0x00,
            0x00,
        )
    )


def build_arm_packet(zone: int, hint: int = 0x0A) -> bytes:
    if zone not in (1, 2):
        raise PacketError("zone must be 1 or 2")

    return bytes(
        (
            0x01,
            0x00,
            zone,
            0x02,
            0x01,
            zone,
            0x02,
            0x00,
            hint,
            0x00,
            0x00,
            0x00,
        )
    )


def build_stop_packet() -> bytes:
    return bytes(
        (
            0x01,
            0x00,
            0x02,
            0x02,
            0x00,
            0x02,
            0x02,
            0x00,
            0x0A,
            0x00,
            0x00,
            0x00,
        )
    )


def build_duration_packet(total_seconds: int) -> bytes:
    if not 0 <= total_seconds <= MAX_WATERING_SECONDS:
        raise PacketError("duration exceeds 3600 seconds")

    minutes = total_seconds // 60
    seconds = total_seconds % 60

    return bytes(
        (
            0x04,
            0x01,
            0x7F,
            0xFF,
            0xFF,
            0xFF,
            0xFF,
            0x00,
            0xFF,
            0xFF,
            0xFF,
            0x00,
            minutes,
            seconds,
            0x00,
            0x1E,
            0x00,
        )
    )


#
# Timer blocks (FF87 / FF8C)
#

def build_timer_block(schedule: TimerSchedule) -> bytes:
    if schedule.run_seconds > MAX_WATERING_SECONDS:
        raise PacketError("run_seconds exceeds 3600")

    if len(schedule.start_times) != 4:
        raise PacketError("exactly four start times required")

    block = bytearray()

    enabled = False

    for start in schedule.start_times:
        if start != OFF_TIME:
            enabled = True
        block.extend(_encode_hms(start))

    block.extend(_encode_hms(schedule.run_seconds))

    if len(block) != 15:
        raise AssertionError

    if schedule.enabled and not enabled:
        raise PacketError("enabled schedule has no start times")

    return bytes(block)


#
# Cycling blocks (FF88 / FF8D)
#

def build_cycling_block(schedule: CyclingSchedule) -> bytes:
    if schedule.run_seconds > MAX_WATERING_SECONDS:
        raise PacketError("run_seconds exceeds 3600")

    values = (
        schedule.start1,
        schedule.end1,
        schedule.start2,
        schedule.end2,
        schedule.run_seconds,
        schedule.soak_seconds,
    )

    block = bytearray()

    for value in values:
        block.extend(_encode_hms(value))

    if len(block) != 18:
        raise AssertionError

    return bytes(block)


#
# Configuration mutations (17-byte FF86 / FF8B payloads)
#

def mutate_timer_config(
    current: bytes,
    enabled: bool,
    days_mask: int,
) -> bytes:
    if len(current) != 17:
        raise PacketError("timer config must be 17 bytes")

    payload = bytearray(current)
    payload[0] = 0x01 if enabled else 0x00
    payload[2] = days_mask & 0x7F

    return bytes(payload)


def mutate_cycling_config(
    current: bytes,
    enabled: bool,
    days_mask: int,
) -> bytes:
    if len(current) != 17:
        raise PacketError("cycling config must be 17 bytes")

    payload = bytearray(current)
    payload[0] = 0x02 if enabled else 0x00
    payload[7] = days_mask & 0x7F

    return bytes(payload)


#
# Notification decoder
#

def decode_remaining_seconds(payload: bytes) -> int | None:
    """
    Decode FF8A countdown notification.

    Payload length: 16 bytes
    Minute byte: 11
    Second byte: 12
    """
    if len(payload) != 16:
        return None

    minutes = payload[11]
    seconds = payload[12]

    if seconds > 59:
        return None

    return minutes * 60 + seconds