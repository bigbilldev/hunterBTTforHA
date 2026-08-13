"""
bluetooth/manager.py

High-level BLE manager for the Hunter BTT201.

Responsibilities
----------------
* Own BLE client/connection/transaction engine
* Maintain device state cache
* Read/write all GATT characteristics
* Decode notifications
* Expose a simple API to the DataUpdateCoordinator

No Home Assistant entity logic belongs here.
"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime
from typing import Any

from homeassistant.components.bluetooth import BluetoothServiceInfoBleak
from homeassistant.core import HomeAssistant

from ..const import (
    BATTERY_LEVEL_UUID,
    COUNTDOWN_UUID,
    STATUS_NOTIFY_UUID,
    ZONE_CONFIG_UUID,
    ZONE_CYCLING_UUID,
    ZONE_DIAGNOSTIC_UUID,
    ZONE_TIMER_UUID,
)
from ..protocol.notifications import (
    CommandNotification,
    RuntimeNotification,
    StatusNotification,
    decode_notification,
)
from ..protocol.parser import (
    parse_battery,
    parse_countdown,
    parse_cycling_characteristic,
    parse_diagnostics,
    parse_timer_characteristic,
    parse_zone_config,
)
from .client import HunterBLEClient
from .connection import HunterConnection
from .transaction import HunterTransactionEngine

_LOGGER = logging.getLogger(__name__)


class HunterBLEManager:
    """Owns all BLE communication with a Hunter controller."""

    def __init__(
        self,
        hass: HomeAssistant,
        discovery_info: BluetoothServiceInfoBleak,
    ) -> None:

        self._hass = hass

        self.address = discovery_info.address
        self.name = discovery_info.name or "Hunter BTT201"

        #
        # BLE stack
        #

        self.client = HunterBLEClient(
            hass,
            discovery_info,
        )

        self.connection = HunterConnection(
            hass,
            self.client,
        )

        self.transaction = HunterTransactionEngine(
            self.connection,
        )

        self.connection.register_notification_callback(
            self._notification_received,
        )

        #
        # Cached GATT values
        #

        self.cache: dict[str, bytes] = {}

        #
        # Parsed state
        #

        self.state: dict[str, Any] = {
            "battery": None,
            "running": False,
            "active_zone": 0,
            "remaining_seconds": 0,
            "zones": {
                1: {},
                2: {},
            },
        }

        self.connected = False

        self.last_seen: datetime | None = None

        self.rssi: int | None = getattr(
            discovery_info,
            "rssi",
            None,
        )

        #
        # Optional callback used by the coordinator.
        #

        self._state_callback = None

        #
        # Prevent concurrent refreshes.
        #

        self._refresh_lock = asyncio.Lock()

    # ------------------------------------------------------------------
    # Callback registration
    # ------------------------------------------------------------------

    def register_callback(
        self,
        callback,
    ) -> None:
        """
        Register a callback invoked whenever state changes.

        The callback may be synchronous or async.
        """
        self._state_callback = callback

    async def _notify_state_changed(self) -> None:
        if self._state_callback is None:
            return

        result = self._state_callback()

        if asyncio.iscoroutine(result):
            await result

    # ------------------------------------------------------------------
    # Connection
    # ------------------------------------------------------------------

    async def connect(self) -> None:

        if self.connected:
            return

        await self.connection.connect()

        self.connected = True

        _LOGGER.info(
            "Connected to Hunter controller %s",
            self.address,
        )

    async def disconnect(self) -> None:

        if not self.connected:
            return

        await self.connection.disconnect()

        self.connected = False

    async def ensure_connected(self) -> None:
        if not self.connected:
            await self.connect()

    # ------------------------------------------------------------------
    # Notification handling
    # ------------------------------------------------------------------

    async def _notification_received(
        self,
        uuid: str,
        payload: bytes,
    ) -> None:
        """
        Invoked by HunterConnection whenever a notification arrives.
        """

        self.cache[uuid] = payload

        self.last_seen = datetime.utcnow()

        #
        # Transaction engine receives acknowledgements first.
        #

        await self.transaction.notification(
            uuid,
            payload,
        )

        decoded = decode_notification(
            uuid,
            payload,
        )

        if isinstance(
            decoded,
            RuntimeNotification,
        ):
            self._handle_runtime(decoded)

        elif isinstance(
            decoded,
            StatusNotification,
        ):
            self._handle_status(decoded)

        elif isinstance(
            decoded,
            CommandNotification,
        ):
            _LOGGER.debug(
                "Command ACK: %s",
                decoded.notification,
            )

        await self._notify_state_changed()

    # ------------------------------------------------------------------
    # Notification decoders
    # ------------------------------------------------------------------

    def _handle_runtime(
        self,
        runtime: RuntimeNotification,
    ) -> None:

        self.state["running"] = runtime.running
        self.state["active_zone"] = runtime.zone
        self.state["remaining_seconds"] = (
            runtime.remaining_seconds
        )

    def _handle_status(
        self,
        status: StatusNotification,
    ) -> None:

        self.state["running"] = status.running
        self.state["active_zone"] = status.zone

        if status.battery_percent is not None:
            self.state["battery"] = (
                status.battery_percent
            )

    # ------------------------------------------------------------------
    # Characteristic cache
    # ------------------------------------------------------------------

    async def _read(
        self,
        uuid: str,
    ) -> bytes:

        value = await self.transaction.read(uuid)

        self.cache[uuid] = value

        return value

    async def _write(
        self,
        uuid: str,
        payload: bytes,
    ) -> None:

        self.cache[uuid] = payload

        await self.transaction.write_characteristic(
            uuid,
            payload,
        )
    # ------------------------------------------------------------------
    # Refresh
    # ------------------------------------------------------------------

    async def refresh(self) -> dict[str, Any]:
        """
        Read all controller characteristics and rebuild the cached state.

        Returns the parsed state dictionary used by the
        DataUpdateCoordinator.
        """

        async with self._refresh_lock:

            await self.ensure_connected()

            #
            # Battery
            #

            try:
                payload = await self._read(
                    BATTERY_LEVEL_UUID,
                )

                self.state["battery"] = parse_battery(
                    payload,
                )

            except Exception:
                _LOGGER.exception(
                    "Failed reading battery level"
                )

            #
            # Zones
            #

            for zone in (1, 2):
                await self._refresh_zone(zone)

            #
            # Countdown
            #

            try:

                payload = await self._read(
                    COUNTDOWN_UUID,
                )

                countdown = parse_countdown(
                    payload,
                )

                self.state["running"] = (
                    countdown.active
                )

                self.state["active_zone"] = (
                    countdown.zone
                )

                self.state[
                    "remaining_seconds"
                ] = countdown.remaining_seconds

            except Exception:
                _LOGGER.debug(
                    "Countdown characteristic unavailable"
                )

            self.last_seen = datetime.utcnow()

            await self._notify_state_changed()

            return self.state

    # ------------------------------------------------------------------
    # Zone refresh
    # ------------------------------------------------------------------

    async def _refresh_zone(
        self,
        zone: int,
    ) -> None:

        zone_state: dict[str, Any] = (
            self.state["zones"].setdefault(
                zone,
                {},
            )
        )

        #
        # Configuration
        #

        try:

            payload = await self._read(
                ZONE_CONFIG_UUID[zone],
            )

            zone_state["config"] = (
                parse_zone_config(
                    payload,
                )
            )

        except Exception:

            _LOGGER.exception(
                "Unable to read zone %s config",
                zone,
            )

        #
        # Timer schedule
        #

        try:

            payload = await self._read(
                ZONE_TIMER_UUID[zone],
            )

            timer = (
                parse_timer_characteristic(
                    payload,
                )
            )

            zone_state["timer"] = {
                "enabled": timer.enabled,
                "days_mask": timer.days_mask,
                "start_times": timer.start_times,
                "runtime": timer.runtime,
            }

        except Exception:

            _LOGGER.exception(
                "Unable to read timer for zone %s",
                zone,
            )

        #
        # Cycling schedule
        #

        try:

            payload = await self._read(
                ZONE_CYCLING_UUID[zone],
            )

            cycling = (
                parse_cycling_characteristic(
                    payload,
                )
            )

            zone_state["cycling"] = {
                "enabled": cycling.enabled,
                "days_mask": cycling.days_mask,
                "start1": cycling.start1,
                "end1": cycling.end1,
                "start2": cycling.start2,
                "end2": cycling.end2,
                "runtime": cycling.runtime,
                "soak": cycling.soak,
            }

        except Exception:

            _LOGGER.exception(
                "Unable to read cycling schedule "
                "for zone %s",
                zone,
            )

        #
        # Diagnostics
        #

        try:

            payload = await self._read(
                ZONE_DIAGNOSTIC_UUID[zone],
            )

            zone_state["diagnostics"] = (
                parse_diagnostics(
                    payload,
                )
            )

        except Exception:

            _LOGGER.debug(
                "Diagnostics unavailable "
                "for zone %s",
                zone,
            )

        #
        # Convenience values exposed to entities
        #

        timer = zone_state.get("timer", {})
        cycling = zone_state.get("cycling", {})

        zone_state["runtime"] = timer.get(
            "runtime",
            0,
        )

        zone_state["timer_enabled"] = timer.get(
            "enabled",
            False,
        )

        zone_state["cycling_enabled"] = (
            cycling.get(
                "enabled",
                False,
            )
        )

    # ------------------------------------------------------------------
    # Cache helpers
    # ------------------------------------------------------------------

    def get_cached(
        self,
        uuid: str,
    ) -> bytes | None:
        """Return the last cached value for a characteristic."""

        return self.cache.get(uuid)

    def clear_cache(self) -> None:
        """Clear the raw characteristic cache."""

        self.cache.clear()

    # ------------------------------------------------------------------
    # State access
    # ------------------------------------------------------------------

    @property
    def battery(self) -> int | None:
        return self.state.get("battery")

    @property
    def running(self) -> bool:
        return self.state.get(
            "running",
            False,
        )

    @property
    def active_zone(self) -> int:
        return self.state.get(
            "active_zone",
            0,
        )

    @property
    def remaining_seconds(self) -> int:
        return self.state.get(
            "remaining_seconds",
            0,
        )

    def zone(self, zone: int) -> dict[str, Any]:
        """
        Return the parsed state for a zone.
        """

        return self.state["zones"].setdefault(
            zone,
            {},
        )

    # ------------------------------------------------------------------
    # Availability
    # ------------------------------------------------------------------

    @property
    def available(self) -> bool:
        """
        Device is available when connected.

        Coordinator will also track update success.
        """

        return self.connected  
     # ------------------------------------------------------------------
    # Manual watering
    # ------------------------------------------------------------------

    async def start_zone(
        self,
        zone: int,
        runtime: int,
    ) -> None:
        """
        Start manual watering.
        """

        _LOGGER.info(
            "Starting zone %s (%s seconds)",
            zone,
            runtime,
        )

        await self.transaction.start_zone(
            zone,
            runtime,
        )

        self.state["running"] = True
        self.state["active_zone"] = zone
        self.state["remaining_seconds"] = runtime

        zone_state = self.zone(zone)
        zone_state["runtime"] = runtime

        await self._notify_state_changed()

    async def stop(self) -> None:
        """
        Stop manual watering.
        """

        _LOGGER.info("Stopping irrigation")

        await self.transaction.stop()

        self.state["running"] = False
        self.state["active_zone"] = 0
        self.state["remaining_seconds"] = 0

        await self._notify_state_changed()

    # ------------------------------------------------------------------
    # Runtime
    # ------------------------------------------------------------------

    async def set_manual_runtime(
        self,
        zone: int,
        runtime: int,
    ) -> None:
        """
        Update the cached manual runtime.

        The runtime packet is written when a manual watering
        transaction is started.
        """

        self.zone(zone)["runtime"] = runtime

        await self._notify_state_changed()

    # ------------------------------------------------------------------
    # Timer configuration
    # ------------------------------------------------------------------

    async def write_timer(
        self,
        zone: int,
        schedule,
    ) -> None:
        """
        Write a complete timer schedule.

        'schedule' is expected to be a TimerSchedule model from
        protocol.schedules.
        """

        from ..protocol.packets import (
            build_timer_block,
            mutate_timer_config,
        )

        timer_payload = build_timer_block(schedule)

        current = self.cache.get(
            ZONE_CONFIG_UUID[zone],
        )

        if current is None:
            current = await self._read(
                ZONE_CONFIG_UUID[zone],
            )

        config_payload = mutate_timer_config(
            current,
            schedule.enabled,
            schedule.day_mask,
        )

        await self._write(
            ZONE_TIMER_UUID[zone],
            timer_payload,
        )

        await self._write(
            ZONE_CONFIG_UUID[zone],
            config_payload,
        )

        await self.refresh()

    async def enable_timer(
        self,
        zone: int,
        enabled: bool,
    ) -> None:

        zone_state = self.zone(zone)

        timer = zone_state.setdefault(
            "timer",
            {},
        )

        timer["enabled"] = enabled

        from ..protocol.packets import (
            mutate_timer_config,
        )

        current = self.cache.get(
            ZONE_CONFIG_UUID[zone],
        )

        if current is None:
            current = await self._read(
                ZONE_CONFIG_UUID[zone],
            )

        payload = mutate_timer_config(
            current,
            enabled,
            timer.get(
                "days_mask",
                0,
            ),
        )

        await self._write(
            ZONE_CONFIG_UUID[zone],
            payload,
        )

        await self.refresh()

    # ------------------------------------------------------------------
    # Cycling configuration
    # ------------------------------------------------------------------

    async def write_cycling(
        self,
        zone: int,
        schedule,
    ) -> None:

        from ..protocol.packets import (
            build_cycling_block,
            mutate_cycling_config,
        )

        cycling_payload = build_cycling_block(
            schedule,
        )

        current = self.cache.get(
            ZONE_CONFIG_UUID[zone],
        )

        if current is None:
            current = await self._read(
                ZONE_CONFIG_UUID[zone],
            )

        config_payload = mutate_cycling_config(
            current,
            schedule.enabled,
            schedule.day_mask,
        )

        await self._write(
            ZONE_CYCLING_UUID[zone],
            cycling_payload,
        )

        await self._write(
            ZONE_CONFIG_UUID[zone],
            config_payload,
        )

        await self.refresh()

    async def enable_cycling(
        self,
        zone: int,
        enabled: bool,
    ) -> None:

        zone_state = self.zone(zone)

        cycling = zone_state.setdefault(
            "cycling",
            {},
        )

        cycling["enabled"] = enabled

        from ..protocol.packets import (
            mutate_cycling_config,
        )

        current = self.cache.get(
            ZONE_CONFIG_UUID[zone],
        )

        if current is None:
            current = await self._read(
                ZONE_CONFIG_UUID[zone],
            )

        payload = mutate_cycling_config(
            current,
            enabled,
            cycling.get(
                "days_mask",
                0,
            ),
        )

        await self._write(
            ZONE_CONFIG_UUID[zone],
            payload,
        )

        await self.refresh()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    async def read_characteristic(
        self,
        uuid: str,
    ) -> bytes:
        return await self._read(uuid)

    async def write_characteristic(
        self,
        uuid: str,
        payload: bytes,
    ) -> None:
        await self._write(
            uuid,
            payload,
        )

    # ------------------------------------------------------------------
    # Refresh helpers
    # ------------------------------------------------------------------

    async def refresh_zone(
        self,
        zone: int,
    ) -> dict[str, Any]:

        await self._refresh_zone(zone)

        return self.zone(zone)

    async def refresh_battery(self) -> int | None:

        payload = await self._read(
            BATTERY_LEVEL_UUID,
        )

        battery = parse_battery(payload)

        self.state["battery"] = battery

        return battery

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    @property
    def diagnostics(self) -> dict[str, Any]:
        return {
            "address": self.address,
            "name": self.name,
            "connected": self.connected,
            "last_seen": self.last_seen,
            "cache_entries": len(self.cache),
            "state": self.state,
        }

    # ------------------------------------------------------------------
    # Shutdown
    # ------------------------------------------------------------------

    async def shutdown(self) -> None:
        """
        Disconnect from the controller and release BLE resources.
        """

        _LOGGER.info(
            "Shutting down Hunter BLE manager"
        )

        self.clear_cache()

        await self.disconnect()    