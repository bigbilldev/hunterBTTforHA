"""Hunter BTT configuration flow.

Discovery deliberately follows the Android application's advertisement
approach: identify the controller from what it advertises, then resolve a
connectable BLE device by address only when a connection is actually needed.

This is important with ESPHome/remote Bluetooth proxies: the advertisement
can arrive as non-connectable even though the proxy can subsequently provide
a connectable BLEDevice for the same address.
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

ACTIVE_SCAN_SECONDS = 8
ADDRESS_SCHEMA = vol.Schema(
    {vol.Required(CONF_ADDRESS): str}
)


class HunterConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a Hunter BTT config flow."""

    VERSION = 1

    def __init__(self) -> None:
        self._devices: dict[str, BluetoothServiceInfoBleak] = {}

    async def _discover_devices(self) -> dict[str, BluetoothServiceInfoBleak]:
        """Collect Hunter advertisements regardless of connectable flag."""
        try:
            await bluetooth.async_request_active_scan(
                self.hass,
                duration=ACTIVE_SCAN_SECONDS,
            )
        except Exception as err:
            _LOGGER.warning("Hunter active scan request failed: %s", err)

        infos = bluetooth.async_discovered_service_info(
            self.hass,
            connectable=False,
        )

        devices: dict[str, BluetoothServiceInfoBleak] = {}
        for info in infos:
            details = describe_discovery(info)
            _LOGGER.warning("Hunter advertisement seen: %s", details)

            if is_hunter_btt(info):
                devices[info.address] = info

        _LOGGER.warning(
            "Hunter discovery result: %d candidate(s): %s",
            len(devices),
            sorted(devices),
        )
        return devices

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> FlowResult:
        """Discover Hunter controllers, with a manual-address fallback."""
        if user_input is not None:
            address = user_input.get(CONF_ADDRESS, "").strip().upper()
            if not address:
                return self.async_abort(reason="no_devices_found")

            # If the address was discovered, retain all advertisement data.
            info = self._devices.get(address)
            if info is None:
                info = self._devices.get(address.replace("-", ":"))

            await self.async_set_unique_id(address)
            self._abort_if_unique_id_configured()

            # Do not require a connectable advertisement here. The actual
            # connection layer will resolve the address through HA Bluetooth.
            return self.async_create_entry(
                title=(info.name if info else None) or f"Hunter BTT {address[-4:]}",
                data={
                    CONF_ADDRESS: address,
                    CONF_NAME: (info.name if info else None) or "Hunter BTT",
                },
            )

        self._devices = await self._discover_devices()

        options = {
            address: (
                f"{info.name or 'Hunter BTT'} "
                f"({address})"
            )
            for address, info in self._devices.items()
        }

        # Always include a manual-address path. This prevents discovery from
        # being a dead end when the remote proxy sees the device but HA's
        # matcher/cache has not retained a candidate yet.
        schema = vol.Schema(
            {
                vol.Optional(CONF_ADDRESS): str,
            }
        )

        if not self._devices:
            _LOGGER.warning(
                "No Hunter advertisements were found. "
                "The Bluetooth proxy may not be forwarding the device. "
                "Manual address entry remains available."
            )
            return self.async_show_form(
                step_id="user",
                data_schema=schema,
                description_placeholders={
                    "hint": "Enter the controller Bluetooth address, for example F0:5E:CD:1C:BB:B4.",
                },
            )

        # A discovered-device selector is easier to use, while still allowing
        # a manually entered address if the device changes advertisement form.
        schema = vol.Schema(
            {
                vol.Optional(
                    CONF_ADDRESS,
                    description="Bluetooth address",
                ): vol.In(options),
            }
        )
        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            description_placeholders={
                "hint": "Select the discovered Hunter controller.",
            },
        )

    async def async_step_bluetooth(
        self,
        discovery_info: BluetoothServiceInfoBleak,
    ) -> FlowResult:
        """Handle manifest-based Bluetooth discovery."""
        _LOGGER.warning(
            "Hunter Bluetooth config-flow discovery: %s",
            describe_discovery(discovery_info),
        )

        if not is_hunter_btt(discovery_info):
            return self.async_abort(reason="not_supported")

        await self.async_set_unique_id(discovery_info.address)
        self._abort_if_unique_id_configured()

        self._devices = {discovery_info.address: discovery_info}
        return await self.async_step_confirm()

    async def async_step_confirm(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> FlowResult:
        """Confirm a discovered Hunter controller."""
        info = next(iter(self._devices.values()))

        if user_input is not None:
            return self.async_create_entry(
                title=info.name or f"Hunter BTT {info.address[-4:]}",
                data={
                    CONF_ADDRESS: info.address,
                    CONF_NAME: info.name or "Hunter BTT",
                },
            )

        return self.async_show_form(
            step_id="confirm",
            description_placeholders={
                "name": info.name or "Hunter BTT",
                "address": info.address,
            },
        )

    async def async_step_reconfigure(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> FlowResult:
        """Handle reconfiguration."""
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
        return HunterOptionsFlow(config_entry)


class HunterOptionsFlow(config_entries.OptionsFlow):
    """Hunter options flow."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self._entry = config_entry

    async def async_step_init(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> FlowResult:
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
