"""
Schedule model and helpers for the Hunter BTT201.

This module provides a higher-level abstraction over the raw protocol
packet builders. Home Assistant entities should manipulate these objects
rather than constructing protocol packets directly.

Flow:

    Number/Text/Switch Entities
            │
            ▼
      TimerSchedule/CyclingSchedule
            │
            ▼
     packets.build_*()
            │
            ▼
         BLE Characteristic
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import time
from typing import Final

MAX_RUNTIME: Final = 3600

DAY_ORDER: Final = (
    "mon",
    "tue",
    "wed",
    "thu",
    "fri",
    "sat",
    "sun",
)


#
# Time helpers
#

def time_to_seconds(value: time | None) -> int:
    if value is None:
        return -1

    return (
        value.hour * 3600
        + value.minute * 60
        + value.second
    )


def seconds_to_time(seconds: int) -> time | None:
    if seconds < 0:
        return None

    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60

    return time(hour=h, minute=m, second=s)


#
# Day helpers
#

def days_to_mask(days: list[str]) -> int:
    mask = 0

    for index, name in enumerate(DAY_ORDER):
        if name in days:
            mask |= 1 << index

    return mask


def mask_to_days(mask: int) -> list[str]:
    return [
        day
        for index, day in enumerate(DAY_ORDER)
        if mask & (1 << index)
    ]


#
# Timer schedule
#

@dataclass(slots=True)
class TimerSchedule:
    enabled: bool = False

    days: list[str] = field(default_factory=list)

    start_times: list[time | None] = field(
        default_factory=lambda: [
            None,
            None,
            None,
            None,
        ]
    )

    runtime: int = 600

    @property
    def day_mask(self) -> int:
        return days_to_mask(self.days)

    @property
    def active(self) -> bool:
        return (
            self.enabled
            and bool(self.days)
            and any(t is not None for t in self.start_times)
        )

    def validate(self) -> None:
        if len(self.start_times) != 4:
            raise ValueError("Exactly four start times required")

        if not 0 <= self.runtime <= MAX_RUNTIME:
            raise ValueError("Runtime exceeds maximum")

    def protocol_start_times(self) -> tuple[int, int, int, int]:
        self.validate()

        return tuple(
            time_to_seconds(t)
            for t in self.start_times
        )

    def copy(self) -> "TimerSchedule":
        return TimerSchedule(
            enabled=self.enabled,
            days=self.days.copy(),
            start_times=self.start_times.copy(),
            runtime=self.runtime,
        )


#
# Cycling schedule
#

@dataclass(slots=True)
class CyclingSchedule:
    enabled: bool = False

    days: list[str] = field(default_factory=list)

    start1: time | None = None
    end1: time | None = None

    start2: time | None = None
    end2: time | None = None

    runtime: int = 300
    soak: int = 300

    @property
    def day_mask(self) -> int:
        return days_to_mask(self.days)

    @property
    def active(self) -> bool:
        return (
            self.enabled
            and bool(self.days)
            and self.start1 is not None
            and self.end1 is not None
        )

    def validate(self) -> None:
        if not 0 <= self.runtime <= MAX_RUNTIME:
            raise ValueError("Runtime exceeds maximum")

        if self.soak < 0:
            raise ValueError("Invalid soak time")

    def protocol_values(self) -> tuple[int, ...]:
        self.validate()

        return (
            time_to_seconds(self.start1),
            time_to_seconds(self.end1),
            time_to_seconds(self.start2),
            time_to_seconds(self.end2),
            self.runtime,
            self.soak,
        )

    def copy(self) -> "CyclingSchedule":
        return CyclingSchedule(
            enabled=self.enabled,
            days=self.days.copy(),
            start1=self.start1,
            end1=self.end1,
            start2=self.start2,
            end2=self.end2,
            runtime=self.runtime,
            soak=self.soak,
        )


#
# Zone configuration
#

@dataclass(slots=True)
class ZoneSchedule:
    zone: int

    timer: TimerSchedule = field(default_factory=TimerSchedule)

    cycling: CyclingSchedule = field(default_factory=CyclingSchedule)

    manual_runtime: int = 600

    @property
    def has_schedule(self) -> bool:
        return (
            self.timer.active
            or self.cycling.active
        )

    def validate(self) -> None:
        if self.zone not in (1, 2):
            raise ValueError("Zone must be 1 or 2")

        if not 0 <= self.manual_runtime <= MAX_RUNTIME:
            raise ValueError("Invalid manual runtime")

        self.timer.validate()
        self.cycling.validate()