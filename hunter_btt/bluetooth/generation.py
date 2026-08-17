"""Hunter BTT generation detection and capabilities."""

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
    """Capabilities discovered from GATT."""

    generation: HunterGeneration
    zone_count: int
    service_uuid: str | None = None


FIRST_SERVICE_UUID = "0000fcc0-0000-1000-8000-00805f9b34fb"
SECOND_SERVICE_UUID = "0000ff80-0000-1000-8000-00805f9b34fb"
FF83_UUID = "0000ff83-0000-1000-8000-00805f9b34fb"

# The known test controller is a BTT100.  It is first-generation even
# though its GATT database contains the FF80 service and an FF83
# characteristic.  FF83 presence alone therefore cannot identify
# second-generation hardware.
BTT100_NAMES = frozenset(
    {
        "btt100",
        "hunter btt100",
    }
)


def detect_generation(
    service_uuids: set[str],
    characteristic_uuids: set[str] | None = None,
    device_name: str | None = None,
) -> HunterGeneration:
    """Detect generation from identity and discovered GATT profile."""

    services = {str(uuid).lower() for uuid in service_uuids}
    characteristics = {
        str(uuid).lower()
        for uuid in (characteristic_uuids or set())
    }
    name = (device_name or "").strip().lower()

    # FCC0 is the established first-generation service.
    if FIRST_SERVICE_UUID in services:
        return HunterGeneration.FIRST

    if SECOND_SERVICE_UUID in services:
        # BTT100 is explicitly known to be first generation.
        if name in BTT100_NAMES:
            return HunterGeneration.FIRST

        # For other FF80 devices, only select the second-generation
        # transaction family when FF83 is actually present.
        if FF83_UUID in characteristics:
            return HunterGeneration.SECOND

    return HunterGeneration.UNKNOWN


def detect_zone_count(
    characteristic_uuids: set[str],
    generation: HunterGeneration,
) -> int:
    """Determine the currently proven zone count."""

    normalized = {str(uuid).lower() for uuid in characteristic_uuids}

    if generation is HunterGeneration.FIRST:
        return 1

    if generation is HunterGeneration.SECOND:
        zone1 = (
            "0000ff86-0000-1000-8000-00805f9b34fb"
            in normalized
        )
        zone2 = (
            "0000ff8b-0000-1000-8000-00805f9b34fb"
            in normalized
        )

        if zone1 and zone2:
            return 2
        if zone1:
            return 1

    return 0
