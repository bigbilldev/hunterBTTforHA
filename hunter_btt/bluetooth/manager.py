"""Hunter BTT BLE manager."""

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
    """Manage the BLE connection and protocol transactions."""

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
        if self.connected and self.connection.connected:
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

            # GATT service identity is authoritative.  Do not classify a
            # BTT100/BTT200 from the marketing name when the service is known.
            self._generation = detect_generation(
                service_uuids=services,
                device_name=self.name,
                characteristic_uuids=characteristics,
            )

            if self._generation is HunterGeneration.UNKNOWN:
                raise HunterManagerError(
                    "Unable to identify Hunter protocol generation."
                )

            zone_count = detect_zone_count(
                characteristics,
                self._generation,
            )
            if zone_count < 1:
                raise HunterManagerError(
                    f"No supported zones found for {self._generation.value} generation."
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

            # Android discovers services, initializes its characteristic
            # objects, then enables the transaction handler.  The HA client
            # has already completed service discovery at this point.  Subscribe
            # before commands so FF82/FF8A notifications cannot be missed.
            try:
                await self.client.subscribe(
                    self.transaction.notification
                )
            except Exception as err:
                _LOGGER.debug(
                    "Hunter notifications could not be subscribed: %s",
                    err,
                )

            self.connected = True

            ff83_properties = self.client.characteristic_properties(
                "0000ff83-0000-1000-8000-00805f9b34fb"
            )

            _LOGGER.info(
                "Hunter connected: name=%r normalized=%r generation=%s "
                "zones=%d FF83_properties=%s",
                self.name,
                normalized_name,
                self._generation.value,
                zone_count,
                sorted(ff83_properties),
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
        try:
            await self.client.unsubscribe()
        except Exception:
            pass

        await self.connection.disconnect()
        self.connected = False
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

        if runtime <= 0:
            raise HunterManagerError("Runtime must be greater than zero.")

        if zone < 1 or zone > self._capabilities.zone_count:
            raise HunterManagerError(f"Zone {zone} is not supported.")

        await self.transaction.start_zone(zone, runtime)

    async def stop(self) -> None:
        await self.ensure_connected()
        await self.transaction.stop()

    async def refresh(self) -> dict[str, Any]:
        await self.ensure_connected()
        return self.state

    async def shutdown(self) -> None:
        await self.disconnect()
