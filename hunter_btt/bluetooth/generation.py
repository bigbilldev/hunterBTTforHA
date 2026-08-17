"""Hunter BTT generation detection and capabilities.

Generation selection follows the decompiled Android application's rule:
the local device name beginning with ``BTT`` identifies first generation;
otherwise it is second generation. GATT service discovery is only a
fallback when no usable device name is available.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

FIRST_SERVICE_UUID = "0000fcc0-0000-1000-8000-00805f9b34fb"
SECOND_SERVICE_UUID = "0000ff80-0000-1000-8000-00805f9b34fb"
COMMAND_UUID = "0000ff83-0000-1000-8000-00805f9b34fb"
FCC0_SERVICE_UUID = FIRST_SERVICE_UUID


class HunterGeneration(str, Enum):
    FIRST = "first"
    SECOND = "second"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class HunterCapabilities:
    generation: HunterGeneration
    zone_count: int
    service_uuid: str | None = None


def _android_name(device_name: str | None) -> str:
    """Normalize HA's friendly 'Hunter BTT ...' name to Android's BTT name."""
    name = (device_name or "").strip()
    if name.upper().startswith("HUNTER BTT"):
        return name[7:].lstrip()
    return name


def detect_generation(
    service_uuids: set[str] | None = None,
    device_name: str | None = None,
    characteristic_uuids: set[str] | None = None,
) -> HunterGeneration:
    name = _android_name(device_name)

    # Android reference rule.
    if name.upper().startswith("BTT"):
        return HunterGeneration.FIRST

    # If a non-empty name exists, Android classifies it as second.
    if name:
        return HunterGeneration.SECOND

    services = {
        str(uuid).strip().lower()
        for uuid in (service_uuids or set())
    }
    if FIRST_SERVICE_UUID in services:
        return HunterGeneration.FIRST
    if SECOND_SERVICE_UUID in services:
        return HunterGeneration.SECOND
    return HunterGeneration.UNKNOWN


def detect_zone_count(
    characteristic_uuids: set[str] | None,
    generation: HunterGeneration,
) -> int:
    chars = {
        str(uuid).strip().lower()
        for uuid in (characteristic_uuids or set())
    }

    if generation is HunterGeneration.FIRST:
        return 1

    if generation is HunterGeneration.SECOND:
        zone1 = "0000ff86-0000-1000-8000-00805f9b34fb" in chars
        zone2 = "0000ff8b-0000-1000-8000-00805f9b34fb" in chars
        if zone1 and zone2:
            return 2
        if zone1:
            return 1

    return 0


def validate_generation_services(
    generation: HunterGeneration,
    service_uuids: set[str] | None,
) -> bool:
    services = {
        str(uuid).strip().lower()
        for uuid in (service_uuids or set())
    }
    if generation is HunterGeneration.FIRST:
        return (
            FIRST_SERVICE_UUID in services
            or SECOND_SERVICE_UUID in services
        )
    if generation is HunterGeneration.SECOND:
        return SECOND_SERVICE_UUID in services
    return False
