"""High-level Hunter BTT BLE manager."""

from __future__ import annotations

import inspect
import logging
from typing import Any

from homeassistant.components.bluetooth import BluetoothServiceInfoBleak
from homeassistant.core import HomeAssistant

from ..protocol.generation import (
    HunterCapabilities,
    HunterGeneration,
    detect_generation,
    detect_zone_count,
)
from .client import HunterBLEClient
from .connection import HunterConnection
from .transaction import HunterTransactionEngine

_LOGGER = logging.getLogger(__name__)

COMMAND_UUID = "0000ff83-0000-1000-8000-00805f9b34fb"
FF80_SERVICE_UUID = "0000ff80-0000-1000-8000-00805f9b34fb"
FCC0_SERVICE_UUID = "0000fcc0-0000-1000-8000-00805f9b34fb"


class HunterManagerError(Exception):
    """Raised for Hunter manager errors."""


class HunterBLEManager:
    """Manage connection and protocol selection."""

    def __init__(
        self,
        hass: HomeAssistant,
        discovery_info: BluetoothServiceInfoBleak,
    ) -> None:
        self._hass = hass
        self.address = discovery_info.address

        # Keep every useful HA name representation.  Some Bluetooth
        # backends populate name while others expose a local_name.
        self.name = (
            getattr(discovery_info, "name", None)
            or getattr(discovery_info, "service_name", None)
            or ""
        )

        self.client = HunterBLEClient(hass, discovery_info)
        self.connection = HunterConnection(hass, self.client)
        self.transaction = HunterTransactionEngine(self.connection)

        self._generation = HunterGeneration.UNKNOWN
        self._capabilities = HunterCapabilities(
            generation=HunterGeneration.UNKNOWN,
            zone_count=0,
        )
        self.connected = False
        self._ff83_authorized = False
        self._state_callback = None

        self.state: dict[str, Any] = {
            "battery": None,
            "running": False,
            "active_zone": 0,
            "remaining_seconds": 0,
            "zones": {1: {}, 2: {}},
        }

    @property
    def generation(self) -> HunterGeneration:
        return self._generation

    @property
    def capabilities(self) -> HunterCapabilities:
        return self._capabilities

    @property
    def available(self) -> bool:
        return self.connected

    def register_callback(self, callback) -> None:
        self._state_callback = callback

    async def _notify_state_changed(self) -> None:
        if self._state_callback is None:
            return
        result = self._state_callback()
        if inspect.isawaitable(result):
            await result

    def _ff83_is_writable(self) -> bool:
        """Inspect GATT properties, but never use them to bless First gen."""
        bleak_client = getattr(self.client, "_client", None)
        if bleak_client is None:
            return False

        try:
            for service in bleak_client.services:
                for characteristic in service.characteristics:
                    if str(characteristic.uuid).lower() != COMMAND_UUID:
                        continue
                    properties = {
                        str(prop).strip().lower()
                        for prop in characteristic.properties
                    }
                    return bool(
                        {"write", "write-without-response"} & properties
                    )
        except Exception:
            _LOGGER.debug("Unable to inspect FF83 properties", exc_info=True)

        return False

    async def connect(self) -> None:
        if self.connected:
            return

        try:
            await self.connection.connect()

            services = set(self.connection.service_uuids)
            characteristics = set(self.connection.characteristic_uuids)

            self._generation = detect_generation(
                service_uuids=services,
                device_name=self.name,
                characteristic_uuids=characteristics,
            )

            name_upper = self.name.strip().upper()
            btt_name = "BTT" in name_upper
            ff83_writable = self._ff83_is_writable()

            _LOGGER.info(
                "Hunter identification: name=%r btt_name=%s generation=%s "
                "FF83_properties=%s FF83_writable=%s",
                self.name,
                btt_name,
                self._generation.value,
                sorted(
                    getattr(
                        self.client,
                        "characteristic_properties",
                        lambda _uuid: set(),
                    )(COMMAND_UUID)
                ),
                ff83_writable,
            )

            if self._generation is HunterGeneration.UNKNOWN:
                await self.connection.disconnect()
                raise HunterManagerError(
                    "Unable to identify Hunter BLE protocol generation."
                )

            # BTT-named devices are First generation. This is an absolute
            # safety rule: FF83 is NEVER authorized for them.
            if btt_name:
                self._generation = HunterGeneration.FIRST

            if self._generation is HunterGeneration.FIRST:
                zone_count = 1
                service_uuid = (
                    FF80_SERVICE_UUID
                    if FF80_SERVICE_UUID in services
                    else FCC0_SERVICE_UUID
                )
                self._ff83_authorized = False
            else:
                if FF80_SERVICE_UUID not in services:
                    await self.connection.disconnect()
                    raise HunterManagerError(
                        "Second-generation Hunter requires FF80 service."
                    )

                zone_count = detect_zone_count(
                    characteristics,
                    self._generation,
                )
                service_uuid = FF80_SERVICE_UUID

                # Only a non-BTT second-generation device with a genuinely
                # writable FF83 can use the existing FF83 transaction engine.
                self._ff83_authorized = ff83_writable

            if zone_count < 1:
                await self.connection.disconnect()
                raise HunterManagerError(
                    "Hunter controller has no proven supported zones."
                )

            self.transaction.set_ff83_enabled(self._ff83_authorized)

            self._capabilities = HunterCapabilities(
                generation=self._generation,
                zone_count=zone_count,
                service_uuid=service_uuid,
            )
            self.connected = True

            _LOGGER.info(
                "Hunter connected: address=%s name=%r generation=%s zones=%d "
                "FF83_authorized=%s",
                self.address,
                self.name,
                self._generation.value,
                zone_count,
                self._ff83_authorized,
            )

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
        await self.connection.disconnect()
        self.connected = False
        self._ff83_authorized = False
        self.transaction.set_ff83_enabled(False)
        await self._notify_state_changed()

    async def ensure_connected(self) -> None:
        if not self.connected or not self.connection.connected:
            await self.connect()

    async def reconnect(self) -> None:
        await self.connection.reconnect()
        self.connected = True

    async def start_zone(self, zone: int, runtime: int) -> None:
        await self.ensure_connected()

        if runtime <= 0:
            raise HunterManagerError("Runtime must be greater than zero.")

        if zone < 1 or zone > self._capabilities.zone_count:
            raise HunterManagerError(f"Zone {zone} is not supported.")

        if self._generation is HunterGeneration.FIRST:
            raise HunterManagerError(
                "First-generation Hunter detected. "
                "FF83 was NOT written. "
                "The First-generation protocol handler is required."
            )

        if not self._ff83_authorized:
            raise HunterManagerError(
                "FF83 is not authorized for this controller. "
                "No BLE write was attempted."
            )

        await self.transaction.start_zone(zone, runtime)

    async def stop(self) -> None:
        await self.ensure_connected()

        if self._generation is HunterGeneration.FIRST:
            raise HunterManagerError(
                "First-generation Hunter detected. "
                "FF83 was NOT written. "
                "The First-generation protocol handler is required."
            )

        if not self._ff83_authorized:
            raise HunterManagerError(
                "FF83 is not authorized for this controller. "
                "No BLE write was attempted."
            )

        await self.transaction.stop()

    async def refresh(self) -> dict[str, Any]:
        await self.ensure_connected()
        return self.state

    async def shutdown(self) -> None:
        await self.disconnect()
