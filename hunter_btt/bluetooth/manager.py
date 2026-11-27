"""Hunter BTT BLE manager."""

from __future__ import annotations

import inspect
import logging
from datetime import timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.util import dt as dt_util

from ..models import HunterState
from ..protocol.second_generation import (
    build_ff83,
    build_ff84,
    merge_android_ff83,
    parse_ff82,
    parse_ff83,
)
from ..protocol.uuids import (
    BATTERY_LEVEL_UUID,
    COMMAND_UUID,
    COUNTDOWN_UUID,
    NOTIFY_UUID,
    STATUS_NOTIFY_UUID,
    TIME_UUID,
)
from ..protocol.generation import (
    FCC0_SERVICE_UUID,
    SECOND_SERVICE_UUID,
    HunterCapabilities,
    HunterGeneration,
    detect_generation,
    detect_zone_count,
    normalize_android_device_name,
)
from .client import HunterBLEClient
from .connection import HunterConnection
from .transaction import (
    HunterTransactionEngine,
    TransactionError,
    TransactionTimeout,
    TransactionWriteNotPermitted,
)

_LOGGER = logging.getLogger(__name__)


class HunterManagerError(Exception):
    """Raised for Hunter manager errors."""


class HunterBLEManager:
    """Manage BLE connection, GATT identification and transactions."""

    def __init__(
        self,
        hass: HomeAssistant,
        address: str,
        passcode: str = "0000",
        zone1_enabled: int = 1,
        zone2_enabled: int = 1,
    ) -> None:
        self._hass = hass
        self.address = address
        self.name = "Hunter BTT"
        self.passcode = passcode
        self._zone_enabled = {1: zone1_enabled, 2: zone2_enabled}
        self.protocol_initialized = False
        self.client = HunterBLEClient(hass, address)
        self.connection = HunterConnection(hass, self.client)
        self.transaction = HunterTransactionEngine(self.connection)

        self._generation = HunterGeneration.UNKNOWN
        self._capabilities = HunterCapabilities(
            generation=HunterGeneration.UNKNOWN,
            zone_count=0,
        )
        self.connected = False
        self._state_callback = None
        self._listeners: set[Any] = set()
        self.state = HunterState()

    @property
    def generation(self) -> HunterGeneration:
        return self._generation

    @property
    def capabilities(self) -> HunterCapabilities:
        return self._capabilities

    @property
    def available(self) -> bool:
        return self.connected

    @property
    def writable_characteristics(self) -> list[dict[str, object]]:
        return self.connection.writable_characteristics

    @property
    def command_properties(self) -> set[str]:
        return self.connection.characteristic_properties(COMMAND_UUID)

    @property
    def control_ready(self) -> bool:
        return (
            self._generation is HunterGeneration.SECOND
            and self.protocol_initialized
            and "write" in self.command_properties
        )

    def command_readiness_issue(self) -> str | None:
        if self._generation is not HunterGeneration.SECOND:
            return "Valve control is currently implemented only for second-generation controllers."
        properties = self.command_properties
        if not properties:
            writable = [
                f"{item['uuid']} (handle={item['handle']}, properties={item['properties']})"
                for item in self.writable_characteristics
            ]
            return (
                "Required FF83 command characteristic is absent from the connected GATT database. "
                "No alternate writable characteristic will be assumed. "
                f"Writable characteristics discovered: {writable or 'none'}."
            )
        if "write" not in properties:
            return (
                "FF83 does not advertise write-with-response, which is required "
                f"for the captured Android command path; properties={sorted(properties)}."
            )
        if not self.protocol_initialized:
            return "Second-generation controller initialization has not completed successfully."
        return None

    def add_listener(self, callback):
        """Register a state listener and return an unsubscribe callback."""
        self._listeners.add(callback)

        def remove_listener() -> None:
            self._listeners.discard(callback)

        return remove_listener

    def register_callback(self, callback) -> None:
        """Compatibility alias for integrations using a single callback."""
        self._state_callback = callback

    async def _notify_state_changed(self) -> None:
        callbacks = set(self._listeners)
        if self._state_callback is not None:
            callbacks.add(self._state_callback)
        for callback in callbacks:
            try:
                result = callback(self.state)
                if inspect.isawaitable(result):
                    await result
            except Exception:
                _LOGGER.exception("Hunter state listener failed")

    @staticmethod
    def _parse_battery_payload(payload: bytes) -> int:
        """Decode the standard 2A19 uint8 battery percentage."""
        if len(payload) != 1:
            raise ValueError(
                f"Battery Level 2A19 must be exactly one byte; received {len(payload)}."
            )
        level = payload[0]
        if level > 100:
            raise ValueError(
                f"Battery Level 2A19 must be 0..100 percent; received {level}."
            )
        return level

    async def _handle_notification(self, uuid: str, payload: bytes) -> None:
        """Cache protocol notifications and update battery telemetry."""
        key = str(uuid).strip().lower()
        value = bytes(payload)
        await self.transaction.notification(key, value)

        if key != BATTERY_LEVEL_UUID:
            return

        try:
            battery = self._parse_battery_payload(value)
        except ValueError as err:
            _LOGGER.warning("Ignoring invalid Hunter battery notification: %s", err)
            return

        if self.state.get("battery") != battery:
            self.state["battery"] = battery
            _LOGGER.debug("Hunter battery level notification: %d%%", battery)
            await self._notify_state_changed()

    async def connect(self) -> None:
        """Connect, enumerate GATT, then identify protocol and zones."""
        if self.connected and self.connection.connected:
            return

        self.protocol_initialized = False
        self.state["protocol_initialized"] = False

        try:
            await self.connection.connect()

            services = set(self.connection.service_uuids)
            characteristics = set(self.connection.characteristic_uuids)

            self._generation = detect_generation(
                service_uuids=services,
                device_name=self.name,
                characteristic_uuids=characteristics,
            )
            if self._generation is HunterGeneration.UNKNOWN:
                raise HunterManagerError(
                    "Unable to identify Hunter protocol generation from "
                    "connected GATT services/characteristics."
                )

            zone_count = detect_zone_count(
                characteristics,
                self._generation,
            )
            if zone_count < 1:
                raise HunterManagerError(
                    f"No supported zones found for "
                    f"{self._generation.value} generation."
                )

            self._capabilities = HunterCapabilities(
                generation=self._generation,
                zone_count=zone_count,
                service_uuid=(
                    SECOND_SERVICE_UUID
                    if self._generation is HunterGeneration.SECOND
                    else FCC0_SERVICE_UUID
                ),
            )

            self.transaction.set_generation(self._generation)

            # Do not infer that FFA0/FFA1 are aliases for FF83. Keep the
            # native command UUID authoritative until packet-level evidence
            # establishes any transport-specific mapping.
            # FF82 is notification-driven on this controller. Discard any
            # payload retained from a previous connection before subscribing.
            self.transaction.clear_notification(NOTIFY_UUID)
            self.transaction.clear_notification(BATTERY_LEVEL_UUID)
            _LOGGER.info(
                "Hunter Android initialization comparison: the reference flow "
                "enables FF82/FF8A/FF8F notifications before connectTwoInit. "
                "Observed connectTwoInit variants differ on an FF84 read "
                "(one issues it and ignores the callback; another omits it); "
                "both proceed with FF84 write, FF82/FF83 reads, status merge, "
                "and FF83 write. This controller's safe "
                "path does not ATT-read FF82 and does not invent an additional "
                "initialization write."
            )
            subscription_status = await self.client.subscribe(
                self._handle_notification
            )
            _LOGGER.info(
                "Hunter notification subscription results: FF82=%s FF8A=%s "
                "FF8F=%s battery_2A19=%s",
                subscription_status.get(NOTIFY_UUID, "not reported"),
                subscription_status.get(COUNTDOWN_UUID, "not reported"),
                subscription_status.get(STATUS_NOTIFY_UUID, "not reported"),
                subscription_status.get(BATTERY_LEVEL_UUID, "not reported"),
            )

            if self._generation is HunterGeneration.SECOND:
                await self._initialize_second_generation_if_supported()
            else:
                self.protocol_initialized = True

            readiness_issue = self.command_readiness_issue()
            if readiness_issue:
                _LOGGER.warning("Hunter valve control is not ready: %s", readiness_issue)

            self.connected = True
            self.state["protocol_initialized"] = self.protocol_initialized
            await self._notify_state_changed()

            _LOGGER.info(
                "Hunter connected: address=%s name=%r generation=%s zones=%d "
                "services=%s",
                self.address,
                normalize_android_device_name(self.name),
                self._generation.value,
                zone_count,
                sorted(services),
            )

        except HunterManagerError:
            self.connected = False
            self.protocol_initialized = False
            try:
                await self.connection.disconnect()
            except Exception:
                pass
            raise
        except Exception as err:
            self.connected = False
            self.protocol_initialized = False
            try:
                await self.connection.disconnect()
            except Exception:
                pass
            raise HunterManagerError(
                f"Unable to connect to Hunter controller: {err}"
            ) from err

    async def _initialize_second_generation_if_supported(self) -> None:
        """Initialize only when the connected GATT transport exposes FF83.

        Some Bluetooth transports expose a different GATT table from the
        native controller. Never guess that another writable UUID is an FF83
        alias. Keep the BLE connection available for supported telemetry,
        but leave valve control unavailable until the command characteristic
        and its initialization notification are actually available.
        """
        self.protocol_initialized = False
        self.state["protocol_initialized"] = False

        if not self.command_properties:
            _LOGGER.warning(
                "Hunter second-generation valve control unavailable: FF83 "
                "was not discovered. GATT inventory: %s",
                self.connection.gatt_inventory,
            )
            return

        try:
            await self._initialize_second_generation()
        except (TransactionTimeout, TransactionError, ValueError) as err:
            _LOGGER.warning(
                "Hunter connected, but second-generation valve control "
                "initialization is incomplete: %s. No FF83 state was written.",
                err,
            )

    async def _synchronize_clock(self) -> None:
        """Write the phone's local time plus one second to FF84.

        Android's connection initialization sends this clock update without
        depending on an FF84 read or using a read response to build the payload.
        Keep clock synchronization explicit and separate from FF82/FF83 state
        synchronization.
        """
        clock_payload = build_ff84(dt_util.now() + timedelta(seconds=1))
        await self.transaction.write(
            TIME_UUID,
            clock_payload,
            response=True,
        )
        _LOGGER.debug("Hunter FF84 clock synchronization written")

    async def _initialize_second_generation(self) -> None:
        """Synchronize FF84 clock, then initialize FF83 from FF82 status.

        FF84 is write-only in this initialization flow: do not read it or make
        a successful FF84 read a prerequisite for guarded FF83 control.
        FF82 is notification-driven and must never be ATT-read.
        """
        self.protocol_initialized = False
        self.state["protocol_initialized"] = False

        async with self.transaction.transaction():
            # Clock synchronization is best-effort. Some controllers expose
            # FF84 as writable in GATT discovery but reject the ATT write.
            # The transaction layer identifies ATT 0x03 explicitly and never
            # retries that permanent rejection. Neither that rejection nor
            # another clock-sync failure may bypass the FF82/FF83 readiness
            # checks below.
            try:
                await self._synchronize_clock()
            except TransactionWriteNotPermitted as err:
                _LOGGER.warning(
                    "Hunter FF84 clock synchronization is unsupported by "
                    "this controller (ATT 0x03 Write Not Permitted); "
                    "continuing initialization without clock sync: %s",
                    err,
                )
            except Exception as err:
                _LOGGER.warning(
                    "Hunter FF84 best-effort clock synchronization failed; "
                    "continuing with FF82/FF83 initialization: %s",
                    err,
                )

            _LOGGER.info(
                "Hunter initialization phase: FF84 clock attempt complete; "
                "consuming FF82 notification cache/waiter before any FF83 read or write"
            )
            status = parse_ff82(
                await self.transaction.wait_for_notification(
                    NOTIFY_UUID,
                    timeout=8.0,
                )
            )
            current_config = parse_ff83(
                await self.transaction.read(COMMAND_UUID)
            )
            merged_config = merge_android_ff83(
                current_config,
                status,
                zone1_enabled=self._zone_enabled[1],
                zone2_enabled=self._zone_enabled[2],
            )
            await self.transaction.write(
                COMMAND_UUID,
                build_ff83(merged_config),
                response=True,
            )

        self.protocol_initialized = True
        self.state["protocol_initialized"] = True
        _LOGGER.info(
            "Hunter second-generation initialization completed: "
            "FF84 clock synchronization attempted (best-effort), "
            "FF82 status received, and FF83 state synchronized"
        )

    async def disconnect(self) -> None:
        try:
            await self.client.unsubscribe()
        except Exception:
            pass
        await self.connection.disconnect()
        self.connected = False
        self.protocol_initialized = False
        self.state["protocol_initialized"] = False
        self.transaction.set_generation(HunterGeneration.UNKNOWN)
        await self._notify_state_changed()

    async def ensure_connected(self) -> None:
        if not self.connected or not self.connection.connected:
            await self.connect()

    async def reconnect(self) -> None:
        await self.connection.reconnect()
        self.connected = False
        await self.connect()

    async def start_zone(self, zone: int, runtime: int) -> None:
        await self.ensure_connected()
        readiness_issue = self.command_readiness_issue()
        if readiness_issue:
            raise HunterManagerError(readiness_issue)
        if runtime <= 0:
            raise HunterManagerError("Runtime must be greater than zero.")
        if zone < 1 or zone > self._capabilities.zone_count:
            raise HunterManagerError(f"Zone {zone} is not supported.")
        await self.transaction.start_zone(zone, runtime)
        self.state["running"] = True
        self.state["active_zone"] = zone
        self.state["remaining_seconds"] = runtime
        await self._notify_state_changed()

    async def stop(self) -> None:
        await self.ensure_connected()
        readiness_issue = self.command_readiness_issue()
        if readiness_issue:
            raise HunterManagerError(readiness_issue)
        await self.transaction.stop()
        self.state["running"] = False
        self.state["active_zone"] = 0
        self.state["remaining_seconds"] = 0
        await self._notify_state_changed()

    async def refresh(self) -> HunterState:
        """Refresh the live values exposed to Home Assistant."""
        await self.refresh_battery()
        return self.state

    async def refresh_battery(self) -> int | None:
        """Read the standard BLE Battery Level characteristic."""
        await self.ensure_connected()
        try:
            value = await self.connection.read(BATTERY_LEVEL_UUID)
            battery = self._parse_battery_payload(value)
        except Exception as err:
            # Battery level is optional telemetry. A transient GATT/proxy read
            # failure must not make the coordinator unavailable or discard the
            # last successfully reported value.
            previous_battery = self.state.get("battery")
            _LOGGER.warning(
                "Optional Hunter battery telemetry read failed: uuid=%s "
                "error_type=%s error=%s; retaining previous value=%s",
                BATTERY_LEVEL_UUID,
                type(err).__name__,
                err,
                previous_battery,
            )
            return previous_battery
        self.state["battery"] = battery
        await self._notify_state_changed()
        return battery

    async def shutdown(self) -> None:
        await self.disconnect()
