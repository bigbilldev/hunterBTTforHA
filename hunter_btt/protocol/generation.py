"""Hunter BTT generation detection and capabilities."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class HunterGeneration(str, Enum):
    """Hunter BLE protocol generation."""

    FIRST = "first"
    SECOND = "second"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class HunterCapabilities:
    """Capabilities discovered from GATT."""

    generation: HunterGeneration
    zone_count: int
    service_uuid: str | None = None


FIRST_SERVICE_UUID = "0000fcc0-0000-1000-8000-00805f9b34fb"
SECOND_SERVICE_UUID = "0000ff80-0000-1000-8000-00805f9b34fb"


def detect_generation(service_uuids: set[str]) -> HunterGeneration:
    """Detect generation from discovered GATT services."""

    normalized = {str(uuid).lower() for uuid in service_uuids}

    if FIRST_SERVICE_UUID in normalized:
        return HunterGeneration.FIRST

    if SECOND_SERVICE_UUID in normalized:
        return HunterGeneration.SECOND

    return HunterGeneration.UNKNOWN


def detect_zone_count(
    characteristic_uuids: set[str],
    generation: HunterGeneration,
) -> int:
    """Determine the currently proven zone count.

    First-generation Zone 2 mapping is deliberately not guessed yet.
    The tested BTT100 is therefore exposed as one zone.

    Second-generation Zone 2 is identified by FF8B.
    """

    normalized = {str(uuid).lower() for uuid in characteristic_uuids}

    if generation is HunterGeneration.FIRST:
        return 1

    if generation is HunterGeneration.SECOND:
        zone1 = "0000ff86-0000-1000-8000-00805f9b34fb" in normalized
        zone2 = "0000ff8b-0000-1000-8000-00805f9b34fb" in normalized

        if zone1 and zone2:
            return 2
        if zone1:
            return 1

    return 0
