"""Hunter BTT generation and capability detection from discovered GATT."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

FIRST_SERVICE_UUID = "0000fcc0-0000-1000-8000-00805f9b34fb"
SECOND_SERVICE_UUID = "0000ff80-0000-1000-8000-00805f9b34fb"
FCC0_SERVICE_UUID = FIRST_SERVICE_UUID
COMMAND_UUID = "0000ff83-0000-1000-8000-00805f9b34fb"
FF82_UUID = "0000ff82-0000-1000-8000-00805f9b34fb"
FF86_UUID = "0000ff86-0000-1000-8000-00805f9b34fb"
FF8B_UUID = "0000ff8b-0000-1000-8000-00805f9b34fb"


class HunterGeneration(str, Enum):
    """Supported protocol generations."""

    FIRST = "first"
    SECOND = "second"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class HunterCapabilities:
    """Capabilities discovered from the connected GATT database."""

    generation: HunterGeneration
    zone_count: int
    service_uuid: str | None = None


def normalize_android_device_name(device_name: str | None) -> str:
    """Normalize the name in the same spirit as the Android wrapper."""
    name = (device_name or "").strip()
    if name.upper().startswith("HUNTER BTT"):
        return name[len("HUNTER "):].lstrip()
    return name


def detect_generation(
    service_uuids: set[str] | None = None,
    device_name: str | None = None,
    characteristic_uuids: set[str] | None = None,
) -> HunterGeneration:
    """Identify protocol from the connected GATT database.

    Service UUID is authoritative, matching the Android AisWrapper mapping:
    FCC0 -> First and FF80 -> Second. Characteristic markers are only a
    fallback for backends that expose characteristics without a service UUID.
    """
    services = {str(v).strip().lower() for v in (service_uuids or set())}
    chars = {str(v).strip().lower() for v in (characteristic_uuids or set())}

    if SECOND_SERVICE_UUID in services:
        return HunterGeneration.SECOND
    if FIRST_SERVICE_UUID in services:
        return HunterGeneration.FIRST

    if COMMAND_UUID in chars or FF82_UUID in chars or FF86_UUID in chars:
        return HunterGeneration.SECOND

    first_markers = {
        "0000fcd9-0000-1000-8000-00805f9b34fb",
        "0000fceb-0000-1000-8000-00805f9b34fb",
    }
    if chars & first_markers:
        return HunterGeneration.FIRST

    # Last-resort fallback only when GATT identity is unavailable.
    normalized = normalize_android_device_name(device_name)
    if normalized.upper().startswith("BTT"):
        return HunterGeneration.FIRST

    return HunterGeneration.UNKNOWN


def detect_zone_count(
    characteristic_uuids: set[str] | None,
    generation: HunterGeneration,
) -> int:
    """Determine zone count from actual GATT characteristics."""
    chars = {str(v).strip().lower() for v in (characteristic_uuids or set())}

    if generation is HunterGeneration.FIRST:
        # Android's first protocol exposes the FCC0 family as a single-zone
        # controller protocol.
        return 1

    if generation is HunterGeneration.SECOND:
        zone1 = FF86_UUID in chars
        zone2 = FF8B_UUID in chars
        if zone1 and zone2:
            return 2
        if zone1:
            return 1

    return 0


def validate_generation_services(
    generation: HunterGeneration,
    service_uuids: set[str] | None,
) -> bool:
    """Validate that the connected service matches the selected generation."""
    services = {str(v).strip().lower() for v in (service_uuids or set())}
    if generation is HunterGeneration.FIRST:
        return FIRST_SERVICE_UUID in services
    if generation is HunterGeneration.SECOND:
        return SECOND_SERVICE_UUID in services
    return False
