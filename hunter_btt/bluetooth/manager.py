"""High-level BLE manager for Hunter BTT controllers.

This manager keeps protocol selection above the transaction layer.

Important:
The FF80 service alone does NOT prove that the controller uses the
FF83/second-generation command protocol.  The BTT100 test device exposes
FF80 but does not expose a writable FF83 characteristic.  Such a device is
therefore treated as an FF80 legacy profile and is deliberately prevented
from entering the FF83 transaction path until its FFAx protocol is mapped.
"""

from __future__ import annotations

import asyncio
import inspect
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
from ..protocol.generation import (
    HunterCapabilities,
    HunterGeneration,
    detect_generation,
    detect_zone_count,
)
from ..protocol.first import (
    FirstC3,
    FirstD9,
    FirstEB,
    build_manual_start,
    build_manual_stop,
    decode_frame,
)
from ..protocol.uuids import (
    FIRST_C3_UUID,
    FIRST_D9_UUID,
    FIRST_EB_UUID,
)
from .client import HunterBLEClient
from .connection import HunterConnection
from .transaction import HunterTransactionEngine

_LOGGER = logging.getLogger(__name__)

COMMAND_UUID = "0000ff83-0000-1000-8000-00805f9b34fb"
SECOND_SERVICE_UUID = "0000ff80-0000-1000-8000-00805f9b34fb"
COMMAND_DELAY = 0.25


class HunterManagerError(Exception):
    """Raised for Hunter manager errors."""


class HunterBLEManager:
    """Own BLE communication and cached controller state."""

    def __init__(
        self,
        hass: HomeAssistant,
        discovery_info: BluetoothServiceInfoBleak,
    ) -> None:
        self._hass = hass
        self.address = discovery_info.address
        self.name = discovery_info.name or "Hunter BTT"

        self.client = HunterBLEClient(hass, discovery_info)
        self.connection = HunterConnection(hass, self.client)
        self.transaction = HunterTransactionEngine(self.connection)

        self.connection.register_notification_callback(
            self._notification_received
        )

        self._generation = HunterGeneration.UNKNOWN
        self._capabilities = HunterCapabilities(
            generation=HunterGeneration.UNKNOWN,
            zone_count=0,
        )

        # True for the BTT100-style FF80 service which does not expose FF83.
        self._ff80_legacy = False

        self.cache: dict[str, bytes] = {}
        self.state: dict[str, Any] = {
            "battery": None,
            "running": False,
            "active_zone": 0,
            "remaining_seconds": 0,
            "zones": {1: {}, 2: {}},
        }

        self.connected = False
        self.last_seen: datetime | None = None
        self.rssi = getattr(discovery_info, "rssi", None)
        self._state_callback = None
        self._refresh_lock = asyncio.Lock()

    def register_callback(self, callback) -> None:
        """Register the coordinator state callback."""
        self._state_callback = callback

    async def _notify_state_changed(self) -> None:
        """Notify the coordinator."""
        if self._state_callback is None:
            return

        result = self._state_callback()
        if inspect.isawaitable(result):
            await result

    @property
    def generation(self) -> HunterGeneration:
        """Return detected generation."""
        return self._generation

    @property
    def capabilities(self) -> HunterCapabilities:
        """Return detected capabilities."""
        return self._capabilities

    @property
    def battery(self) -> int | None:
        return self.state.get("battery")

    @property
    def running(self) -> bool:
        return bool(self.state.get("running", False))

    @property
    def active_zone(self) -> int:
        return int(self.state.get("active_zone", 0))

    @property
    def remaining_seconds(self) -> int:
        return int(self.state.get("remaining_seconds", 0))

    def zone(self, zone: int) -> dict[str, Any]:
        return self.state["zones"].setdefault(zone, {})

    @property
    def available(self) -> bool:
        return self.connected

    @property
    def legacy_ff80(self) -> bool:
        """Return whether this is the FF80/no-FF83 legacy profile."""
        return self._ff80_legacy

    async def connect(self) -> None:
        """Connect and identify the protocol profile."""
        if self.connected:
            return

        try:
            await self.connection.connect()

            services = self.connection.service_uuids
            characteristics = self.connection.characteristic_uuids

            self._generation = detect_generation(services)

            # FF80 is shared by devices which do not necessarily use FF83.
            # The BTT100 test device has FF80 but no FF83. Do not route it
            # into the FF83 transaction engine.
            self._ff80_legacy = (
                SECOND_SERVICE_UUID in services
                and COMMAND_UUID not in characteristics
            )

            if self._ff80_legacy:
                self._generation = HunterGeneration.FIRST
                zone_count = 1
                _LOGGER.warning(
                    "Hunter BTT legacy FF80 profile detected: "
                    "FF83 is absent; using one-zone legacy profile"
                )
            else:
                if self._generation is HunterGeneration.UNKNOWN:
                    await self.connection.disconnect()
                    raise HunterManagerError(
                        "Unable to identify Hunter BLE protocol generation."
                    )

                zone_count = detect_zone_count(
                    characteristics,
                    self._generation,
                )

            self._capabilities = HunterCapabilities(
                generation=self._generation,
                zone_count=zone_count,
                service_uuid=(
                    SECOND_SERVICE_UUID
                    if SECOND_SERVICE_UUID in services
                    else "0000fcc0-0000-1000-8000-00805f9b34fb"
                ),
            )

            self.connected = True

            _LOGGER.info(
                "Connected to Hunter %s: generation=%s zones=%d "
                "legacy_ff80=%s",
                self.address,
                self._generation.value,
                self._capabilities.zone_count,
                self._ff80_legacy,
            )

            if (
                self._generation is HunterGeneration.SECOND
                and not self._ff80_legacy
            ):
                await self.client.subscribe(
                    self._notification_received,
                )

            self.last_seen = datetime.utcnow()
            self.rssi = await self.connection.read_rssi()
            await self._notify_state_changed()

        except HunterManagerError:
            self.connected = False
            raise
        except Exception as err:
            self.connected = False
            try:
                await self.connection.disconnect()
            except Exception:
                pass

            raise HunterManagerError(
                f"Unable to connect to Hunter controller: {err}"
            ) from err

    async def disconnect(self) -> None:
        """Disconnect and clear connection state."""
        if not self.connected and not self.connection.connected:
            return

        try:
            if self._generation is HunterGeneration.SECOND:
                try:
                    await self.client.unsubscribe()
                except Exception:
                    _LOGGER.debug(
                        "Unable to unsubscribe Hunter notifications",
                        exc_info=True,
                    )
        finally:
            await self.connection.disconnect()
            self.connected = False
            await self._notify_state_changed()

    async def ensure_connected(self) -> None:
        """Ensure the controller is connected."""
        if not self.connected or not self.connection.connected:
            await self.connect()

    async def _notification_received(
        self,
        uuid: str,
        payload: bytes,
    ) -> None:
        """Handle second-generation notifications."""
        self.cache[uuid] = payload
        self.last_seen = datetime.utcnow()

        if not self._ff80_legacy:
            await self.transaction.notification(uuid, payload)

        decoded = decode_notification(uuid, payload)

        if isinstance(decoded, RuntimeNotification):
            self.state["running"] = decoded.running
            self.state["active_zone"] = decoded.zone
            self.state["remaining_seconds"] = (
                decoded.remaining_seconds
            )
        elif isinstance(decoded, StatusNotification):
            self.state["running"] = decoded.running
            self.state["active_zone"] = decoded.zone
            if decoded.battery_percent is not None:
                self.state["battery"] = decoded.battery_percent
        elif isinstance(decoded, CommandNotification):
            _LOGGER.debug(
                "Command ACK: %s",
                decoded.notification,
            )

        await self._notify_state_changed()

    async def _read(self, uuid: str) -> bytes:
        await self.ensure_connected()
        value = await self.transaction.read(uuid)
        self.cache[uuid] = value
        return value

    async def _write(self, uuid: str, payload: bytes) -> None:
        await self.ensure_connected()
        await self.transaction.write_characteristic(
            uuid,
            payload,
        )
        self.cache[uuid] = payload

    async def refresh(self) -> dict[str, Any]:
        """Refresh only characteristics appropriate to this profile."""
        async with self._refresh_lock:
            await self.ensure_connected()

            try:
                self.state["battery"] = await self.refresh_battery()
            except Exception:
                _LOGGER.debug(
                    "Failed reading battery level",
                    exc_info=True,
                )

            # Do not guess at the BTT100 FFAx protocol yet.
            if self._ff80_legacy:
                self.last_seen = datetime.utcnow()
                await self._notify_state_changed()
                return self.state

            if self._generation is HunterGeneration.FIRST:
                self.last_seen = datetime.utcnow()
                await self._notify_state_changed()
                return self.state

            for zone in range(
                1,
                self._capabilities.zone_count + 1,
            ):
                await self._refresh_zone(zone)

            try:
                payload = await self._read(COUNTDOWN_UUID)
                countdown = parse_countdown(payload)
                self.state["running"] = countdown.active
                self.state["active_zone"] = countdown.zone
                self.state["remaining_seconds"] = (
                    countdown.remaining_seconds
                )
            except Exception:
                _LOGGER.debug(
                    "Countdown characteristic unavailable",
                    exc_info=True,
                )

            self.last_seen = datetime.utcnow()
            await self._notify_state_changed()
            return self.state

    async def _refresh_zone(self, zone: int) -> None:
        """Refresh one second-generation zone."""
        zone_state = self.zone(zone)

        try:
            payload = await self._read(ZONE_CONFIG_UUID[zone])
            zone_state["config"] = parse_zone_config(payload)
        except Exception:
            _LOGGER.debug(
                "Unable to read zone %s config",
                zone,
                exc_info=True,
            )

        try:
            payload = await self._read(ZONE_TIMER_UUID[zone])
            timer = parse_timer_characteristic(payload)
            zone_state["timer"] = {
                "enabled": timer.enabled,
                "days_mask": timer.days_mask,
                "start_times": timer.start_times,
                "runtime": timer.runtime,
            }
        except Exception:
            _LOGGER.debug(
                "Unable to read timer for zone %s",
                zone,
                exc_info=True,
            )

        try:
            payload = await self._read(ZONE_CYCLING_UUID[zone])
            cycling = parse_cycling_characteristic(payload)
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
            _LOGGER.debug(
                "Unable to read cycling schedule for zone %s",
                zone,
                exc_info=True,
            )

        try:
            payload = await self._read(ZONE_DIAGNOSTIC_UUID[zone])
            zone_state["diagnostics"] = parse_diagnostics(payload)
        except Exception:
            _LOGGER.debug(
                "Diagnostics unavailable for zone %s",
                zone,
                exc_info=True,
            )

        timer = zone_state.get("timer", {})
        cycling = zone_state.get("cycling", {})
        zone_state["runtime"] = timer.get("runtime", 0)
        zone_state["timer_enabled"] = timer.get("enabled", False)
        zone_state["cycling_enabled"] = cycling.get(
            "enabled",
            False,
        )

    async def refresh_zone(self, zone: int) -> dict[str, Any]:
        """Refresh a single zone."""
        await self.ensure_connected()

        if self._ff80_legacy:
            if zone != 1:
                raise HunterManagerError(
                    "Legacy FF80 Zone 2 support is not proven."
                )
            return self.zone(zone)

        if self._generation is HunterGeneration.FIRST:
            if zone != 1:
                raise HunterManagerError(
                    "First-generation Zone 2 support is not proven."
                )
            return self.zone(zone)

        await self._refresh_zone(zone)
        await self._notify_state_changed()
        return self.zone(zone)

    async def refresh_battery(self) -> int | None:
        """Read the battery characteristic."""
        payload = await self._read(BATTERY_LEVEL_UUID)
        battery = parse_battery(payload)
        self.state["battery"] = battery
        return battery

    async def start_zone(self, zone: int, runtime: int) -> None:
        """Start manual watering."""
        await self.ensure_connected()

        if runtime <= 0:
            raise HunterManagerError(
                "Runtime must be greater than zero."
            )

        if zone < 1 or zone > self._capabilities.zone_count:
            raise HunterManagerError(
                f"Zone {zone} is not supported."
            )

        if self._ff80_legacy:
            raise HunterManagerError(
                "BTT100 legacy FF80 protocol detected. "
                "FF83 is not present; the legacy FFAx start "
                "protocol has not yet been mapped."
            )

        if self._generation is HunterGeneration.FIRST:
            await self._start_zone_first(zone, runtime)
            return

        await self.transaction.start_zone(zone, runtime)
        self.state["running"] = True
        self.state["active_zone"] = zone
        self.state["remaining_seconds"] = runtime
        self.zone(zone)["runtime"] = runtime
        await self._notify_state_changed()

    async def _start_zone_first(
        self,
        zone: int,
        runtime: int,
    ) -> None:
        """Start the proven FCC0 first-generation controller path."""
        if zone != 1:
            raise HunterManagerError(
                "First-generation Zone 2 support is not proven."
            )

        c3_payload = await self._read(FIRST_C3_UUID)
        try:
            c3 = FirstC3.from_payload(
                decode_frame(c3_payload).payload
            )
        except Exception as err:
            raise HunterManagerError(
                "Unable to decode First-generation C3 state."
            ) from err

        try:
            write = build_manual_start(
                c3.select_mode,
                runtime,
            )
        except ValueError as err:
            raise HunterManagerError(str(err)) from err

        _LOGGER.info(
            "First-generation start: mode=%d runtime=%d "
            "uuid=%s payload=%s",
            c3.select_mode,
            runtime,
            write.uuid,
            write.payload.hex(" "),
        )

        await self.connection.write(
            write.uuid,
            write.payload,
            response=True,
        )

        await asyncio.sleep(COMMAND_DELAY)
        self.state["running"] = True
        self.state["active_zone"] = zone
        self.state["remaining_seconds"] = runtime
        self.zone(zone)["runtime"] = runtime
        await self._notify_state_changed()

    async def stop(self) -> None:
        """Stop manual watering."""
        await self.ensure_connected()

        if self._ff80_legacy:
            raise HunterManagerError(
                "BTT100 legacy FF80 protocol detected. "
                "FF83 is not used; the legacy FFAx stop "
                "protocol has not yet been mapped."
            )

        if self._generation is HunterGeneration.FIRST:
            await self._stop_first()
            return

        await self.transaction.stop()
        self.state["running"] = False
        self.state["active_zone"] = 0
        self.state["remaining_seconds"] = 0
        await self._notify_state_changed()

    async def _stop_first(self) -> None:
        """Stop the proven FCC0 first-generation controller path."""
        c3_payload = await self._read(FIRST_C3_UUID)

        try:
            c3 = FirstC3.from_payload(
                decode_frame(c3_payload).payload
            )
        except Exception as err:
            raise HunterManagerError(
                "Unable to decode First-generation C3 state."
            ) from err

        if c3.select_mode == 0:
            uuid = FIRST_D9_UUID
            protocol_type = FirstD9
        elif c3.select_mode == 1:
            uuid = FIRST_EB_UUID
            protocol_type = FirstEB
        else:
            raise HunterManagerError(
                f"Unsupported First-generation selectMode: "
                f"{c3.select_mode}"
            )

        current_payload = await self._read(uuid)

        try:
            current = protocol_type.from_payload(
                decode_frame(current_payload).payload
            )
            write = build_manual_stop(
                c3.select_mode,
                current.minute,
            )
        except ValueError as err:
            raise HunterManagerError(str(err)) from err

        _LOGGER.info(
            "First-generation stop: mode=%d uuid=%s payload=%s",
            c3.select_mode,
            write.uuid,
            write.payload.hex(" "),
        )

        await self.connection.write(
            write.uuid,
            write.payload,
            response=True,
        )

        await asyncio.sleep(COMMAND_DELAY)
        self.state["running"] = False
        self.state["active_zone"] = 0
        self.state["remaining_seconds"] = 0
        await self._notify_state_changed()

    async def set_manual_runtime(
        self,
        zone: int,
        runtime: int,
    ) -> None:
        """Update the cached runtime for a zone."""
        self.zone(zone)["runtime"] = runtime
        await self._notify_state_changed()

    async def write_timer(self, zone: int, schedule) -> None:
        """Write a second-generation timer schedule."""
        if self._generation is HunterGeneration.FIRST:
            raise HunterManagerError(
                "Timer writes are not supported for this generation."
            )

        from ..protocol.packets import (
            build_timer_block,
            mutate_timer_config,
        )

        timer_payload = build_timer_block(schedule)
        current = self.cache.get(ZONE_CONFIG_UUID[zone])
        if current is None:
            current = await self._read(ZONE_CONFIG_UUID[zone])

        config_payload = mutate_timer_config(
            current,
            schedule.enabled,
            schedule.day_mask,
        )
        await self._write(ZONE_TIMER_UUID[zone], timer_payload)
        await self._write(ZONE_CONFIG_UUID[zone], config_payload)
        await self.refresh()

    async def enable_timer(self, zone: int, enabled: bool) -> None:
        """Enable or disable a second-generation timer."""
        if self._generation is HunterGeneration.FIRST:
            raise HunterManagerError(
                "Timer writes are not supported for this generation."
            )

        zone_state = self.zone(zone)
        timer = zone_state.setdefault("timer", {})
        timer["enabled"] = enabled

        from ..protocol.packets import mutate_timer_config

        current = self.cache.get(ZONE_CONFIG_UUID[zone])
        if current is None:
            current = await self._read(ZONE_CONFIG_UUID[zone])

        payload = mutate_timer_config(
            current,
            enabled,
            timer.get("days_mask", 0),
        )
        await self._write(ZONE_CONFIG_UUID[zone], payload)
        await self.refresh()

    async def write_cycling(self, zone: int, schedule) -> None:
        """Write a second-generation cycling schedule."""
        if self._generation is HunterGeneration.FIRST:
            raise HunterManagerError(
                "Cycling writes are not supported for this generation."
            )

        from ..protocol.packets import (
            build_cycling_block,
            mutate_cycling_config,
        )

        cycling_payload = build_cycling_block(schedule)
        current = self.cache.get(ZONE_CONFIG_UUID[zone])
        if current is None:
            current = await self._read(ZONE_CONFIG_UUID[zone])

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
        """Enable or disable second-generation cycling."""
        if self._generation is HunterGeneration.FIRST:
            raise HunterManagerError(
                "Cycling writes are not supported for this generation."
            )

        zone_state = self.zone(zone)
        cycling = zone_state.setdefault("cycling", {})
        cycling["enabled"] = enabled

        from ..protocol.packets import mutate_cycling_config

        current = self.cache.get(ZONE_CONFIG_UUID[zone])
        if current is None:
            current = await self._read(ZONE_CONFIG_UUID[zone])

        payload = mutate_cycling_config(
            current,
            enabled,
            cycling.get("days_mask", 0),
        )
        await self._write(
            ZONE_CONFIG_UUID[zone],
            payload,
        )
        await self.refresh()

    async def read_characteristic(self, uuid: str) -> bytes:
        """Read a raw GATT characteristic."""
        return await self._read(uuid)

    async def write_characteristic(
        self,
        uuid: str,
        payload: bytes,
    ) -> None:
        """Write a raw GATT characteristic."""
        if self._ff80_legacy and uuid.lower() == COMMAND_UUID:
            raise HunterManagerError(
                "FF83 is not available on the BTT100 legacy FF80 profile."
            )

        await self._write(uuid, payload)

    def get_cached(self, uuid: str) -> bytes | None:
        return self.cache.get(uuid)

    def clear_cache(self) -> None:
        self.cache.clear()

    @property
    def diagnostics(self) -> dict[str, Any]:
        """Return diagnostic information."""
        return {
            "address": self.address,
            "name": self.name,
            "connected": self.connected,
            "generation": self._generation.value,
            "zone_count": self._capabilities.zone_count,
            "legacy_ff80": self._ff80_legacy,
            "last_seen": self.last_seen,
            "cache_entries": len(self.cache),
            "state": self.state,
        }

    async def shutdown(self) -> None:
        """Shut down the manager."""
        self.clear_cache()
        await self.disconnect()
