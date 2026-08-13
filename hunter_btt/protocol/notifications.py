"""
Notification decoding for the Hunter BTT201 BLE protocol.

This module handles notifications from:

    FF82 - Command/status notifications
    FF8A - Countdown characteristic
    FF8F - Live status notifications

Unlike parser.py, these payloads are asynchronous events rather than
configuration characteristics.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum
from typing import Final


class NotificationType(IntEnum):
    UNKNOWN = 0
    STARTED = 1
    STOPPED = 2
    PAUSED = 3
    FINISHED = 4
    ERROR = 5


@dataclass(slots=True)
class RuntimeNotification:
    running: bool
    zone: int
    remaining_seconds: int


@dataclass(slots=True)
class CommandNotification:
    success: bool
    notification: NotificationType
    raw: bytes


@dataclass(slots=True)
class StatusNotification:
    zone: int
    running: bool
    manual: bool
    timer_enabled: bool
    cycling_enabled: bool
    battery_percent: int | None = None
    raw: bytes | None = None


#
# Helpers
#

def _decode_remaining(minutes: int, seconds: int) -> int:
    if seconds > 59:
        return 0

    return minutes * 60 + seconds


#
# FF8A Countdown notifications
#

def decode_countdown(payload: bytes) -> RuntimeNotification:
    """
    Decode FF8A countdown characteristic.

    Reverse engineered layout:

        byte1   active zone
        byte11  minutes remaining
        byte12  seconds remaining
    """

    if len(payload) != 16:
        raise ValueError("Invalid countdown payload")

    zone = payload[1]

    remaining = _decode_remaining(
        payload[11],
        payload[12],
    )

    return RuntimeNotification(
        running=remaining > 0,
        zone=zone,
        remaining_seconds=remaining,
    )


#
# FF82 acknowledgements
#

def decode_command_notification(payload: bytes) -> CommandNotification:
    """
    Decode FF82 acknowledgement.

    Hunter returns a small acknowledgement after writes.
    """

    if not payload:
        raise ValueError("Empty payload")

    success = payload[0] == 0x00

    notification = NotificationType.UNKNOWN

    if len(payload) > 1:
        code = payload[1]

        notification = {
            0x01: NotificationType.STARTED,
            0x02: NotificationType.STOPPED,
            0x03: NotificationType.PAUSED,
            0x04: NotificationType.FINISHED,
            0x05: NotificationType.ERROR,
        }.get(code, NotificationType.UNKNOWN)

    return CommandNotification(
        success=success,
        notification=notification,
        raw=payload,
    )


#
# FF8F live status
#

def decode_status_notification(payload: bytes) -> StatusNotification:
    """
    Decode FF8F status notification.

    The reverse-engineered protocol shows only a handful of fields.
    Unknown bytes are preserved in raw.
    """

    if len(payload) < 8:
        raise ValueError("Invalid status payload")

    flags = payload[0]

    running = bool(flags & 0x01)
    manual = bool(flags & 0x02)
    timer = bool(flags & 0x04)
    cycling = bool(flags & 0x08)

    zone = payload[1]

    battery = None

    if len(payload) > 2:
        if payload[2] <= 100:
            battery = payload[2]

    return StatusNotification(
        zone=zone,
        running=running,
        manual=manual,
        timer_enabled=timer,
        cycling_enabled=cycling,
        battery_percent=battery,
        raw=payload,
    )


#
# Dispatcher
#

def decode_notification(
    characteristic_uuid: str,
    payload: bytes,
):
    """
    Decode any incoming notification.

    Returns one of:

        RuntimeNotification
        CommandNotification
        StatusNotification
        bytes
    """

    uuid = characteristic_uuid.lower()

    if uuid.endswith("ff8a-0000-1000-8000-00805f9b34fb"):
        return decode_countdown(payload)

    if uuid.endswith("ff82-0000-1000-8000-00805f9b34fb"):
        return decode_command_notification(payload)

    if uuid.endswith("ff8f-0000-1000-8000-00805f9b34fb"):
        return decode_status_notification(payload)

    return payload