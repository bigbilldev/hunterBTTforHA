"""Hunter BTT Bluetooth discovery helpers.

The Android application identifies Hunter controllers from the advertised
FCC0/FF80 services. Home Assistant must not require the advertisement to be
marked connectable because a remote Bluetooth proxy may provide the
advertisement without exposing its connectability flag.

Generation is intentionally not decided here.
"""

from __future__ import annotations

from homeassistant.components.bluetooth import BluetoothServiceInfoBleak

FIRST_SERVICE_UUID = "0000fcc0-0000-1000-8000-00805f9b34fb"
SECOND_SERVICE_UUID = "0000ff80-0000-1000-8000-00805f9b34fb"

def _norm(value: str | None) -> str:
    return (value or "").strip().lower()

def advertised_service_uuids(info: BluetoothServiceInfoBleak) -> set[str]:
    return {_norm(uuid) for uuid in (info.service_uuids or ())}

def discovery_name(info: BluetoothServiceInfoBleak) -> str:
    return (
        _norm(getattr(info, "local_name", None))
        or _norm(getattr(info, "name", None))
        or _norm(getattr(info.device, "name", None))
    )

def is_hunter_btt(info: BluetoothServiceInfoBleak) -> bool:
    services = advertised_service_uuids(info)
    if FIRST_SERVICE_UUID in services or SECOND_SERVICE_UUID in services:
        return True

    name = discovery_name(info)
    return name.startswith("btt") or "hunter" in name

def describe_discovery(info: BluetoothServiceInfoBleak) -> dict[str, object]:
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
