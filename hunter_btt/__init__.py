"""
Hunter BTT Home Assistant Integration.

This integration communicates directly with the Hunter BTT irrigation
controller over Bluetooth Low Energy (BLE).

Architecture

Home Assistant
        │
HunterDataUpdateCoordinator
        │
HunterBLEManager
        │
HunterTransactionEngine
        │
HunterConnection
        │
HunterBLEClient
        │
Hunter BTT
"""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .coordinator import HunterDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    Platform.SWITCH,
    Platform.BUTTON,
    Platform.NUMBER,
]


async def async_setup(
    hass: HomeAssistant,
    config: dict,
) -> bool:
    """
    YAML setup is not supported.

    Configuration is performed through the Config Flow.
    """
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> bool:
    """
    Set up a Hunter controller from a config entry.
    """

    coordinator = HunterDataUpdateCoordinator(
        hass,
        entry,
    )

    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = coordinator

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(
        entry,
        PLATFORMS,
    )

    entry.async_on_unload(
        entry.add_update_listener(
            async_reload_entry,
        )
    )

    _LOGGER.info(
        "Hunter BTT integration initialized (%s)",
        coordinator.address,
    )

    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> bool:
    """
    Unload a config entry.
    """

    unload_ok = await hass.config_entries.async_unload_platforms(
        entry,
        PLATFORMS,
    )

    if unload_ok:

        coordinator = hass.data[DOMAIN].pop(
            entry.entry_id,
            None,
        )

        if coordinator is not None:
            await coordinator.async_shutdown()

    return unload_ok


async def async_reload_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> None:
    """
    Reload a config entry.
    """

    await async_unload_entry(
        hass,
        entry,
    )

    await async_setup_entry(
        hass,
        entry,
    )


async def async_remove_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> None:
    """
    Remove integration data after a config entry is deleted.
    """

    hass.data.get(DOMAIN, {}).pop(
        entry.entry_id,
        None,
    )