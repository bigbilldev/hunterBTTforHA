"""Hunter BTT BLE transaction engine.

Generation-specific manual watering is selected by FF83 authorization:
- First generation: FF83 is never used. START/STOP use FCC0-family C3/D9/EB
  protocol frames.
- Second generation: existing FF83 transaction path is retained.

The First-generation frame construction follows the Android-derived protocol
objects in protocol/first and commands.py.
"""

from __future__ import annotations

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Awaitable, Callable

from bleak.exc import BleakError

from ..protocol.first.commands import build_manual_start, build_manual_stop
from ..protocol.uuids import COMMAND_UUID
from ..protocol.generation import HunterGeneration

_LOGGER = logging.getLogger(__name__)

PREPARE_DELAY = 0.20
ARM_DELAY = 0.50
STOP_DELAY = 0.20
ACK_TIMEOUT = 5.0
MAX_RETRIES = 2

FIRST_DEFAULT_SELECT_MODE = 0


class TransactionError(RuntimeError):
    """Transaction failed."""


class TransactionTimeout(TransactionError):
    """Timed out waiting for controller."""


class HunterTransactionEngine:
    """Serialize generation-specific BLE transactions."""

    def __init__(self, connection) -> None:
        self._connection = connection
        self._lock = asyncio.Lock()
        self._ack_event = asyncio.Event()
        self._last_ack: bytes | None = None
        self._ff83_enabled = False
        self._generation = HunterGeneration.UNKNOWN
        self._first_select_mode = FIRST_DEFAULT_SELECT_MODE
        self._first_stop_minute = 0

    @property
    def ff83_enabled(self) -> bool:
        return self._ff83_enabled

    def set_ff83_enabled(self, enabled: bool) -> None:
        self._ff83_enabled = bool(enabled)
        _LOGGER.info("FF83 transaction authorization=%s", self._ff83_enabled)

    def set_generation(self, generation: HunterGeneration) -> None:
        """Explicitly select the controller generation when available."""
        self._generation = generation
        _LOGGER.info("Transaction protocol generation=%s", generation.value)

    def set_first_select_mode(self, select_mode: int) -> None:
        """Set Android First_C3 selectMode (0=D9, 1=EB)."""
        if select_mode not in (0, 1):
            raise ValueError("First-generation selectMode must be 0 or 1")
        self._first_select_mode = select_mode

    def set_first_stop_minute(self, minute: int) -> None:
        """Set the minute field used by the First-generation STOP frame."""
        if not 0 <= minute <= 0xFFFF:
            raise ValueError("First-generation minute must be 0..65535")
        self._first_stop_minute = minute

    def _is_first_generation(self) -> bool:
        # The manager deliberately disables FF83 for First generation.
        # This fallback keeps the transaction engine compatible with the
        # current manager while preventing any accidental FF83 write.
        return (
            self._generation is HunterGeneration.FIRST
            or not self._ff83_enabled
        )

    def _assert_write_allowed(self, uuid: str) -> None:
        if (
            str(uuid).strip().lower() == COMMAND_UUID
            and not self._ff83_enabled
        ):
            raise TransactionError(
                "FF83 write blocked; First-generation protocol is active."
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

    async def wait_for_ack(self) -> bytes:
        try:
            await asyncio.wait_for(
                self._ack_event.wait(),
                ACK_TIMEOUT,
            )
        except TimeoutError as exc:
            raise TransactionTimeout(
                "Timed out waiting for Hunter acknowledgement."
            ) from exc
        return self._last_ack or b""

    async def write(
        self,
        uuid: str,
        payload: bytes,
        *,
        response: bool = True,
    ) -> None:
        self._assert_write_allowed(uuid)

        async def _write() -> None:
            await self._connection.client.write(
                uuid,
                payload,
                response=response,
            )

        await self._retry(_write)

    async def _write_first(
        self,
        uuid: str,
        payload: bytes,
    ) -> None:
        """Write a First-generation frame; this path can never use FF83."""
        if str(uuid).strip().lower() == COMMAND_UUID:
            raise TransactionError(
                "Internal safety error: First-generation attempted FF83."
            )

        async def _write() -> None:
            await self._connection.client.write(
                uuid,
                payload,
                response=True,
            )

        await self._retry(_write)

    async def start_zone(self, zone: int, runtime_seconds: int) -> None:
        """Start a zone using the correct generation protocol."""
        if runtime_seconds <= 0:
            raise ValueError("runtime must be greater than zero")

        if self._is_first_generation():
            # BTT100 is currently proven as a single-zone First-generation
            # controller. Do not silently address another zone.
            if zone != 1:
                raise TransactionError(
                    f"First-generation controller does not support zone {zone}."
                )

            command = build_manual_start(
                self._first_select_mode,
                runtime_seconds,
            )

            _LOGGER.info(
                "FIRST START: uuid=%s payload=%s selectMode=%d runtime=%ds",
                command.uuid,
                command.payload.hex(" "),
                self._first_select_mode,
                runtime_seconds,
            )

            async with self.transaction():
                await self._write_first(
                    command.uuid,
                    command.payload,
                )
            return

        # Second-generation path: FF83 only.
        self._assert_write_allowed(COMMAND_UUID)

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
            await asyncio.sleep(PREPARE_DELAY)
            await self.write(
                COMMAND_UUID,
                build_duration_packet(runtime_seconds),
            )
            await asyncio.sleep(ARM_DELAY)
            await self.write(
                COMMAND_UUID,
                build_arm_packet(zone),
            )

            try:
                await self.wait_for_ack()
            except TransactionTimeout:
                _LOGGER.debug("No acknowledgement received after second-gen start.")

    async def stop(self) -> None:
        """Stop watering using the correct generation protocol."""
        if self._is_first_generation():
            command = build_manual_stop(
                self._first_select_mode,
                self._first_stop_minute,
            )

            _LOGGER.info(
                "FIRST STOP: uuid=%s payload=%s selectMode=%d minute=%d",
                command.uuid,
                command.payload.hex(" "),
                self._first_select_mode,
                self._first_stop_minute,
            )

            async with self.transaction():
                await self._write_first(
                    command.uuid,
                    command.payload,
                )
            return

        from ..protocol.packets import build_stop_packet

        self._assert_write_allowed(COMMAND_UUID)

        async with self.transaction():
            packet = build_stop_packet()
            await self.write(COMMAND_UUID, packet)
            await asyncio.sleep(STOP_DELAY)
            await self.write(COMMAND_UUID, packet)

            try:
                await self.wait_for_ack()
            except TransactionTimeout:
                _LOGGER.debug("No acknowledgement received after second-gen stop.")

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

    async def command(self, payload: bytes) -> None:
        await self.write(COMMAND_UUID, payload)

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
                if attempt < MAX_RETRIES:
                    await self._connection.reconnect()
                    await asyncio.sleep(0.25)

        raise TransactionError(f"Failed reading {uuid}") from last_error

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

    @property
    def busy(self) -> bool:
        return self._lock.locked()
