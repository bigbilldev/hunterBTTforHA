"""Hunter BTT protocol generation and capability detection."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable


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
SECOND_ZONE1_CONFIG_UUID = "0000ff86-0000-1000-8000-00805f9b34fb"
SECOND_ZONE2_CONFIG_UUID = "0000ff8b-0000-1000-8000-00805f9b34fb"


def _normalize(values: Iterable[object] | None) -> set[str]:
    """Normalize UUID-like collections safely."""
    if values is None:
        return set()
    return {str(value).strip().lower() for value in values}


def detect_generation(
    service_uuids: Iterable[object],
    device_name: str | None = None,
    characteristic_uuids: Iterable[object] | None = None,
) -> HunterGeneration:
    """Use the proven Android device-name rule."""
    services = _normalize(service_uuids)
    name = (device_name or "").strip().upper()

    # AisWrapper classifies BTT-named devices as First before GATT
    # protocol selection. FF80/FF83 must not override this.
    if name.startswith("BTT"):
        return HunterGeneration.FIRST

    if SECOND_SERVICE_UUID in services:
        return HunterGeneration.SECOND

    if FIRST_SERVICE_UUID in services:
        return HunterGeneration.FIRST

    return HunterGeneration.UNKNOWN


def validate_generation_services(
    generation: HunterGeneration,
    service_uuids: Iterable[object],
) -> bool:
    """Validate the service expected by the selected protocol family."""
    services = _normalize(service_uuids)

    if generation is HunterGeneration.FIRST:
        return FIRST_SERVICE_UUID in services

    if generation is HunterGeneration.SECOND:
        return SECOND_SERVICE_UUID in services

    return False


def detect_zone_count(
    characteristic_uuids: Iterable[object],
    generation: HunterGeneration,
) -> int:
    """Determine currently supportable zone count conservatively."""
    characteristics = _normalize(characteristic_uuids)

    # The tested BTT100 is first-generation and one-zone. Do not infer
    # another zone merely from the presence of FF8B or other FFxx UUIDs.
    if generation is HunterGeneration.FIRST:
        return 1

    # Second_83 explicitly models both zones in the reference protocol.
    # Require both known zone configuration characteristics before exposing
    # two zones; otherwise expose only the proven zone 1.
    if generation is HunterGeneration.SECOND:
        if (
            SECOND_ZONE1_CONFIG_UUID in characteristics
            and SECOND_ZONE2_CONFIG_UUID in characteristics
        ):
            return 2
        if SECOND_ZONE1_CONFIG_UUID in characteristics:
            return 1

    return 0
