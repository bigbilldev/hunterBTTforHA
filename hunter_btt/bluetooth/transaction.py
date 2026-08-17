"""Hunter BTT generation-specific BLE transaction engine.

FIRST generation:
    Manual START/STOP use the Android-derived First_D9 / First_EB protocol
    characteristics.  FF83 is structurally inaccessible from this path.

SECOND generation:
    FF83 remains available only when the manager explicitly selects SECOND.

The generation is deliberately explicit so a first-generation controller
cannot accidentally fall through into the FF83 code.
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

        # Unknown is intentionally NOT treated as second-generation.
        self._generation = HunterGeneration.UNKNOWN

    @property
    def generation(self) -> HunterGeneration:
        """Return the currently selected generation."""
        return self._generation

    @property
    def ff83_enabled(self) -> bool:
        """Return whether FF83 is permitted."""
        return self._generation is HunterGeneration.SECOND

    def set_generation(self, generation: HunterGeneration) -> None:
        """Set the generation selected by the manager.

        There is no independent generation inference in this class.
        """
        if not isinstance(generation, HunterGeneration):
            try:
                generation = HunterGeneration(
                    str(getattr(generation, "value", generation)).strip().lower()
                )
            except ValueError:
                generation = HunterGeneration.UNKNOWN

        self._generation = generation

        _LOGGER.info(
            "Hunter transaction generation=%s FF83_allowed=%s",
            generation.value,
            generation is HunterGeneration.SECOND,
        )

    # Backward-compatible API used by older manager revisions.
    def set_ff83_enabled(self, enabled: bool) -> None:
        """Compatibility wrapper; enabled means SECOND, disabled means FIRST."""
        self.set_generation(
            HunterGeneration.SECOND if enabled else HunterGeneration.FIRST
        )

    def _assert_write_allowed(self, uuid: str) -> None:
        """Block FF83 unless SECOND is explicitly selected."""
        normalized = str(uuid).strip().lower()
        if normalized == COMMAND_UUID.lower():
            if self._generation is not HunterGeneration.SECOND:
                raise TransactionError(
                    "FF83 write blocked: controller is not explicitly "
                    "identified as second-generation."
                )

    async def notification(self, uuid: str, payload: bytes) -> None:
        """Accept protocol acknowledgement notifications."""
        self._last_ack = bytes(payload)
        self._ack_event.set()

    @asynccontextmanager
    async def transaction(self):
        """Serialize one BLE transaction."""
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
        self._assert_write_allowed(uuid)

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
        """Wait for a notification acknowledgement."""
        try:
            await asyncio.wait_for(self._ack_event.wait(), timeout)
        except TimeoutError as exc:
            raise TransactionTimeout(
                "Timed out waiting for Hunter acknowledgement."
            ) from exc

        return self._last_ack or b""

    async def start_zone(self, zone: int, runtime_seconds: int) -> None:
        """Start a zone using the selected generation's protocol."""
        if runtime_seconds <= 0:
            raise TransactionError("Runtime must be greater than zero.")

        if self._generation is HunterGeneration.FIRST:
            # BTT100 / first-generation Android protocol.
            #
            # select_mode=0 -> First_D9
            # select_mode=1 -> First_EB
            #
            # These writes are completely separate from FF83.
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
                # Deliberately call the underlying characteristic write path
                # with the FIRST characteristic.  COMMAND_UUID/FF83 cannot be
                # reached from this branch.
                await self.write(
                    command.uuid,
                    command.payload,
                )
            return

        if self._generation is not HunterGeneration.SECOND:
            raise TransactionError(
                "Hunter protocol generation is unknown; refusing to write."
            )

        # SECOND generation only.
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
        """Stop watering using the selected generation's protocol."""

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
                await self.write(
                    command.uuid,
                    command.payload,
                )
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
        """Send a generic FF83 command only for SECOND generation."""
        if self._generation is not HunterGeneration.SECOND:
            raise TransactionError(
                "Generic FF83 command blocked: controller is not "
                "second-generation."
            )

        await self.write(COMMAND_UUID, payload)

    async def write_characteristic(
        self,
        uuid: str,
        payload: bytes,
    ) -> None:
        """Write a generation-independent characteristic."""
        await self.write(uuid, payload)

    async def execute_sequence(
        self,
        *operations: Callable[[], Awaitable[None]],
    ) -> None:
        """Execute serialized BLE operations."""
        async with self.transaction():
            for operation in operations:
                await operation()

    async def _retry(
        self,
        func: Callable[[], Awaitable[None]],
    ) -> None:
        """Retry failed BLE writes after reconnecting."""
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
