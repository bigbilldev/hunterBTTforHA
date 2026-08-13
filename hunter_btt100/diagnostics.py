"""
Diagnostics support for the Hunter BTT201 integration.

This module provides:

- Home Assistant diagnostics download support
- Device information
- Connection status
- Protocol state
- Raw BLE cache (redacted)
- Coordinator state

See:
https://developers.home-assistant.io/docs/core/integration_diagnostics/
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from homeassistant.components.diagnostics import (
    async_redact_data,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN

#
# Values that should never appear in diagnostics
#

TO_REDACT = {
    "address",
    "mac",
    "mac_address",
    "identifier",
    "serial",
    "passcode",
    "password",
    "token",
    "key",
}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> dict[str, Any]:
    """
    Return diagnostics for a config entry.
    """

    coordinator = hass.data[DOMAIN][entry.entry_id]

    manager = coordinator.manager

    diagnostics: dict[str, Any] = {
        "integration": DOMAIN,
        "config_entry": async_redact_data(
            dict(entry.data),
            TO_REDACT,
        ),
        "options": async_redact_data(
            dict(entry.options),
            TO_REDACT,
        ),
        "device": await _device(manager),
        "connection": await _connection(manager),
        "coordinator": await _coordinator(
            coordinator,
        ),
        "cache": await _cache(manager),
    }

    return diagnostics


#
# Device
#

async def _device(manager) -> dict[str, Any]:

    info = {
        "connected": manager.connected,
        "name": getattr(
            manager,
            "name",
            None,
        ),
        "model": getattr(
            manager,
            "model",
            None,
        ),
        "manufacturer": getattr(
            manager,
            "manufacturer",
            None,
        ),
        "firmware": getattr(
            manager,
            "firmware_version",
            None,
        ),
    }

    return info


#
# Connection
#

async def _connection(manager) -> dict[str, Any]:

    connection = {
        "connected": manager.connected,
        "address": getattr(
            manager,
            "address",
            None,
        ),
        "last_rssi": getattr(
            manager,
            "rssi",
            None,
        ),
        "last_seen": getattr(
            manager,
            "last_seen",
            None,
        ),
    }

    return async_redact_data(
        connection,
        TO_REDACT,
    )


#
# Coordinator
#

async def _coordinator(
    coordinator,
) -> dict[str, Any]:

    return {
        "last_update_success":
            coordinator.last_update_success,

        "available":
            coordinator.available,

        "update_interval":
            str(coordinator.update_interval),

        "last_exception":
            (
                repr(coordinator.last_exception)
                if coordinator.last_exception
                else None
            ),

        "state":
            deepcopy(
                coordinator.data,
            ),
    }


#
# BLE cache
#

async def _cache(
    manager,
) -> dict[str, Any]:

    if not hasattr(manager, "cache"):
        return {}

    cache = {}

    for uuid, value in manager.cache.items():

        if isinstance(value, bytes):

            cache[uuid] = value.hex()

        else:

            cache[uuid] = deepcopy(value)

    return cache


#
# Extra helper
#

async def async_get_device_diagnostics(
    hass: HomeAssistant,
    entry: ConfigEntry,
    device,
) -> dict[str, Any]:
    """
    Optional per-device diagnostics.

    Currently identical to the config entry diagnostics.
    """

    return await async_get_config_entry_diagnostics(
        hass,
        entry,
    )