"""Hunter BTT generation detection and protocol constants."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

FIRST_SERVICE_UUID = "0000fcc0-0000-1000-8000-00805f9b34fb"
SECOND_SERVICE_UUID = "0000ff80-0000-1000-8000-00805f9b34fb"
FCC0_SERVICE_UUID = FIRST_SERVICE_UUID
COMMAND_UUID = "0000ff83-0000-1000-8000-00805f9b34fb"


class HunterGeneration(str, Enum):
    FIRST = "first"
    SECOND = "second"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class HunterCapabilities:
    generation: HunterGeneration
    zone_count: int
    service_uuid: str | None = None


def normalize_android_device_name(device_name: str | None) -> str:
    name = (device_name or "").strip()
    if name.upper().startswith("HUNTER BTT"):
        return name[len("HUNTER "):].lstrip()
    return name


def detect_generation(
    service_uuids: set[str] | None = None,
    device_name: str | None = None,
    characteristic_uuids: set[str] | None = None,
) -> HunterGeneration:
    """Determine generation from GATT service identity first.

    GATT services are authoritative when available.  Device names are only
    a fallback because Android/HA names can be misleading or stale.
    """
    services = {
        str(uuid).strip().lower()
        for uuid in (service_uuids or set())
    }

    # Authoritative protocol identity.
    if SECOND_SERVICE_UUID in services:
        return HunterGeneration.SECOND

    if FIRST_SERVICE_UUID in services:
        return HunterGeneration.FIRST

    # If services are unavailable, characteristic sets can still provide
    # a strong protocol identity.
    chars = {
        str(uuid).strip().lower()
        for uuid in (characteristic_uuids or set())
    }

    second_markers = {
        COMMAND_UUID,
        "0000ff82-0000-1000-8000-00805f9b34fb",
        "0000ff86-0000-1000-8000-00805f9b34fb",
    }
    first_markers = {
        "0000fcd9-0000-1000-8000-00805f9b34fb",
        "0000fceb-0000-1000-8000-00805f9b34fb",
    }

    if second_markers & chars:
        return HunterGeneration.SECOND

    if first_markers & chars:
        return HunterGeneration.FIRST

    # Last-resort Android naming fallback.
    normalized_name = normalize_android_device_name(device_name)
    if normalized_name.upper().startswith("BTT"):
        return HunterGeneration.FIRST

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
        return FIRST_SERVICE_UUID in services

    if generation is HunterGeneration.SECOND:
        return SECOND_SERVICE_UUID in services

    return False
