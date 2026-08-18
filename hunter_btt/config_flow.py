"""Config flow for Hunter BTT.

Discovery follows the Android application's approach rather than requiring a
specific advertised service to be present in Home Assistant's cached scan.

The flow:
1. Use HA's one-shot active scan.
2. Inspect every newly available connectable advertisement.
3. Accept FCC0, FF80, or an Android-style BTT/Hunter name.
4. Preserve the raw discovery information for the later connection layer.
5. Do NOT determine generation or probe GATT during discovery.
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

from .bluetooth.discovery import describe_discovery, is_hunter_btt
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

ACTIVE_SCAN_SECONDS = 5


class HunterConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a Hunter BTT config flow."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the flow."""
        self._devices: dict[str, BluetoothServiceInfoBleak] = {}

    async def _discover_devices(self) -> dict[str, BluetoothServiceInfoBleak]:
        """Run an active scan and return Hunter candidates."""
        try:
            await bluetooth.async_request_active_scan(
                self.hass,
                duration=ACTIVE_SCAN_SECONDS,
            )
        except Exception as err:
            _LOGGER.warning("Hunter active Bluetooth scan failed: %s", err)

        # Read the cache AFTER the active sweep. Do not depend on the
        # integration manifest's service UUID filter for manual discovery.
        current = bluetooth.async_discovered_service_info(
            self.hass,
            connectable=True,
        )

        devices: dict[str, BluetoothServiceInfoBleak] = {}
        for info in current:
            details = describe_discovery(info)
            _LOGGER.debug("Hunter Bluetooth advertisement: %s", details)

            if not is_hunter_btt(info):
                continue

            devices[info.address] = info

        _LOGGER.info(
            "Hunter Bluetooth discovery found %d candidate(s): %s",
            len(devices),
            list(devices),
        )
        return devices

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> FlowResult:
        """Show discovered Hunter controllers."""
        self._devices = await self._discover_devices()

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
        """Handle Home Assistant's automatic Bluetooth discovery."""
        _LOGGER.debug(
            "Hunter automatic Bluetooth discovery: %s",
            describe_discovery(discovery_info),
        )

        if not is_hunter_btt(discovery_info):
            return self.async_abort(reason="not_supported")

        await self.async_set_unique_id(discovery_info.address)
        self._abort_if_unique_id_configured()

        self.context["title_placeholders"] = {
            "name": discovery_info.name or discovery_info.address,
        }

        self._devices = {discovery_info.address: discovery_info}
        return await self.async_step_confirm()

    async def async_step_confirm(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> FlowResult:
        """Confirm an automatically discovered controller."""
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
            self.hass.config_entries.async_update_entry(
                entry,
                data=user_input,
            )
            return self.async_abort(reason="reconfigured")

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
    ) -> "HunterOptionsFlow":
        """Return options flow."""
        return HunterOptionsFlow(config_entry)


class HunterOptionsFlow(config_entries.OptionsFlow):
    """Handle Hunter BTT options."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options."""
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
