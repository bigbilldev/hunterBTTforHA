"""Hunter BTT BLE transaction engine.

Generation routing is explicit:
- FIRST: Android-derived FCD9/FCEB manual protocol.
- SECOND: FF83 only.
The low-level client selects the correct GATT write type from the
characteristic properties.
"""

from __future__ import annotations

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Awaitable, Callable

from bleak.exc import BleakError

from ..protocol.first.commands import build_manual_start, build_manual_stop
from ..protocol.generation import HunterGeneration
from ..protocol.uuids import COMMAND_UUID

_LOGGER = logging.getLogger(__name__)

STOP_DELAY = 0.20
MAX_RETRIES = 2


class TransactionError(RuntimeError):
    """A BLE transaction failed."""


class TransactionTimeout(TransactionError):
    """A BLE transaction timed out."""


class HunterTransactionEngine:
    """Serialize BLE operations and enforce generation-specific routing."""

    def __init__(self, connection) -> None:
        self._connection = connection
        self._lock = asyncio.Lock()
        self._ack_event = asyncio.Event()
        self._last_ack: bytes | None = None
        self._generation = HunterGeneration.UNKNOWN

    @property
    def generation(self) -> HunterGeneration:
        return self._generation

    @property
    def ff83_enabled(self) -> bool:
        return self._generation is HunterGeneration.SECOND

    def set_generation(self, generation) -> None:
        value = getattr(generation, "value", generation)
        try:
            self._generation = HunterGeneration(
                str(value).strip().lower()
            )
        except ValueError:
            self._generation = HunterGeneration.UNKNOWN

        _LOGGER.info(
            "Hunter transaction generation=%s FF83_allowed=%s",
            self._generation.value,
            self.ff83_enabled,
        )

    def set_ff83_enabled(self, enabled: bool) -> None:
        """Backward-compatible manager API."""
        self.set_generation(
            HunterGeneration.SECOND
            if enabled
            else HunterGeneration.FIRST
        )

    def _assert_write_allowed(self, uuid: str) -> None:
        """Prevent accidental FF83 writes from the FIRST path."""
        if str(uuid).strip().lower() == COMMAND_UUID.lower():
            if self._generation is not HunterGeneration.SECOND:
                raise TransactionError(
                    "FF83 write blocked: controller is not explicitly "
                    "identified as second-generation."
                )

    async def notification(self, uuid: str, payload: bytes) -> None:
        self._last_ack = bytes(payload)
        self._ack_event.set()

    @asynccontextmanager
    async def transaction(self):
        async with self._lock:
            self._ack_event.clear()
            self._last_ack = None
            yield

    async def write(
        self,
        uuid: str,
        payload: bytes,
        *,
        response: bool | None = None,
    ) -> None:
        """Write a characteristic.

        response=None deliberately lets HunterBLEClient inspect GATT
        properties. This prevents write-without-response characteristics
        from being sent as write-with-response.
        """
        self._assert_write_allowed(uuid)

        async def _write() -> None:
            await self._connection.client.write(
                uuid,
                payload,
                response=response,
            )

        await self._retry(_write)

    async def read(self, uuid: str) -> bytes:
        async def _read() -> bytes:
            return await self._connection.client.read(uuid)

        last_error: Exception | None = None

        for attempt in range(MAX_RETRIES + 1):
            try:
                await self._connection.ensure_connection()
                return await _read()
            except BleakError as err:
                last_error = err
                _LOGGER.warning(
                    "BLE read failed (%s/%s) for %s: %s",
                    attempt + 1,
                    MAX_RETRIES + 1,
                    uuid,
                    err,
                )
                if attempt < MAX_RETRIES:
                    await self._connection.reconnect()
                    await asyncio.sleep(0.25)

        raise TransactionError(f"Failed reading {uuid}") from last_error

    async def wait_for_ack(self, timeout: float = 5.0) -> bytes:
        try:
            await asyncio.wait_for(self._ack_event.wait(), timeout)
        except TimeoutError as exc:
            raise TransactionTimeout(
                "Timed out waiting for Hunter acknowledgement."
            ) from exc
        return self._last_ack or b""

    async def start_zone(self, zone: int, runtime_seconds: int) -> None:
        if runtime_seconds <= 0:
            raise TransactionError("Runtime must be greater than zero.")

        if self._generation is HunterGeneration.FIRST:
            if zone != 1:
                raise TransactionError(
                    "First-generation BTT100 currently supports only zone 1."
                )

            command = build_manual_start(
                select_mode=0,
                runtime_seconds=runtime_seconds,
            )

            _LOGGER.info(
                "FIRST START: uuid=%s payload=%s",
                command.uuid,
                command.payload.hex(" "),
            )

            async with self.transaction():
                await self.write(command.uuid, command.payload)
            return

        if self._generation is not HunterGeneration.SECOND:
            raise TransactionError(
                "Hunter protocol generation is unknown; refusing to write."
            )

        # Preserve the existing proven second-generation sequence, but let
        # the low-level client choose write-with-response vs
        # write-without-response from FF83's actual GATT properties.
        from ..protocol.packets import (
            build_arm_packet,
            build_duration_packet,
            build_prepare_packet,
        )

        async with self.transaction():
            await self.write(
                COMMAND_UUID,
                build_prepare_packet(zone),
            )
            await asyncio.sleep(0.20)
            await self.write(
                COMMAND_UUID,
                build_duration_packet(runtime_seconds),
            )
            await asyncio.sleep(0.50)
            await self.write(
                COMMAND_UUID,
                build_arm_packet(zone),
            )

    async def stop(self) -> None:
        if self._generation is HunterGeneration.FIRST:
            command = build_manual_stop(
                select_mode=0,
                minute=0,
            )

            _LOGGER.info(
                "FIRST STOP: uuid=%s payload=%s",
                command.uuid,
                command.payload.hex(" "),
            )

            async with self.transaction():
                await self.write(command.uuid, command.payload)
            return

        if self._generation is not HunterGeneration.SECOND:
            raise TransactionError(
                "Hunter protocol generation is unknown; refusing to write."
            )

        from ..protocol.packets import build_stop_packet

        packet = build_stop_packet()

        async with self.transaction():
            await self.write(COMMAND_UUID, packet)
            await asyncio.sleep(STOP_DELAY)
            await self.write(COMMAND_UUID, packet)

    async def command(self, payload: bytes) -> None:
        if self._generation is not HunterGeneration.SECOND:
            raise TransactionError(
                "Generic FF83 command blocked for First-generation Hunter."
            )
        await self.write(COMMAND_UUID, payload)

    async def write_characteristic(
        self,
        uuid: str,
        payload: bytes,
    ) -> None:
        await self.write(uuid, payload)

    async def execute_sequence(
        self,
        *operations: Callable[[], Awaitable[None]],
    ) -> None:
        async with self.transaction():
            for operation in operations:
                await operation()

    async def _retry(
        self,
        func: Callable[[], Awaitable[None]],
    ) -> None:
        last_error: Exception | None = None

        for attempt in range(MAX_RETRIES + 1):
            try:
                await self._connection.ensure_connection()
                await func()
                return

            except BleakError as err:
                last_error = err
                _LOGGER.warning(
                    "BLE transaction failed (%s/%s): %s",
                    attempt + 1,
                    MAX_RETRIES + 1,
                    err,
                )

                if attempt < MAX_RETRIES:
                    await self._connection.reconnect()
                    await asyncio.sleep(0.25)

        raise TransactionError("BLE transaction failed.") from last_error
