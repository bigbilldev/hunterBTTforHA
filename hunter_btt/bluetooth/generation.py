"""Hunter BTT generation detection based on the Android reference logic."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

# Public UUID constants retained here for compatibility with config_flow and
# manager.py.  Protocol UUIDs are normalized to lowercase.
FIRST_SERVICE_UUID = "0000fcc0-0000-1000-8000-00805f9b34fb"
SECOND_SERVICE_UUID = "0000ff80-0000-1000-8000-00805f9b34fb"
COMMAND_UUID = "0000ff83-0000-1000-8000-00805f9b34fb"
FCC0_SERVICE_UUID = FIRST_SERVICE_UUID


class HunterGeneration(str, Enum):
    """Hunter BLE protocol generation."""

    FIRST = "first"
    SECOND = "second"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class HunterCapabilities:
    """Capabilities discovered from the controller."""

    generation: HunterGeneration
    zone_count: int
    service_uuid: str | None = None


def _normalize_name(device_name: str | None) -> str:
    name = (device_name or "").strip()
    # HA commonly presents this device as "Hunter BTT CBBB4", while the
    # Android wrapper receives the BTT-prefixed local name.
    if name.upper().startswith("HUNTER BTT"):
        return name[7:].lstrip()
    return name


def detect_generation(
    service_uuids: set[str] | None = None,
    device_name: str | None = None,
    characteristic_uuids: set[str] | None = None,
) -> HunterGeneration:
    """Mirror AisWrapper generation selection.

    Android's rule is:
        device name starts with "BTT" -> First
        otherwise -> Second

    GATT is only a fallback when no usable device name is available.
    """
    name = _normalize_name(device_name)

    if name.upper().startswith("BTT"):
        return HunterGeneration.FIRST

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
    """Compatibility validator for config flow.

    This validates the expected service family after generation has been
    selected; it does not change the Android name-based generation decision.
    """
    services = {
        str(uuid).strip().lower()
        for uuid in (service_uuids or set())
    }

    if generation is HunterGeneration.FIRST:
        return FIRST_SERVICE_UUID in services or SECOND_SERVICE_UUID in services

    if generation is HunterGeneration.SECOND:
        return SECOND_SERVICE_UUID in services

    return False


def normalize_android_device_name(device_name: str | None) -> str:
    """Return the BTT-prefixed name used by the Android generation rule."""
    return _normalize_name(device_name)
