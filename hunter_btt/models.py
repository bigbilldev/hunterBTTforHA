"""Shared runtime state for the Hunter BTT integration."""

from __future__ import annotations

from typing import Any


class HunterState(dict[str, Any]):
    """Dictionary-backed coordinator state with typed convenience accessors."""

    def __init__(self, initial: dict[str, Any] | None = None) -> None:
        super().__init__(
            battery=None,
            running=False,
            active_zone=0,
            remaining_seconds=0,
            protocol_initialized=False,
            zones={1: {"runtime": 600}, 2: {"runtime": 600}},
        )
        if initial:
            self.update(initial)
            self.setdefault("zones", {1: {"runtime": 600}, 2: {"runtime": 600}})

    @property
    def battery(self) -> int | None:
        value = self.get("battery")
        return int(value) if value is not None else None

    @property
    def active_zone(self) -> int | None:
        value = self.get("active_zone")
        return int(value) if value else None

    @property
    def remaining_seconds(self) -> int:
        return int(self.get("remaining_seconds", 0) or 0)

    @property
    def running(self) -> bool:
        return bool(self.get("running", False))
