"""Hunter BTT BLE manager."""

from __future__ import annotations

import inspect
import logging
from dataclasses import asdict
from typing import Any

from homeassistant.core import HomeAssistant

from ..models import HunterState
from ..protocol.second_generation import (
    build_ff83,
    merge_android_ff83,
    parse_ff82,
    parse_ff83,
)
from ..protocol.uuids import BATTERY_LEVEL_UUID, COMMAND_UUID, NOTIFY_UUID
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
from .transaction import HunterTransactionEngine

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
    def gatt_inventory(self) -> list[dict[str, object]]:
        return self.connection.gatt_inventory

    @property
    def writable_characteristics(self) -> list[dict[str, object]]:
        return self.connection.writable_characteristics

    @property
    def notification_status(self) -> dict[str, str]:
        return self.connection.notification_status

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

            _LOGGER.debug(
                "Hunter post-connect GATT inventory address=%s services=%s chars=%s",
                self.address,
                sorted(services),
                sorted(characteristics),
            )

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

            inventory = self.gatt_inventory
            _LOGGER.info(
                "Hunter GATT inventory address=%s service_count=%d characteristic_count=%d",
                self.address,
                len(services),
                len(inventory),
            )
            for item in inventory:
                _LOGGER.debug(
                    "Hunter GATT characteristic service=%s uuid=%s handle=%s properties=%s",
                    item["service_uuid"],
                    item["uuid"],
                    item["handle"],
                    item["properties"],
                )

            # Do not infer that FFA0/FFA1 are aliases for FF83. Keep the
            # native command UUID authoritative until packet-level evidence
            # establishes any transport-specific mapping.
            notification_status = await self.client.subscribe(
                self.transaction.notification
            )
            _LOGGER.info(
                "Hunter notification subscription results: %s",
                notification_status,
            )

            if self._generation is HunterGeneration.SECOND:
                await self._initialize_second_generation()
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

    async def _initialize_second_generation(self) -> None:
        """Initialize manual controls using readable FF82 and FF83 state.

        FF84 clock synchronization is deliberately non-blocking: some
        controllers/proxies reject ATT reads on FF84 even when GATT metadata
        advertises the read property. Clock synchronization is not required
        to establish the FF83 manual-control path.
        """
        self.protocol_initialized = False
        self.state["protocol_initialized"] = False

        async with self.transaction.transaction():
            status = parse_ff82(await self.transaction.read(NOTIFY_UUID))
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

        self.state["ff82_status"] = asdict(status)
        self.state["ff83_config"] = asdict(merged_config)
        self.protocol_initialized = True
        self.state["protocol_initialized"] = True
        _LOGGER.info(
            "Hunter second-generation initialization completed: "
            "FF82/FF83 read and FF83 state synchronized; FF84 clock sync skipped"
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
        await self.ensure_connected()
        return self.state

    async def refresh_battery(self) -> int | None:
        """Read the standard BLE Battery Level characteristic."""
        await self.ensure_connected()
        try:
            value = await self.connection.read(BATTERY_LEVEL_UUID)
            battery = int(value[0]) if value else None
        except Exception as err:
            raise HunterManagerError(f"Unable to read battery level: {err}") from err
        self.state["battery"] = battery
        await self._notify_state_changed()
        return battery

    async def shutdown(self) -> None:
        await self.disconnect()
