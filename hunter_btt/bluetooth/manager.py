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

# Keep these in manager.py for compatibility with the current project.
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

    async def connect(self) -> None:
        if self.connected:
            return

        try:
            await self.connection.connect()

            services = {
                str(uuid).strip().lower()
                for uuid in self.connection.service_uuids
            }
            characteristics = {
                str(uuid).strip().lower()
                for uuid in self.connection.characteristic_uuids
            }

            # IMPORTANT: do not import COMMAND_UUID or service constants
            # from generation.py. The manager owns those compatibility
            # constants and generation.py owns only generation logic.
            self._generation = detect_generation(
                service_uuids=services,
                device_name=self.name,
                characteristic_uuids=characteristics,
            )

            _LOGGER.info(
                "Hunter Android identification: name=%r generation=%s "
                "services=%s characteristics=%d",
                self.name,
                self._generation.value,
                sorted(services),
                len(characteristics),
            )

            if self._generation is HunterGeneration.UNKNOWN:
                await self.connection.disconnect()
                raise HunterManagerError(
                    "Unable to identify Hunter BLE protocol generation."
                )

            zone_count = detect_zone_count(
                characteristics,
                self._generation,
            )
            if zone_count < 1:
                await self.connection.disconnect()
                raise HunterManagerError(
                    "Hunter controller has no proven supported zones."
                )

            # First generation MUST NEVER authorize FF83.
            self._ff83_authorized = False
            if self._generation is HunterGeneration.SECOND:
                # Retain existing transaction compatibility, but only
                # authorize FF83 for second generation. The transaction
                # layer remains responsible for its own safety checks.
                self._ff83_authorized = True

            self.transaction.set_ff83_enabled(self._ff83_authorized)

            service_uuid = (
                FF80_SERVICE_UUID
                if FF80_SERVICE_UUID in services
                else FCC0_SERVICE_UUID
            )

            self._capabilities = HunterCapabilities(
                generation=self._generation,
                zone_count=zone_count,
                service_uuid=service_uuid,
            )
            self.connected = True

            _LOGGER.info(
                "Hunter connected: generation=%s zones=%d FF83_authorized=%s",
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
                "First-generation Hunter detected. FF83 was NOT written. "
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
                "First-generation Hunter detected. FF83 was NOT written. "
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
