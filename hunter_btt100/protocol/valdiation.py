"""
Validation helpers for the Hunter BTT201 integration.

This module centralizes validation rules shared by entities,
coordinator methods, schedules, and protocol builders.

Keeping validation in one place ensures Home Assistant rejects invalid
values before they reach the BLE layer.
"""

from __future__ import annotations

from datetime import time
from typing import Final

MAX_RUNTIME: Final = 3600
MIN_RUNTIME: Final = 0

MAX_SECONDS_IN_DAY: Final = 86399

OFF_TIME: Final = -1

VALID_ZONES: Final = (1, 2)

DAY_NAMES: Final = (
    "mon",
    "tue",
    "wed",
    "thu",
    "fri",
    "sat",
    "sun",
)


class ValidationError(ValueError):
    """Raised when an invalid Hunter protocol value is detected."""


#
# Zone validation
#

def validate_zone(zone: int) -> None:
    if zone not in VALID_ZONES:
        raise ValidationError(
            f"Zone must be one of {VALID_ZONES}"
        )


#
# Runtime validation
#

def validate_runtime(seconds: int) -> None:
    if not MIN_RUNTIME <= seconds <= MAX_RUNTIME:
        raise ValidationError(
            f"Runtime must be between "
            f"{MIN_RUNTIME} and {MAX_RUNTIME} seconds."
        )


#
# Time validation
#

def validate_seconds(seconds: int) -> None:
    """
    Validate protocol HH/MM/SS value.

    OFF_TIME (-1) is accepted.
    """

    if seconds == OFF_TIME:
        return

    if not 0 <= seconds <= MAX_SECONDS_IN_DAY:
        raise ValidationError(
            "Time must be between "
            "00:00:00 and 23:59:59"
        )


def validate_time(value: time | None) -> None:
    if value is None:
        return

    validate_seconds(
        value.hour * 3600
        + value.minute * 60
        + value.second
    )


#
# Day validation
#

def validate_days(days: list[str]) -> None:
    invalid = [
        d
        for d in days
        if d.lower() not in DAY_NAMES
    ]

    if invalid:
        raise ValidationError(
            f"Invalid day names: {invalid}"
        )


def validate_day_mask(mask: int) -> None:
    if not 0 <= mask <= 0x7F:
        raise ValidationError(
            "Day mask must fit in seven bits."
        )


#
# Schedule validation
#

def validate_start_times(times: list[int]) -> None:
    if len(times) != 4:
        raise ValidationError(
            "Exactly four timer start times are required."
        )

    for value in times:
        validate_seconds(value)


def validate_timer_runtime(runtime: int) -> None:
    validate_runtime(runtime)


def validate_timer_schedule(
    days_mask: int,
    start_times: list[int],
    runtime: int,
) -> None:
    validate_day_mask(days_mask)
    validate_start_times(start_times)
    validate_runtime(runtime)


#
# Cycling validation
#

def validate_cycling_schedule(
    start1: int,
    end1: int,
    start2: int,
    end2: int,
    runtime: int,
    soak: int,
) -> None:

    for value in (
        start1,
        end1,
        start2,
        end2,
    ):
        validate_seconds(value)

    validate_runtime(runtime)
    validate_runtime(soak)


#
# BLE payload validation
#

def validate_payload_size(
    payload: bytes,
    expected: int,
) -> None:
    if len(payload) != expected:
        raise ValidationError(
            f"Expected {expected} bytes "
            f"received {len(payload)}."
        )


def validate_notification(
    payload: bytes,
    minimum: int,
) -> None:
    if len(payload) < minimum:
        raise ValidationError(
            "Notification payload too short."
        )


#
# Battery validation
#

def validate_battery(level: int) -> None:
    if not 0 <= level <= 100:
        raise ValidationError(
            "Battery percentage must be 0-100."
        )


#
# Convenience predicates
#

def is_valid_runtime(seconds: int) -> bool:
    try:
        validate_runtime(seconds)
        return True
    except ValidationError:
        return False


def is_valid_time(seconds: int) -> bool:
    try:
        validate_seconds(seconds)
        return True
    except ValidationError:
        return False


def is_valid_day_mask(mask: int) -> bool:
    try:
        validate_day_mask(mask)
        return True
    except ValidationError:
        return False


def is_valid_zone(zone: int) -> bool:
    return zone in VALID_ZONES


#
# Generic assertions
#

def require(
    condition: bool,
    message: str,
) -> None:
    """
    Raise ValidationError when condition is False.

    Useful inside parser and packet builders.
    """

    if not condition:
        raise ValidationError(message)