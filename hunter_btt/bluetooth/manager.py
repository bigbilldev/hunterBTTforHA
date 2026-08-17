"""Hunter BTT BLE manager with explicit generation routing.

The manager determines the protocol generation once at connection time and
passes that generation explicitly into the transaction engine.  This is
important for the BTT100/first-generation path: a first-generation controller
must never enter the FF83 transaction path.
"""

from __future__ import annotations

import inspect
import logging
from typing import Any

from homeassistant.components.bluetooth import BluetoothServiceInfoBleak
from homeassistant.core import HomeAssistant

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
    """Manage Hunter BLE connection and route operations by generation."""

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
        """Return the detected protocol generation."""
        return self._generation

    @property
    def capabilities(self) -> HunterCapabilities:
        """Return detected controller capabilities."""
        return self._capabilities

    @property
    def available(self) -> bool:
        """Return whether the controller is connected."""
        return self.connected

    def register_callback(self, callback) -> None:
        """Register a state-change callback."""
        self._state_callback = callback

    async def _notify_state_changed(self) -> None:
        if self._state_callback is None:
            return
        result = self._state_callback()
        if inspect.isawaitable(result):
            await result

    async def connect(self) -> None:
        """Connect and select the protocol generation exactly once."""
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

            normalized_name = normalize_android_device_name(self.name)

            # Android-equivalent identification rule.  For the BTT100 family,
            # names beginning with BTT are first-generation.
            generation = detect_generation(
                service_uuids=services,
                device_name=self.name,
                characteristic_uuids=characteristics,
            )

            if generation is HunterGeneration.UNKNOWN:
                raise HunterManagerError(
                    "Unable to identify Hunter protocol generation."
                )

            zone_count = detect_zone_count(characteristics, generation)
            if zone_count < 1:
                raise HunterManagerError(
                    f"No supported zones found for {generation.value} generation."
                )

            self._generation = generation

            # CRITICAL: make the transaction engine use the same generation
            # decision.  It must not infer generation independently.
            self.transaction.set_generation(generation)

            service_uuid = (
                SECOND_SERVICE_UUID
                if generation is HunterGeneration.SECOND
                else FCC0_SERVICE_UUID
            )

            self._capabilities = HunterCapabilities(
                generation=generation,
                zone_count=zone_count,
                service_uuid=service_uuid,
            )
            self.connected = True

            _LOGGER.info(
                "Hunter connected: name=%r normalized=%r generation=%s zones=%d",
                self.name,
                normalized_name,
                generation.value,
                zone_count,
            )

        except HunterManagerError:
            self.connected = False
            try:
                await self.connection.disconnect()
            except Exception:
                pass
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
        """Disconnect the controller."""
        await self.connection.disconnect()
        self.connected = False
        self.transaction.set_generation(HunterGeneration.UNKNOWN)
        await self._notify_state_changed()

    async def ensure_connected(self) -> None:
        """Ensure a live BLE connection."""
        if not self.connected or not self.connection.connected:
            await self.connect()

    async def reconnect(self) -> None:
        """Reconnect and reapply the detected generation."""
        await self.connection.reconnect()
        self.connected = False
        await self.connect()

    async def start_zone(self, zone: int, runtime: int) -> None:
        """Start a zone through the generation-specific transaction path."""
        await self.ensure_connected()

        if runtime <= 0:
            raise HunterManagerError("Runtime must be greater than zero.")

        if zone < 1 or zone > self._capabilities.zone_count:
            raise HunterManagerError(f"Zone {zone} is not supported.")

        # The transaction engine is now generation-locked.  In particular,
        # FIRST can only use the First_D9/First_EB path and can never write
        # COMMAND_UUID / FF83.
        await self.transaction.start_zone(zone, runtime)

    async def stop(self) -> None:
        """Stop watering through the generation-specific transaction path."""
        await self.ensure_connected()
        await self.transaction.stop()

    async def refresh(self) -> dict[str, Any]:
        """Return the current manager state."""
        await self.ensure_connected()
        return self.state

    async def shutdown(self) -> None:
        """Shut down the BLE manager."""
        await self.disconnect()
