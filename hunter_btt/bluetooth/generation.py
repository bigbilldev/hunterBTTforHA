"""Hunter BTT protocol generation and conservative capabilities."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from collections.abc import Iterable


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
ZONE1_CONFIG_UUID = "0000ff86-0000-1000-8000-00805f9b34fb"
ZONE2_CONFIG_UUID = "0000ff8b-0000-1000-8000-00805f9b34fb"


def _normalize(values: Iterable[object] | None) -> set[str]:
    if values is None:
        return set()
    return {str(value).strip().lower() for value in values}


def detect_generation(
    service_uuids: Iterable[object],
    device_name: str | None = None,
    characteristic_uuids: Iterable[object] | None = None,
) -> HunterGeneration:
    """Use the Android-derived BTT-name rule before GATT heuristics.

    A name such as 'Hunter BTT CBBB4' is First generation. FF80/FF83
    presence must not override that result.
    """
    services = _normalize(service_uuids)
    name = (device_name or "").strip().upper()

    if "BTT" in name:
        return HunterGeneration.FIRST

    if SECOND_SERVICE_UUID in services:
        return HunterGeneration.SECOND

    if FIRST_SERVICE_UUID in services:
        return HunterGeneration.FIRST

    return HunterGeneration.UNKNOWN


def detect_zone_count(
    characteristic_uuids: Iterable[object],
    generation: HunterGeneration,
) -> int:
    """Return only zones supported by the currently proven protocol."""
    chars = _normalize(characteristic_uuids)

    if generation is HunterGeneration.FIRST:
        # BTT100 is proven single-zone. Do not infer Zone 2 from FF8B.
        return 1

    if generation is HunterGeneration.SECOND:
        if ZONE1_CONFIG_UUID in chars and ZONE2_CONFIG_UUID in chars:
            return 2
        if ZONE1_CONFIG_UUID in chars:
            return 1

    return 0
