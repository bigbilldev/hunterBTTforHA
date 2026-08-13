"""Low-level BLE connection wrapper for Hunter BTT controllers."""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Callable

from bleak import BleakClient
from bleak.backends.characteristic import BleakGATTCharacteristic
from bleak.backends.device import BLEDevice
from bleak.exc import BleakError

from homeassistant.components import bluetooth

_LOGGER = logging.getLogger(__name__)

NotificationCallback = Callable[[str, bytes], None]


class HunterBLEConnectionError(Exception):
    """Raised when BLE communication fails."""


class HunterBLEConnection:
    """Thin wrapper around a BleakClient."""

    def __init__(
        self,
        hass,
        address: str,
        *,
        timeout: float = 15.0,
    ) -> None:
        self._hass = hass
        self._address = address
        self._timeout = timeout
        self._ble_device: BLEDevice | None = None
        self._client: BleakClient | None = None

    @property
    def address(self) -> str:
        return self._address

    @property
    def connected(self) -> bool:
        return bool(
            self._client is not None
            and self._client.is_connected
        )

    @property
    def service_uuids(self) -> set[str]:
        """Return discovered GATT service UUIDs."""

        if self._client is None:
            return set()

        return {
            str(service.uuid).lower()
            for service in self._client.services
        }

    @property
    def characteristic_uuids(self) -> set[str]:
        """Return discovered GATT characteristic UUIDs."""

        if self._client is None:
            return set()

        return {
            str(characteristic.uuid).lower()
            for service in self._client.services
            for characteristic in service.characteristics
        }

    async def connect(self) -> None:
        """Connect without subscribing to notifications."""

        if self.connected:
            return

        try:
            self._ble_device = (
                bluetooth.async_ble_device_from_address(
                    self._hass,
                    self._address,
                    connectable=True,
                )
            )

            if self._ble_device is None:
                raise HunterBLEConnectionError(
                    f"Device {self._address} not found."
                )

            self._client = BleakClient(
                self._ble_device,
                disconnected_callback=self._handle_disconnect,
            )

            await asyncio.wait_for(
                self._client.connect(),
                timeout=self._timeout,
            )

            _LOGGER.info(
                "Connected to Hunter controller (%s)",
                self._address,
            )

        except Exception as err:
            self._client = None
            self._ble_device = None
            raise HunterBLEConnectionError(
                f"Unable to connect: {err}"
            ) from err

    async def disconnect(self) -> None:
        """Disconnect from the controller."""

        if self._client is None:
            return

        try:
            if self._client.is_connected:
                await asyncio.wait_for(
                    self._client.disconnect(),
                    timeout=self._timeout,
                )
        except BleakError as err:
            _LOGGER.debug("Disconnect failed: %s", err)
        finally:
            self._client = None
            self._ble_device = None

    async def read(self, uuid: str) -> bytes:
        """Read a GATT characteristic."""

        self._require_connection()

        try:
            return bytes(
                await self._client.read_gatt_char(uuid)
            )
        except Exception as err:
            raise HunterBLEConnectionError(
                f"Read failed: {uuid}"
            ) from err

    async def write(
        self,
        uuid: str,
        payload: bytes,
        *,
        response: bool = True,
    ) -> None:
        """Write a GATT characteristic."""

        self._require_connection()

        try:
            await self._client.write_gatt_char(
                uuid,
                payload,
                response=response,
            )
        except Exception as err:
            raise HunterBLEConnectionError(
                f"Write failed: {uuid}"
            ) from err

    async def start_notify(
        self,
        uuid: str,
        callback: NotificationCallback,
    ) -> None:
        """Subscribe to a notification characteristic."""

        self._require_connection()

        def _callback(
            characteristic: BleakGATTCharacteristic,
            data: bytearray,
        ) -> None:
            callback(
                str(characteristic.uuid),
                bytes(data),
            )

        try:
            await self._client.start_notify(uuid, _callback)
        except Exception as err:
            raise HunterBLEConnectionError(
                f"Unable to subscribe: {uuid}"
            ) from err

    async def stop_notify(self, uuid: str) -> None:
        """Remove a notification subscription."""

        self._require_connection()

        try:
            await self._client.stop_notify(uuid)
        except Exception as err:
            raise HunterBLEConnectionError(
                f"Unable to unsubscribe: {uuid}"
            ) from err

    async def read_rssi(self) -> int | None:
        if self._ble_device is None:
            return None
        return getattr(self._ble_device, "rssi", None)

    def _handle_disconnect(self, _client: BleakClient) -> None:
        """Handle an unexpected disconnect."""

        self._client = None
        _LOGGER.info("Hunter controller disconnected.")

    def _require_connection(self) -> None:
        if (
            self._client is None
            or not self._client.is_connected
        ):
            raise HunterBLEConnectionError("Not connected.")
