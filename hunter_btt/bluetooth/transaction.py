"""Hunter BTT transaction engine.

Second-generation START/STOP is modeled on the decompiled Android
Second_83_Protocol.  The Android wrapper constructs a fresh Second_83 object,
serializes its 12 fields, and submits that object to the BLE write path. It
does not perform a prerequisite FF83 read.

Therefore this implementation NEVER reads FF83 before START/STOP.
"""

from __future__ import annotations

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Awaitable, Callable

from bleak.exc import BleakError

from ..protocol.generation import HunterGeneration
from ..protocol.uuids import COMMAND_UUID

_LOGGER = logging.getLogger(__name__)

FF83_UUID = COMMAND_UUID
MAX_RUNTIME = 3600
MAX_RETRIES = 2


class TransactionError(RuntimeError):
    """A Hunter BLE transaction failed."""


class TransactionTimeout(TransactionError):
    """A Hunter BLE transaction timed out."""


def _hms(seconds: int) -> tuple[int, int, int]:
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    if hours > 255:
        raise TransactionError("Runtime exceeds the 1-byte hour field.")
    return hours, minutes, seconds


def _encode_second_83(
    *,
    enabled: bool,
    suspend_watering: int,
    zone1_enabled: int,
    zone1_mode: int,
    zone1_manual: bool,
    zone2_enabled: int,
    zone2_mode: int,
    zone2_manual: bool,
    run_seconds: int,
    special_setting: int,
) -> bytes:
    """Encode Second_83_Protocol.a() field order exactly.

    Source: ais/Second_83_Protocol.java:
      enabled
      suspendWatering
      zone1Enabled
      zone1Mode
      zone1EnableManual
      zone2Enabled
      zone2Mode
      zone2EnableManual
      runAllHH
      runAllMM
      runAllSS
      specialSetting
    """
    hh, mm, ss = _hms(run_seconds)
    return bytes(
        (
            1 if enabled else 0,
            suspend_watering & 0xFF,
            zone1_enabled & 0xFF,
            zone1_mode & 0xFF,
            1 if zone1_manual else 0,
            zone2_enabled & 0xFF,
            zone2_mode & 0xFF,
            1 if zone2_manual else 0,
            hh,
            mm,
            ss,
            special_setting & 0xFF,
        )
    )


def build_start_packet(zone: int, runtime_seconds: int) -> bytes:
    """Build a complete Android Second_83 START state."""
    if zone not in (1, 2):
        raise TransactionError(f"Unsupported zone {zone}.")
    if not 0 < runtime_seconds <= MAX_RUNTIME:
        raise TransactionError(
            f"Runtime must be between 1 and {MAX_RUNTIME} seconds."
        )

    return _encode_second_83(
        enabled=True,
        suspend_watering=0,
        zone1_enabled=1 if zone == 1 else 0,
        zone1_mode=2 if zone == 1 else 0,
        zone1_manual=zone == 1,
        zone2_enabled=1 if zone == 2 else 0,
        zone2_mode=2 if zone == 2 else 0,
        zone2_manual=zone == 2,
        run_seconds=runtime_seconds,
        special_setting=0,
    )


def build_stop_packet() -> bytes:
    """Build a complete Android Second_83 STOP state."""
    return _encode_second_83(
        enabled=False,
        suspend_watering=0,
        zone1_enabled=0,
        zone1_mode=0,
        zone1_manual=False,
        zone2_enabled=0,
        zone2_mode=0,
        zone2_manual=False,
        run_seconds=0,
        special_setting=0,
    )


class HunterTransactionEngine:
    """Serialize Hunter protocol operations."""

    def __init__(self, connection) -> None:
        self._connection = connection
        self._lock = asyncio.Lock()
        self._ack_event = asyncio.Event()
        self._last_ack: bytes | None = None
        self._generation = HunterGeneration.UNKNOWN

    @property
    def generation(self) -> HunterGeneration:
        return self._generation

    def set_generation(self, generation) -> None:
        value = getattr(generation, "value", generation)
        try:
            self._generation = HunterGeneration(
                str(value).strip().lower()
            )
        except ValueError:
            self._generation = HunterGeneration.UNKNOWN

    def set_ff83_enabled(self, enabled: bool) -> None:
        """Compatibility API retained for existing manager/config code."""
        self.set_generation(
            HunterGeneration.SECOND if enabled else HunterGeneration.FIRST
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

    async def read(self, uuid: str) -> bytes:
        async def operation() -> bytes:
            await self._connection.ensure_connection()
            return await self._connection.client.read(uuid)

        last_error: Exception | None = None
        for attempt in range(MAX_RETRIES + 1):
            try:
                return await operation()
            except BleakError as err:
                last_error = err
                if attempt < MAX_RETRIES:
                    await self._connection.reconnect()
                    await asyncio.sleep(0.25)
        raise TransactionError(f"Failed reading {uuid}") from last_error

    async def write(
        self,
        uuid: str,
        payload: bytes,
        *,
        response: bool | None = None,
    ) -> None:
        target = str(uuid).strip().lower()
        if target == FF83_UUID.lower():
            if self._generation is not HunterGeneration.SECOND:
                raise TransactionError(
                    "FF83 write blocked: controller is not second-generation."
                )
            if len(payload) != 12:
                raise TransactionError(
                    "Second-generation FF83 writes must contain exactly 12 bytes."
                )

        async def operation() -> None:
            await self._connection.ensure_connection()
            await self._connection.client.write(
                uuid,
                payload,
                response=response,
            )

        await self._retry(operation)

    async def start_zone(self, zone: int, runtime_seconds: int) -> None:
        """Start a zone using one Android-style FF83 write."""
        if self._generation is not HunterGeneration.SECOND:
            raise TransactionError(
                "START currently requires the second-generation protocol."
            )

        payload = build_start_packet(zone, runtime_seconds)
        _LOGGER.info(
            "SECOND START: FF83 write=%s (no FF83 read)",
            payload.hex(" "),
        )

        async with self.transaction():
            await self.write(
                FF83_UUID,
                payload,
                response=True,
            )

    async def stop(self) -> None:
        """Stop watering using one Android-style FF83 write."""
        if self._generation is not HunterGeneration.SECOND:
            raise TransactionError(
                "STOP currently requires the second-generation protocol."
            )

        payload = build_stop_packet()
        _LOGGER.info(
            "SECOND STOP: FF83 write=%s (no FF83 read)",
            payload.hex(" "),
        )

        async with self.transaction():
            await self.write(
                FF83_UUID,
                payload,
                response=True,
            )

    async def wait_for_ack(self, timeout: float = 5.0) -> bytes:
        try:
            await asyncio.wait_for(self._ack_event.wait(), timeout)
        except TimeoutError as exc:
            raise TransactionTimeout(
                "Timed out waiting for Hunter acknowledgement."
            ) from exc
        return self._last_ack or b""

    async def command(self, payload: bytes) -> None:
        if self._generation is not HunterGeneration.SECOND:
            raise TransactionError(
                "Generic FF83 command blocked for non-second-generation Hunter."
            )
        if len(payload) != 12:
            raise TransactionError(
                "Second-generation FF83 commands must be 12 bytes."
            )
        await self.write(FF83_UUID, payload, response=True)

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
