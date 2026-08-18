"""Hunter BTT advertisement filtering.

This module intentionally does not decide first/second generation. The
Android code first finds a BLE device, then initializes the protocol objects
against the connected GATT service. We mirror that separation here.
"""

from __future__ import annotations

from homeassistant.components.bluetooth import BluetoothServiceInfoBleak

FIRST_SERVICE_UUID = "0000fcc0-0000-1000-8000-00805f9b34fb"
SECOND_SERVICE_UUID = "0000ff80-0000-1000-8000-00805f9b34fb"

_HUNTER_MARKERS = ("hunter", "btt")


def _norm(value: str | None) -> str:
    return (value or "").strip().lower()


def discovery_name(info: BluetoothServiceInfoBleak) -> str:
    """Return the best available advertised/device name."""
    return (
        _norm(getattr(info, "local_name", None))
        or _norm(getattr(info, "name", None))
        or _norm(getattr(info.device, "name", None))
    )


def is_hunter_btt(info: BluetoothServiceInfoBleak) -> bool:
    """Identify a Hunter candidate without making a protocol decision."""
    services = {_norm(uuid) for uuid in info.service_uuids}

    if FIRST_SERVICE_UUID in services or SECOND_SERVICE_UUID in services:
        return True

    name = discovery_name(info)
    return any(marker in name for marker in _HUNTER_MARKERS)


def describe_discovery(info: BluetoothServiceInfoBleak) -> dict[str, object]:
    """Return diagnostic discovery data."""
    return {
        "address": info.address,
        "name": getattr(info, "name", None),
        "local_name": getattr(info, "local_name", None),
        "service_uuids": sorted(info.service_uuids),
        "connectable": info.connectable,
        "rssi": info.rssi,
    }
