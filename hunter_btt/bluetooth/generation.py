"""Hunter BTT generation detection and capabilities."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from collections.abc import Iterable


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


def _normalize_uuids(values: Iterable[object] | None) -> set[str]:
    """Normalize a collection of UUID-like values.

    This function deliberately handles sets/lists/tuples and never calls
    string methods on the collection itself.
    """
    if values is None:
        return set()

    return {
        str(value).strip().lower()
        for value in values
    }


def detect_generation(
    service_uuids: Iterable[object],
    device_name: str | None = None,
    characteristic_uuids: Iterable[object] | None = None,
) -> HunterGeneration:
    """Detect the Hunter protocol generation.

    BTT100 is known to be first-generation.  Its observed GATT database can
    contain FF80 and FF83, so FF80/FF83 presence must not by itself classify
    it as second-generation.

    The Android reference also uses a BTT-prefixed device name as a
    first-generation signal.  FCC0 is an explicit first-generation service.
    FF80 is otherwise treated as second-generation.
    """
    services = _normalize_uuids(service_uuids)
    _ = _normalize_uuids(characteristic_uuids)

    name = (device_name or "").strip().upper()

    if name.startswith("BTT"):
        return HunterGeneration.FIRST

    if FIRST_SERVICE_UUID in services:
        return HunterGeneration.FIRST

    if SECOND_SERVICE_UUID in services:
        return HunterGeneration.SECOND

    return HunterGeneration.UNKNOWN


def detect_zone_count(
    characteristic_uuids: Iterable[object],
    generation: HunterGeneration,
) -> int:
    """Determine the currently proven zone count."""
    characteristics = _normalize_uuids(characteristic_uuids)

    if generation is HunterGeneration.FIRST:
        # The current proven first-generation implementation is one-zone.
        return 1

    if generation is HunterGeneration.SECOND:
        zone1 = "0000ff86-0000-1000-8000-00805f9b34fb" in characteristics
        zone2 = "0000ff8b-0000-1000-8000-00805f9b34fb" in characteristics

        if zone1 and zone2:
            return 2
        if zone1:
            return 1

    return 0
