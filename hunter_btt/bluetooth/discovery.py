"""Generation-agnostic Hunter BTT Bluetooth discovery."""

from __future__ import annotations

from homeassistant.components.bluetooth import BluetoothServiceInfoBleak

# Both protocol families are accepted at discovery time. This is NOT a
# generation decision; generation.py makes that decision after connection.
HUNTER_SERVICE_UUIDS = frozenset(
    {
        "0000ff80-0000-1000-8000-00805f9b34fb",
        "0000fcc0-0000-1000-8000-00805f9b34fb",
    }
)

HUNTER_NAME_MARKERS = (
    "hunter",
    "btt",
)


def _normalized(value: str | None) -> str:
    return (value or "").strip().lower()


def is_hunter_btt(
    discovery: BluetoothServiceInfoBleak,
) -> bool:
    """Return True when an advertisement is plausibly a Hunter BTT.

    Do not inspect FF82/FF83 properties here and do not decide generation
    here. Those operations require a connection and belong to protocol
    detection after discovery.
    """
    advertised_services = {
        _normalized(uuid)
        for uuid in discovery.service_uuids
    }

    if advertised_services & HUNTER_SERVICE_UUIDS:
        return True

    # HA's BluetoothServiceInfoBleak normally exposes name; local_name is
    # included when available on the object supplied by the scanner.
    names = {
        _normalized(getattr(discovery, "name", None)),
        _normalized(getattr(discovery, "service_name", None)),
        _normalized(getattr(discovery, "service_data", None).__class__.__name__),
    }

    # Use the actual advertised/device name when present. Do not require a
    # particular model suffix because BT100/BTT variants may advertise
    # differently.
    device_name = _normalized(
        getattr(discovery, "name", None)
        or getattr(getattr(discovery, "device", None), "name", None)
        or getattr(discovery, "local_name", None)
    )

    if any(marker in device_name for marker in HUNTER_NAME_MARKERS):
        return True

    return False
