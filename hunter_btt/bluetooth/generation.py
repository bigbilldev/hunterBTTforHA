"""Hunter BTT generation detection matching the Android application."""

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


def normalize_android_device_name(device_name: str | None) -> str:
    """Convert HA's friendly Hunter name to the Android local-name form.

    The Android wrapper classifies a device as first generation when the
    device name starts with 'BTT'. HA may expose the same device as
    'Hunter BTT CBBB4', so remove only that HA-added prefix.
    """
    name = (device_name or "").strip()
    upper = name.upper()

    if upper.startswith("HUNTER BTT"):
        return name[len("HUNTER "):].lstrip()

    return name


def detect_generation(
    service_uuids: set[str] | None = None,
    device_name: str | None = None,
    characteristic_uuids: set[str] | None = None,
) -> HunterGeneration:
    """Mirror AisWrapper: BTT-prefixed name means first generation."""
    normalized_name = normalize_android_device_name(device_name)

    # This is the primary and authoritative generation selector.
    if normalized_name.upper().startswith("BTT"):
        return HunterGeneration.FIRST

    # Android treats non-BTT named devices as second generation.
    if normalized_name:
        return HunterGeneration.SECOND

    # Only if there is no usable name do we use GATT as a fallback.
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
    """Determine currently proven zone count."""
    chars = {
        str(uuid).strip().lower()
        for uuid in (characteristic_uuids or set())
    }

    if generation is HunterGeneration.FIRST:
        # Confirmed BTT100 test device.
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
    """Compatibility check used by config flow."""
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
