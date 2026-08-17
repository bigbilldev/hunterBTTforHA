"""Serialized Hunter BTT transactions with an absolute FF83 safety guard."""

from __future__ import annotations

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Awaitable, Callable

from bleak.exc import BleakError

from ..protocol.packets import (
    build_arm_packet,
    build_duration_packet,
    build_prepare_packet,
    build_stop_packet,
)
from ..protocol.uuids import COMMAND_UUID

_LOGGER = logging.getLogger(__name__)

PREPARE_DELAY = 0.20
ARM_DELAY = 0.50
STOP_DELAY = 0.20
ACK_TIMEOUT = 5.0
MAX_RETRIES = 2


class TransactionError(RuntimeError):
    """Transaction failed."""


class TransactionTimeout(TransactionError):
    """Timed out waiting for controller."""


class HunterTransactionEngine:
    """Serialize transactions and enforce the FF83 authorization boundary."""

    def __init__(self, connection) -> None:
        self._connection = connection
        self._lock = asyncio.Lock()
        self._ack_event = asyncio.Event()
        self._last_ack: bytes | None = None
        self._ff83_enabled = False

    @property
    def ff83_enabled(self) -> bool:
        return self._ff83_enabled

    def set_ff83_enabled(self, enabled: bool) -> None:
        self._ff83_enabled = bool(enabled)
        _LOGGER.info(
            "FF83 transaction authorization=%s",
            self._ff83_enabled,
        )

    def _assert_write_allowed(self, uuid: str) -> None:
        """Reject FF83 before connection/retry/BLE code is reached."""
        if str(uuid).strip().lower() == COMMAND_UUID:
            if not self._ff83_enabled:
                raise TransactionError(
                    "FF83 WRITE BLOCKED before BLE I/O. "
                    "This transaction is not authorized for this controller."
                )

    async def notification(self, uuid: str, payload: bytes) -> None:
        if uuid.lower().endswith(
            "ff82-0000-1000-8000-00805f9b34fb"
        ):
            self._last_ack = payload
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
        # CRITICAL: this is before _retry(), so an unauthorized FF83 write
        # cannot produce a BLE Write-not-permitted error.
        self._assert_write_allowed(uuid)

        async def _write() -> None:
            await self._connection.client.write(
                uuid,
                payload,
                response=response,
            )

        await self._retry(_write)

    async def start_zone(self, zone: int, runtime_seconds: int) -> None:
        self._assert_write_allowed(COMMAND_UUID)

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
                _LOGGER.debug(
                    "No acknowledgement received after start."
                )

    async def stop(self) -> None:
        self._assert_write_allowed(COMMAND_UUID)

        async with self.transaction():
            packet = build_stop_packet()
            await self.write(COMMAND_UUID, packet)
            await asyncio.sleep(STOP_DELAY)
            await self.write(COMMAND_UUID, packet)

            try:
                await self.wait_for_ack()
            except TransactionTimeout:
                pass

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
                await self._connection.reconnect()
                await asyncio.sleep(0.25)

        raise TransactionError(
            "BLE transaction failed."
        ) from last_error

    async def command(self, payload: bytes) -> None:
        await self.write(COMMAND_UUID, payload)

    async def read(self, uuid: str) -> bytes:
        async def _read() -> bytes:
            return await self._connection.client.read(uuid)

        last_error: Exception | None = None

        for _ in range(MAX_RETRIES + 1):
            try:
                await self._connection.ensure_connection()
                return await _read()
            except BleakError as err:
                last_error = err
                await self._connection.reconnect()

        raise TransactionError(
            f"Failed reading {uuid}"
        ) from last_error

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
