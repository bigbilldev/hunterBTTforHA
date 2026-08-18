"""Hunter BTT Bluetooth discovery.

Discovery deliberately mirrors the Android discovery model:
- FCC0 identifies first-generation devices.
- FF80 identifies second-generation devices.
- A device name beginning with BTT is also a valid Hunter candidate.

Generation is NOT decided here; that happens after discovery/connection.
"""

from __future__ import annotations

from homeassistant.components.bluetooth import BluetoothServiceInfoBleak

FIRST_SERVICE_UUID = "0000fcc0-0000-1000-8000-00805f9b34fb"
SECOND_SERVICE_UUID = "0000ff80-0000-1000-8000-00805f9b34fb"

_HUNTER_NAME_PREFIXES = ("btt",)
_HUNTER_NAME_MARKERS = ("hunter",)


def _norm(value: str | None) -> str:
    return (value or "").strip().lower()


def discovery_name(info: BluetoothServiceInfoBleak) -> str:
    """Return the best name available from the advertisement."""
    return (
        _norm(getattr(info, "local_name", None))
        or _norm(getattr(info, "name", None))
        or _norm(getattr(info.device, "name", None))
    )


def advertised_service_uuids(info: BluetoothServiceInfoBleak) -> set[str]:
    """Return normalized advertised service UUIDs."""
    return {_norm(uuid) for uuid in (info.service_uuids or ())}


def is_hunter_btt(info: BluetoothServiceInfoBleak) -> bool:
    """Identify a Hunter candidate without connecting to it."""
    services = advertised_service_uuids(info)

    if FIRST_SERVICE_UUID in services or SECOND_SERVICE_UUID in services:
        return True

    name = discovery_name(info)
    if not name:
        return False

    return name.startswith(_HUNTER_NAME_PREFIXES) or any(
        marker in name for marker in _HUNTER_NAME_MARKERS
    )


def describe_discovery(info: BluetoothServiceInfoBleak) -> dict[str, object]:
    """Return complete advertisement diagnostics for troubleshooting."""
    return {
        "address": info.address,
        "name": getattr(info, "name", None),
        "local_name": getattr(info, "local_name", None),
        "service_uuids": sorted(advertised_service_uuids(info)),
        "connectable": bool(info.connectable),
        "rssi": info.rssi,
        "manufacturer_data": {
            str(key): bytes(value).hex()
            for key, value in (info.manufacturer_data or {}).items()
        },
        "service_data": {
            str(key): bytes(value).hex()
            for key, value in (info.service_data or {}).items()
        },
    }
