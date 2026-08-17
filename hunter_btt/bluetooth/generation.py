"""Hunter BTT generation detection based on the Android reference logic."""

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
    generation: HunterGeneration
    zone_count: int
    service_uuid: str | None = None


FIRST_SERVICE_UUID = "0000fcc0-0000-1000-8000-00805f9b34fb"
SECOND_SERVICE_UUID = "0000ff80-0000-1000-8000-00805f9b34fb"
COMMAND_UUID = "0000ff83-0000-1000-8000-00805f9b34fb"


def _android_generation_from_name(device_name: str | None) -> HunterGeneration:
    """Mirror AisWrapper.connect(): startsWith('BTT') => First."""
    name = (device_name or "").strip().upper()
    if name.startswith("BTT"):
        return HunterGeneration.FIRST
    return HunterGeneration.SECOND


def normalize_android_device_name(device_name: str | None) -> str:
    """Recover the advertised BTT name when HA prepends its friendly label.

    AisWrapper receives a BTT-prefixed device identifier. HA can expose the
    same device as 'Hunter BTT CBBB4'. This normalization does not change the
    Android rule; it only removes the HA 'Hunter ' display prefix.
    """
    name = (device_name or "").strip()
    if name.upper().startswith("HUNTER BTT"):
        return name[7:].lstrip()
    return name


def detect_generation(
    service_uuids: set[str],
    device_name: str | None = None,
    characteristic_uuids: set[str] | None = None,
) -> HunterGeneration:
    """Use the Android name rule first, with GATT only as a consistency check."""
    normalized_name = normalize_android_device_name(device_name)

    # This is the manufacturer's application rule:
    # BTT* -> First; otherwise -> Second.
    generation = _android_generation_from_name(normalized_name)

    services = {str(uuid).strip().lower() for uuid in service_uuids}

    # If no usable BTT name is available, use GATT as a fallback only.
    if not normalized_name:
        if FIRST_SERVICE_UUID in services:
            return HunterGeneration.FIRST
        if SECOND_SERVICE_UUID in services:
            return HunterGeneration.SECOND
        return HunterGeneration.UNKNOWN

    return generation


def detect_zone_count(
    characteristic_uuids: set[str],
    generation: HunterGeneration,
) -> int:
    """Determine zone count from generation-specific evidence."""
    chars = {str(uuid).strip().lower() for uuid in characteristic_uuids}

    if generation is HunterGeneration.FIRST:
        # BTT100 is the confirmed first-generation test device and is one-zone.
        return 1

    if generation is HunterGeneration.SECOND:
        zone1 = "0000ff86-0000-1000-8000-00805f9b34fb" in chars
        zone2 = "0000ff8b-0000-1000-8000-00805f9b34fb" in chars
        if zone1 and zone2:
            return 2
        if zone1:
            return 1

    return 0
