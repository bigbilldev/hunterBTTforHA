"""Hunter BTT generation detection and conservative capabilities."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class HunterGeneration(str, Enum):
    FIRST = "first"
    SECOND = "second"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class HunterCapabilities:
    generation: HunterGeneration
    zone_count: int
    service_uuid: str | None = None


FIRST_SERVICE_UUID = "0000fcc0-0000-1000-8000-00805f9b34fb"
SECOND_SERVICE_UUID = "0000ff80-0000-1000-8000-00805f9b34fb"


def detect_generation(
    service_uuids: set[str],
    device_name: str | None = None,
    characteristic_uuids: set[str] | None = None,
) -> HunterGeneration:
    """Determine generation.

    The Android source identifies BTT-family devices as first generation.
    HA may expose a friendly name such as "Hunter BTT CBBB4", so BTT is
    deliberately matched anywhere in the name, not only at position zero.

    FF80/FF83 presence must not override that first-generation classification.
    """
    normalized = {str(uuid).strip().lower() for uuid in service_uuids}
    name = (device_name or "").strip().upper()

    if "BTT" in name:
        return HunterGeneration.FIRST

    if FIRST_SERVICE_UUID in normalized:
        return HunterGeneration.FIRST

    if SECOND_SERVICE_UUID in normalized:
        return HunterGeneration.SECOND

    return HunterGeneration.UNKNOWN


def detect_zone_count(
    characteristic_uuids: set[str],
    generation: HunterGeneration,
) -> int:
    """Return only currently proven zone counts."""
    normalized = {str(uuid).strip().lower() for uuid in characteristic_uuids}

    if generation is HunterGeneration.FIRST:
        # BTT100 is confirmed first-generation/single-zone.
        return 1

    if generation is HunterGeneration.SECOND:
        zone1 = "0000ff86-0000-1000-8000-00805f9b34fb" in normalized
        zone2 = "0000ff8b-0000-1000-8000-00805f9b34fb" in normalized
        if zone1 and zone2:
            return 2
        if zone1:
            return 1

    return 0
