"""Config flow for Hunter BTT.

Discovery follows the Android application's model: perform an active BLE scan,
identify a candidate from the advertisement, then defer protocol/generation
identification until after a real GATT connection and service discovery.
"""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.components import bluetooth
from homeassistant.components.bluetooth import BluetoothServiceInfoBleak
from homeassistant.const import CONF_ADDRESS, CONF_NAME
from homeassistant.data_entry_flow import FlowResult

from .bluetooth.discovery import is_hunter_btt
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class HunterConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Hunter BTT config flow."""

    VERSION = 1

    def __init__(self) -> None:
        self._devices: dict[str, BluetoothServiceInfoBleak] = {}

    async def _async_refresh_discoveries(self) -> None:
        """Run a one-shot active scan, then refresh the HA discovery cache."""
        await bluetooth.async_request_active_scan(self.hass, duration=5)
        current = bluetooth.async_discovered_service_info(
            self.hass,
            connectable=True,
        )
        self._devices = {
            info.address: info
            for info in current
            if is_hunter_btt(info)
        }
        _LOGGER.debug(
            "Hunter active scan: %d candidate(s): %s",
            len(self._devices),
            {
                address: {
                    "name": info.name,
                    "local_name": getattr(info, "local_name", None),
                    "services": sorted(info.service_uuids),
                }
                for address, info in self._devices.items()
            },
        )

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> FlowResult:
        """Handle user initiated setup."""
        await self._async_refresh_discoveries()

        if not self._devices:
            return self.async_abort(reason="no_devices_found")

        if user_input is not None:
            address = user_input[CONF_ADDRESS]
            discovery = self._devices.get(address)
            if discovery is None:
                return self.async_abort(reason="device_not_found")

            await self.async_set_unique_id(discovery.address)
            self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title=discovery.name or discovery.address,
                data={
                    CONF_ADDRESS: discovery.address,
                    CONF_NAME: discovery.name or "Hunter BTT",
                },
            )

        options = {
            address: f"{info.name or 'Hunter BTT'} ({address})"
            for address, info in self._devices.items()
        }
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {vol.Required(CONF_ADDRESS): vol.In(options)}
            ),
        )

    async def async_step_bluetooth(
        self,
        discovery_info: BluetoothServiceInfoBleak,
    ) -> FlowResult:
        """Handle Home Assistant Bluetooth discovery."""
        if not discovery_info.connectable:
            return self.async_abort(reason="not_supported")
        if not is_hunter_btt(discovery_info):
            return self.async_abort(reason="not_supported")

        await self.async_set_unique_id(discovery_info.address)
        self._abort_if_unique_id_configured()

        self._devices = {discovery_info.address: discovery_info}
        self.context["title_placeholders"] = {
            "name": discovery_info.name or discovery_info.address,
        }
        return await self.async_step_confirm()

    async def async_step_confirm(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> FlowResult:
        """Confirm discovery."""
        discovery = next(iter(self._devices.values()))

        if user_input is not None:
            self._abort_if_unique_id_configured()
            return self.async_create_entry(
                title=discovery.name or discovery.address,
                data={
                    CONF_ADDRESS: discovery.address,
                    CONF_NAME: discovery.name or "Hunter BTT",
                },
            )

        return self.async_show_form(
            step_id="confirm",
            description_placeholders={
                "name": discovery.name or discovery.address,
                "address": discovery.address,
            },
        )

    async def async_step_reconfigure(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> FlowResult:
        """Reconfigure the display name."""
        entry = self._get_reconfigure_entry()
        if user_input is not None:
            return self.async_update_reload_and_abort(
                entry,
                data_updates=user_input,
            )

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_NAME,
                        default=entry.data.get(CONF_NAME, "Hunter BTT"),
                    ): str,
                }
            ),
        )

    @staticmethod
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> HunterOptionsFlow:
        """Return options flow."""
        return HunterOptionsFlow(config_entry)


class HunterOptionsFlow(config_entries.OptionsFlow):
    """Hunter BTT options."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self._entry = config_entry

    async def async_step_init(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> FlowResult:
        """Handle options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        "poll_interval",
                        default=self._entry.options.get("poll_interval", 60),
                    ): vol.All(int, vol.Range(min=15, max=600)),
                    vol.Optional(
                        "automatic_refresh",
                        default=self._entry.options.get(
                            "automatic_refresh", True
                        ),
                    ): bool,
                    vol.Optional(
                        "debug_logging",
                        default=self._entry.options.get(
                            "debug_logging", False
                        ),
                    ): bool,
                }
            ),
        )
