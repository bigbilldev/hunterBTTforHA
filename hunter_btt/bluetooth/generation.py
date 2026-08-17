"""Hunter BTT protocol generation and capability detection."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable


class HunterGeneration(str, Enum):
    """Hunter protocol generation."""

    FIRST = "first"
    SECOND = "second"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class HunterCapabilities:
    """Capabilities established from protocol identification."""

    generation: HunterGeneration
    zone_count: int
    service_uuid: str | None = None


FIRST_SERVICE_UUID = "0000fcc0-0000-1000-8000-00805f9b34fb"
SECOND_SERVICE_UUID = "0000ff80-0000-1000-8000-00805f9b34fb"

SECOND_ZONE1_CONFIG_UUID = "0000ff86-0000-1000-8000-00805f9b34fb"
SECOND_ZONE2_CONFIG_UUID = "0000ff8b-0000-1000-8000-00805f9b34fb"


def _normalize(values: Iterable[object] | None) -> set[str]:
    """Normalize UUID-like collections safely."""
    if values is None:
        return set()
    return {str(value).strip().lower() for value in values}


def detect_generation(
    service_uuids: Iterable[object],
    device_name: str | None = None,
    characteristic_uuids: Iterable[object] | None = None,
) -> HunterGeneration:
    """Determine generation using the proven device-name rule.

    The decompiled Android implementation classifies devices whose name
    starts with BTT as first generation. GATT UUIDs are then used as
    validation evidence, not as a reason to reclassify a BTT device.
    """
    services = _normalize(service_uuids)
    name = (device_name or "").strip().upper()

    if name.startswith("BTT"):
        return HunterGeneration.FIRST

    if SECOND_SERVICE_UUID in services:
        return HunterGeneration.SECOND

    if FIRST_SERVICE_UUID in services:
        return HunterGeneration.FIRST

    return HunterGeneration.UNKNOWN


def validate_generation_services(
    generation: HunterGeneration,
    service_uuids: Iterable[object],
) -> bool:
    """Validate that the expected GATT service exists for a generation."""
    services = _normalize(service_uuids)

    if generation is HunterGeneration.FIRST:
        return FIRST_SERVICE_UUID in services

    if generation is HunterGeneration.SECOND:
        return SECOND_SERVICE_UUID in services

    return False


def detect_zone_count(
    characteristic_uuids: Iterable[object],
    generation: HunterGeneration,
) -> int:
    """Determine the currently supportable zone count conservatively."""
    characteristics = _normalize(characteristic_uuids)

    # BTT100 is confirmed first-generation and single-zone.
    # Do not infer additional zones from incidental FFxx UUIDs.
    if generation is HunterGeneration.FIRST:
        return 1

    if generation is HunterGeneration.SECOND:
        if (
            SECOND_ZONE1_CONFIG_UUID in characteristics
            and SECOND_ZONE2_CONFIG_UUID in characteristics
        ):
            return 2

        if SECOND_ZONE1_CONFIG_UUID in characteristics:
            return 1

    return 0
