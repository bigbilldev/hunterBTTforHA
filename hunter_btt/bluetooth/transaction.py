"""Hunter BTT BLE transaction engine.

Generation-specific manual START/STOP:
- First generation uses the proven FCD9/FCEB command characteristics.
- Second generation may use FF83 only when explicitly authorized.
- A First-generation transaction can never reach FF83.
"""

from __future__ import annotations

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Awaitable, Callable

from bleak.exc import BleakError

from ..protocol.first.commands import build_manual_start, build_manual_stop
from ..protocol.uuids import COMMAND_UUID

_LOGGER = logging.getLogger(__name__)

STOP_DELAY = 0.20
MAX_RETRIES = 2


class TransactionError(RuntimeError):
    """A BLE transaction failed."""


class TransactionTimeout(TransactionError):
    """A BLE transaction timed out."""


class HunterTransactionEngine:
    """Serialize BLE operations and keep FF83 behind an authorization boundary."""

    def __init__(self, connection) -> None:
        self._connection = connection
        self._lock = asyncio.Lock()
        self._ack_event = asyncio.Event()
        self._last_ack: bytes | None = None
        self._ff83_enabled = False

        # First-generation is the safe default until the manager explicitly
        # enables the second-generation FF83 path.
        self._generation = "first"

    @property
    def ff83_enabled(self) -> bool:
        return self._ff83_enabled

    def set_ff83_enabled(self, enabled: bool) -> None:
        """Authorize FF83 only for the second-generation path."""
        self._ff83_enabled = bool(enabled)
        self._generation = "second" if self._ff83_enabled else "first"
        _LOGGER.info(
            "Hunter transaction mode=%s FF83_authorized=%s",
            self._generation,
            self._ff83_enabled,
        )

    def set_generation(self, generation) -> None:
        """Explicitly set generation when the manager has it available."""
        value = getattr(generation, "value", generation)
        value = str(value).strip().lower()

        if value == "first":
            self._generation = "first"
            self._ff83_enabled = False
        elif value == "second":
            self._generation = "second"
        else:
            self._generation = "first"
            self._ff83_enabled = False

        _LOGGER.info(
            "Hunter transaction generation=%s FF83_authorized=%s",
            self._generation,
            self._ff83_enabled,
        )

    def _assert_ff83_allowed(self, uuid: str) -> None:
        if str(uuid).strip().lower() == COMMAND_UUID.lower():
            if self._generation != "second" or not self._ff83_enabled:
                raise TransactionError(
                    "FF83 write blocked: First-generation Hunter protocol "
                    "is active."
                )

    async def notification(self, uuid: str, payload: bytes) -> None:
        """Accept protocol acknowledgements supplied by notifications."""
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
        response: bool = True,
    ) -> None:
        """Write a characteristic with retry/reconnect handling."""
        self._assert_ff83_allowed(uuid)

        async def _write() -> None:
            await self._connection.client.write(
                uuid,
                payload,
                response=response,
            )

        await self._retry(_write)

    async def read(self, uuid: str) -> bytes:
        """Read a characteristic with retry/reconnect handling."""

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
        """Start a zone using the generation-specific proven path."""
        if runtime_seconds <= 0:
            raise TransactionError("Runtime must be greater than zero.")

        if self._generation == "first":
            # BTT100 is the currently proven first-generation device.
            # The repository's first-generation command builder maps
            # select_mode 0 -> FCD9 and select_mode 1 -> FCEB.
            #
            # Do NOT call self.write(COMMAND_UUID, ...) here.
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
                await self.write(
                    command.uuid,
                    command.payload,
                )

            return

        # Second-generation path only.
        if not self._ff83_enabled:
            raise TransactionError(
                "Second-generation transaction requested without FF83 "
                "authorization."
            )

        # Import lazily so first-generation execution has no dependency on
        # second-generation packet builders.
        from ..protocol.packets import (
            build_arm_packet,
            build_duration_packet,
            build_prepare_packet,
        )

        async with self.transaction():
            await self.write(COMMAND_UUID, build_prepare_packet(zone))
            await asyncio.sleep(0.20)
            await self.write(
                COMMAND_UUID,
                build_duration_packet(runtime_seconds),
            )
            await asyncio.sleep(0.50)
            await self.write(COMMAND_UUID, build_arm_packet(zone))

    async def stop(self) -> None:
        """Stop watering using the generation-specific proven path."""
        if self._generation == "first":
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
                await self.write(
                    command.uuid,
                    command.payload,
                )

            return

        if not self._ff83_enabled:
            raise TransactionError(
                "Second-generation transaction requested without FF83 "
                "authorization."
            )

        from ..protocol.packets import build_stop_packet

        packet = build_stop_packet()

        async with self.transaction():
            await self.write(COMMAND_UUID, packet)
            await asyncio.sleep(STOP_DELAY)
            await self.write(COMMAND_UUID, packet)

    async def command(self, payload: bytes) -> None:
        """Send a second-generation FF83 command only when authorized."""
        if self._generation != "second" or not self._ff83_enabled:
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
