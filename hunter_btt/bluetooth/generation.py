"""Hunter BTT protocol generation detection."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class HunterGeneration(str, Enum):
    """Hunter protocol generation."""

    UNKNOWN = "unknown"
    FIRST = "first"
    SECOND = "second"


FCC0_SERVICE_UUID = "0000fcc0-0000-1000-8000-00805f9b34fb"
FF80_SERVICE_UUID = "0000ff80-0000-1000-8000-00805f9b34fb"
FF83_UUID = "0000ff83-0000-1000-8000-00805f9b34fb"


@dataclass(frozen=True, kw_only=True)
class HunterCapabilities:
    """Capabilities discovered for a Hunter controller."""

    generation: HunterGeneration
    zone_count: int
    service_uuid: str | None = None


def _normalize_uuid(value: object) -> str:
    """Normalize one UUID-like value."""
    return str(value).strip().lower()


def _normalize_set(values: object) -> set[str]:
    """Normalize a collection of UUID-like values."""
    if values is None:
        return set()

    if isinstance(values, str):
        return {_normalize_uuid(values)}

    try:
        return {
            _normalize_uuid(value)
            for value in values
        }
    except TypeError:
        return {_normalize_uuid(values)}


def detect_generation(
    service_uuids: object,
    characteristic_uuids: object | None = None,
    *,
    device_name: str | None = None,
) -> HunterGeneration:
    """Detect the Hunter protocol generation.

    BTT100 is a known first-generation controller.  It can expose the
    FF80 service and FF83 characteristic, but FF83 is not necessarily a
    writable command characteristic.  Therefore FF80/FF83 presence alone
    must not classify a device as second generation.

    The FCC0 service is an explicit first-generation marker.  A device
    named BTT/BTT100 is also treated as first generation when the FCC0
    service is not available.  Otherwise FF80 with a writable FF83 may be
    treated as second generation.
    """
    services = _normalize_set(service_uuids)
    characteristics = _normalize_set(characteristic_uuids)

    name = (device_name or "").strip().lower()

    if FCC0_SERVICE_UUID in services:
        return HunterGeneration.FIRST

    if name.startswith("btt100") or name == "btt":
        return HunterGeneration.FIRST

    if FF80_SERVICE_UUID in services:
        # Presence of FF83 is insufficient.  If no characteristic
        # properties are available here, retain the legacy-safe default.
        if FF83_UUID in characteristics:
            return HunterGeneration.SECOND

    return HunterGeneration.UNKNOWN


def detect_zone_count(
    characteristic_uuids: object,
    generation: HunterGeneration,
) -> int:
    """Determine the supported zone count conservatively."""
    characteristics = _normalize_set(characteristic_uuids)

    if generation is HunterGeneration.FIRST:
        return 1

    if generation is HunterGeneration.SECOND:
        # FF8B is the known second-zone configuration characteristic.
        if "0000ff8b-0000-1000-8000-00805f9b34fb" in characteristics:
            return 2
        return 1

    return 0
