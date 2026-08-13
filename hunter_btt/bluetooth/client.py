"""Low-level BLE client for Hunter BTT controllers."""

from __future__ import annotations

import asyncio
import inspect
import logging
from collections.abc import Callable

from bleak.exc import BleakError
from homeassistant.components import bluetooth
from homeassistant.components.bluetooth import BluetoothServiceInfoBleak
from bleak_retry_connector import (
    BleakClientWithServiceCache,
    establish_connection,
)
from homeassistant.core import HomeAssistant

from ..protocol.uuids import (
    COUNTDOWN_UUID,
    NOTIFY_UUID,
    PASSCODE_UUID,
    STATUS_NOTIFY_UUID,
)

_LOGGER = logging.getLogger(__name__)


class HunterBLEClient:
    """Low-level BLE I/O; no protocol/entity logic."""

    def __init__(
        self,
        hass: HomeAssistant,
        discovery_info: BluetoothServiceInfoBleak,
    ) -> None:
        self._hass = hass
        self._address = discovery_info.address
        self._client: BleakClientWithServiceCache | None = None
        self._lock = asyncio.Lock()
        self._notification_callback = None

    @property
    def connected(self) -> bool:
        return bool(
            self._client is not None
            and self._client.is_connected
        )

    @property
    def service_uuids(self) -> set[str]:
        if self._client is None:
            return set()

        return {
            str(service.uuid).lower()
            for service in self._client.services
        }

    @property
    def characteristic_uuids(self) -> set[str]:
        if self._client is None:
            return set()

        return {
            str(characteristic.uuid).lower()
            for service in self._client.services
            for characteristic in service.characteristics
        }

    @property
    def rssi(self) -> int | None:
        if self._client is None:
            return None
        return getattr(self._client, "rssi", None)

    def register_notification_callback(self, callback) -> None:
        self._notification_callback = callback

    async def connect(self) -> None:
        async with self._lock:
            if self.connected:
                return

            device = bluetooth.async_ble_device_from_address(
                self._hass,
                self._address,
                connectable=True,
            )

            if device is None:
                raise BleakError(
                    f"Unable to locate BLE device {self._address}"
                )

            try:
                self._client = await establish_connection(
                    BleakClientWithServiceCache,
                    device,
                    name="Hunter BTT",
                )
            except Exception:
                self._client = None
                raise

            _LOGGER.debug("Connected to %s", self._address)

    async def disconnect(self) -> None:
        async with self._lock:
            if self._client is None:
                return

            try:
                if self._client.is_connected:
                    await self._client.disconnect()
            finally:
                self._client = None

    async def read(self, uuid: str) -> bytes:
        async with self._lock:
            await self._ensure_connected()
            assert self._client is not None
            try:
                return bytes(
                    await self._client.read_gatt_char(uuid)
                )
            except Exception as err:
                raise BleakError(
                    f"Read failed for {uuid}: {err}"
                ) from err

    async def write(
        self,
        uuid: str,
        payload: bytes,
        *,
        response: bool = True,
    ) -> None:
        async with self._lock:
            await self._ensure_connected()
            assert self._client is not None

            _LOGGER.debug(
                "WRITE %s : %s",
                uuid,
                payload.hex(" "),
            )

            try:
                await self._client.write_gatt_char(
                    uuid,
                    payload,
                    response=response,
                )
            except Exception as err:
                raise BleakError(
                    f"Write failed for {uuid}: {err}"
                ) from err

    async def start_notify(self, uuid: str) -> None:
        if not self.connected:
            await self.connect()

        assert self._client is not None

        if self._notification_callback is None:
            raise BleakError(
                "No Hunter notification callback registered."
            )

        def _callback(characteristic, data) -> None:
            result = self._notification_callback(
                str(characteristic.uuid),
                bytes(data),
            )
            if inspect.isawaitable(result):
                asyncio.create_task(result)

        await self._client.start_notify(
            uuid,
            _callback,
        )

    async def stop_notify(self, uuid: str) -> None:
        if not self.connected:
            return

        assert self._client is not None
        try:
            await self._client.stop_notify(uuid)
        except Exception:
            pass

    async def subscribe(self, callback=None) -> None:
        """Subscribe to Second-generation notifications only."""
        if callback is not None:
            self._notification_callback = callback

        if not self.connected:
            await self.connect()

        for uuid in (
            NOTIFY_UUID,
            COUNTDOWN_UUID,
            STATUS_NOTIFY_UUID,
        ):
            await self.start_notify(uuid)

    async def unsubscribe(self) -> None:
        if not self.connected:
            return

        for uuid in (
            NOTIFY_UUID,
            COUNTDOWN_UUID,
            STATUS_NOTIFY_UUID,
        ):
            await self.stop_notify(uuid)

    async def authenticate(self, passcode: bytes) -> None:
        await self.write(
            PASSCODE_UUID,
            passcode,
            response=True,
        )

    async def read_rssi(self) -> int | None:
        return self.rssi

    async def _ensure_connected(self) -> None:
        if not self.connected:
            await self.connect()
