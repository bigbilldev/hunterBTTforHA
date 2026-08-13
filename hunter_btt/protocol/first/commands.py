"""First-generation manual watering commands."""

from __future__ import annotations

from dataclasses import dataclass

from ..uuids import FIRST_D9_UUID, FIRST_EB_UUID
from .protocols import FirstD9, FirstEB


@dataclass(frozen=True, slots=True)
class FirstWrite:
    """A First-generation GATT write."""

    uuid: str
    payload: bytes


def build_manual_start(
    select_mode: int,
    runtime_seconds: int,
) -> FirstWrite:
    """Build the Android-equivalent manual start."""

    if runtime_seconds <= 0:
        raise ValueError("runtime must be greater than zero")

    if runtime_seconds % 60:
        raise ValueError(
            "First-generation manual runtime must be a whole number of minutes"
        )

    minute = runtime_seconds // 60

    if select_mode == 0:
        return FirstWrite(
            FIRST_D9_UUID,
            FirstD9(control=1, minute=minute).to_frame(),
        )

    if select_mode == 1:
        return FirstWrite(
            FIRST_EB_UUID,
            FirstEB(control=1, minute=minute).to_frame(),
        )

    raise ValueError(
        f"Unsupported First-generation selectMode: {select_mode}"
    )


def build_manual_stop(
    select_mode: int,
    minute: int,
) -> FirstWrite:
    """Build the Android-equivalent manual stop."""

    if not 0 <= minute <= 0xFFFF:
        raise ValueError("minute out of range")

    if select_mode == 0:
        return FirstWrite(
            FIRST_D9_UUID,
            FirstD9(control=0, minute=minute).to_frame(),
        )

    if select_mode == 1:
        return FirstWrite(
            FIRST_EB_UUID,
            FirstEB(control=0, minute=minute).to_frame(),
        )

    raise ValueError(
        f"Unsupported First-generation selectMode: {select_mode}"
    )
