"""DataUpdateCoordinator for the Hunter BTT integration.

The config entry stores the controller Bluetooth address.  Discovery is used
to identify the device, but the coordinator must not require a currently
connectable discovery record during setup.  The BLE manager/client resolves
the stored address when a connection is required.

This matches the current HunterBLEManager interface in the project:
    HunterBLEManager(hass=..., address=..., passcode=...)
    add_listener(...)
    connect()
    disconnect()
    refresh()
    start_zone(...)
    stop()
    shutdown()
"""

from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .bluetooth.manager import (
    HunterBLEManager,
    HunterManagerError,
)
from .const import (
    CONF_ADDRESS,
    CONF_PASSCODE,
    DEFAULT_SCAN_INTERVAL,
)
from .models import HunterState

_LOGGER = logging.getLogger(__name__)


class HunterDataUpdateCoordinator(DataUpdateCoordinator[HunterState]):
    """Coordinate communication with a Hunter BTT controller."""

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize the coordinator."""

        self.config_entry = config_entry

        self._address = config_entry.data[CONF_ADDRESS]
        self._manager = HunterBLEManager(
            hass=hass,
            address=self._address,
            passcode=config_entry.data.get(
                CONF_PASSCODE,
                "0000",
            ),
        )

        super().__init__(
            hass,
            _LOGGER,
            name="Hunter BTT201",
            update_interval=DEFAULT_SCAN_INTERVAL,
        )

        self.data = HunterState()

        self._remove_listener = self._manager.add_listener(
            self._manager_state_updated,
        )

    @property
    def manager(self) -> HunterBLEManager:
        """Return the BLE manager."""

        return self._manager

    @property
    def address(self) -> str:
        """Return the configured Bluetooth address."""

        return self._address

    @property
    def connected(self) -> bool:
        """Return connection status."""

        return self._manager.connected

    @property
    def state(self) -> HunterState:
        """Return current controller state."""

        return self.data

    @property
    def battery(self) -> int | None:
        """Return battery percentage."""

        return self.data.battery

    @property
    def active_zone(self) -> int | None:
        """Return active zone."""

        return self.data.active_zone

    @property
    def remaining_seconds(self) -> int:
        """Return remaining runtime."""

        return self.data.remaining_seconds

    async def async_initialize(self) -> None:
        """Connect and initialize the controller.

        No advertisement/discoverability check is performed here.  The
        controller was already identified by config flow; the stored BLE
        address is now handed to the manager.
        """

        _LOGGER.info(
            "Initializing Hunter BTT at stored address %s",
            self._address,
        )

        try:
            await self._manager.connect()

            self.data = self._manager.state
            self.async_set_updated_data(self.data)

        except Exception as err:
            raise UpdateFailed(
                f"Unable to connect to Hunter controller "
                f"{self._address}: {err}"
            ) from err

    async def _async_update_data(self) -> HunterState:
        """Refresh controller state."""

        try:
            if not self._manager.connected:
                _LOGGER.debug(
                    "Hunter controller %s is disconnected; reconnecting",
                    self._address,
                )
                await self._manager.connect()

            return await self._manager.refresh()

        except ConfigEntryAuthFailed:
            raise

        except HunterManagerError as err:
            raise UpdateFailed(str(err)) from err

        except Exception as err:
            raise UpdateFailed(
                f"Unexpected Hunter refresh failure: {err}"
            ) from err

    async def async_connect(self) -> None:
        """Ensure the controller is connected."""

        if self._manager.connected:
            return

        await self._manager.connect()

        self.data = self._manager.state
        self.async_set_updated_data(self.data)

    async def async_disconnect(self) -> None:
        """Disconnect from the controller."""

        await self._manager.disconnect()

        self.data = self._manager.state
        self.async_set_updated_data(self.data)

    async def async_shutdown(self) -> None:
        """Release coordinator resources."""

        if self._remove_listener is not None:
            self._remove_listener()
            self._remove_listener = None

        await self._manager.shutdown()

    def _manager_state_updated(
        self,
        state: HunterState,
    ) -> None:
        """Receive notification-driven manager state updates."""

        self.data = state
        self.async_set_updated_data(state)

    async def async_start_zone(
        self,
        zone: int,
        runtime: int,
    ) -> None:
        """Start manual watering."""

        _LOGGER.info(
            "Hunter START requested: zone=%d runtime=%ds",
            zone,
            runtime,
        )

        await self._manager.start_zone(zone, runtime)

        self.data = self._manager.state
        self.async_set_updated_data(self.data)

    async def async_stop(self) -> None:
        """Stop all watering."""

        _LOGGER.info("Hunter STOP requested")

        await self._manager.stop()

        self.data = self._manager.state
        self.async_set_updated_data(self.data)

    async def async_refresh_battery(self) -> int | None:
        """Refresh battery state."""

        battery = await self._manager.refresh_battery()

        self.data = self._manager.state
        self.async_set_updated_data(self.data)

        return battery

    async def async_refresh_all(self) -> None:
        """Request an immediate full refresh."""

        await self.async_request_refresh()
