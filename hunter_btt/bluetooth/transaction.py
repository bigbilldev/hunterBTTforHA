"""Hunter BTT transaction engine.

FF83 is deliberately disabled in this build.

The current test device is a first-generation BTT100.  Although its BLE
database exposes FF83, the characteristic rejects writes.  Therefore this
module contains an absolute FF83 block at the lowest common write path.
"""

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
    """Transaction failed or was intentionally blocked."""


class TransactionTimeout(TransactionError):
    """Timed out waiting for controller."""


class HunterTransactionEngine:
    """Serialize Hunter transactions.

    IMPORTANT:
    FF83 is hard-disabled.  There is intentionally no authorization switch
    that can enable it.  This prevents any accidental FF83 BLE write while
    the first-generation BTT100 protocol is being implemented.
    """

    def __init__(self, connection) -> None:
        self._connection = connection
        self._lock = asyncio.Lock()
        self._ack_event = asyncio.Event()
        self._last_ack: bytes | None = None

    @property
    def ff83_enabled(self) -> bool:
        """Always false in this build."""
        return False

    def set_ff83_enabled(self, enabled: bool) -> None:
        """Compatibility method; FF83 cannot be enabled."""
        if enabled:
            _LOGGER.error(
                "IGNORING request to enable FF83: FF83 is hard-disabled "
                "in the current Hunter BTT build."
            )
        else:
            _LOGGER.debug("FF83 remains hard-disabled.")

    def _assert_write_allowed(self, uuid: str) -> None:
        """Absolute FF83 safety boundary.

        This executes before _retry(), connection handling, and client.write().
        """
        if str(uuid).strip().lower() == COMMAND_UUID:
            _LOGGER.error(
                "BLOCKED FF83 WRITE before BLE I/O. "
                "No write to FF83 was attempted."
            )
            raise TransactionError(
                "FF83 is hard-disabled. No BLE write was attempted."
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
        # MUST remain before _retry().
        self._assert_write_allowed(uuid)

        async def _write() -> None:
            await self._connection.client.write(
                uuid,
                payload,
                response=response,
            )

        await self._retry(_write)

    async def start_zone(self, zone: int, runtime_seconds: int) -> None:
        """FF83 start path is intentionally unavailable."""
        raise TransactionError(
            "FF83 start is disabled. The first-generation Hunter protocol "
            "must be used for this controller."
        )

    async def stop(self) -> None:
        """FF83 stop path is intentionally unavailable."""
        raise TransactionError(
            "FF83 stop is disabled. The first-generation Hunter protocol "
            "must be used for this controller."
        )

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
        """Generic command path is disabled because it targets FF83."""
        raise TransactionError(
            "Generic FF83 command path is disabled."
        )

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
        self._assert_write_allowed(uuid)
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
