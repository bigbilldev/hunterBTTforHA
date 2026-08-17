"""Hunter BTT transaction engine.

Second-generation START/STOP follows the decompiled Android model for
Second_83_Protocol.  FF83 is a single 12-byte state/command structure;
the older prepare/duration/arm sequence is NOT used here.

The Android wrapper queues a normal BluetoothGatt.writeCharacteristic()
operation.  Therefore the caller uses write-with-response for FF83.
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
STOP_DELAY = 0.20
MAX_RETRIES = 2
MAX_RUNTIME = 3600


class TransactionError(RuntimeError):
    """A Hunter BLE transaction failed."""


class TransactionTimeout(TransactionError):
    """A Hunter BLE transaction timed out."""


def _hms(seconds: int) -> tuple[int, int, int]:
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return hours, minutes, seconds


def _encode_83(
    *,
    enabled: bool,
    suspend: int,
    zone1_enabled: int,
    zone1_mode: int,
    zone1_manual: bool,
    zone2_enabled: int,
    zone2_mode: int,
    zone2_manual: bool,
    run_seconds: int,
    special: int,
) -> bytes:
    """Serialize the exact Second_83_Protocol.a() field order."""
    hh, mm, ss = _hms(run_seconds)
    return bytes(
        (
            1 if enabled else 0,
            suspend & 0xFF,
            zone1_enabled & 0xFF,
            zone1_mode & 0xFF,
            1 if zone1_manual else 0,
            zone2_enabled & 0xFF,
            zone2_mode & 0xFF,
            1 if zone2_manual else 0,
            hh,
            mm,
            ss,
            special & 0xFF,
        )
    )


def _mutate_start(current: bytes, zone: int, runtime: int) -> bytes:
    """Mutate an existing FF83 state rather than inventing unrelated fields."""
    if len(current) != 12:
        raise TransactionError(
            f"FF83 returned {len(current)} bytes; expected 12."
        )
    if zone not in (1, 2):
        raise TransactionError(f"Unsupported zone {zone}.")
    if not 0 < runtime <= MAX_RUNTIME:
        raise TransactionError(
            f"Runtime must be between 1 and {MAX_RUNTIME} seconds."
        )

    # Second_83_Protocol field order from the Android source:
    # 0 enabled
    # 1 suspendWatering
    # 2 zone1Enabled
    # 3 zone1Mode
    # 4 zone1EnableManual
    # 5 zone2Enabled
    # 6 zone2Mode
    # 7 zone2EnableManual
    # 8..10 runAllHH/MM/SS
    # 11 specialSetting
    data = bytearray(current)
    data[0] = 1

    if zone == 1:
        data[2] = 1
        data[3] = 2
        data[4] = 1
        data[7] = 0
    else:
        data[5] = 1
        data[6] = 2
        data[7] = 1
        data[4] = 0

    hh, mm, ss = _hms(runtime)
    data[8:11] = bytes((hh, mm, ss))
    return bytes(data)


def _mutate_stop(current: bytes) -> bytes:
    """Create the Android Second_83 representation of a stopped controller."""
    if len(current) != 12:
        raise TransactionError(
            f"FF83 returned {len(current)} bytes; expected 12."
        )

    data = bytearray(current)
    data[0] = 0
    data[4] = 0
    data[7] = 0
    data[8:11] = b"\x00\x00\x00"
    return bytes(data)


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

        last_error = None
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
        if (
            str(uuid).strip().lower() == FF83_UUID.lower()
            and self._generation is not HunterGeneration.SECOND
        ):
            raise TransactionError(
                "FF83 write blocked: controller is not second-generation."
            )

        async def operation() -> None:
            await self._connection.ensure_connection()
            # Android BleWrapper.commitTransactionToBT() calls
            # BluetoothGatt.writeCharacteristic(), i.e. the normal
            # acknowledged write operation.
            await self._connection.client.write(
                uuid,
                payload,
                response=True if uuid.lower() == FF83_UUID.lower() else response,
            )

        await self._retry(operation)

    async def start_zone(self, zone: int, runtime_seconds: int) -> None:
        if self._generation is not HunterGeneration.SECOND:
            raise TransactionError(
                "START currently requires the second-generation protocol."
            )

        async with self.transaction():
            # Android Second_83_Protocol is a complete 12-byte structure.
            # Read the current state first, mutate only command-relevant
            # fields, then perform one normal GATT write.
            current = await self.read(FF83_UUID)
            payload = _mutate_start(current, zone, runtime_seconds)

            _LOGGER.info(
                "SECOND START: FF83 read=%s write=%s",
                current.hex(" "),
                payload.hex(" "),
            )
            await self.write(FF83_UUID, payload, response=True)

    async def stop(self) -> None:
        if self._generation is not HunterGeneration.SECOND:
            raise TransactionError(
                "STOP currently requires the second-generation protocol."
            )

        async with self.transaction():
            current = await self.read(FF83_UUID)
            payload = _mutate_stop(current)

            _LOGGER.info(
                "SECOND STOP: FF83 read=%s write=%s",
                current.hex(" "),
                payload.hex(" "),
            )
            await self.write(FF83_UUID, payload, response=True)

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
            raise TransactionError("Second-generation FF83 commands must be 12 bytes.")
        await self.write(FF83_UUID, payload, response=True)

    async def write_characteristic(self, uuid: str, payload: bytes) -> None:
        await self.write(uuid, payload)

    async def execute_sequence(
        self,
        *operations: Callable[[], Awaitable[None]],
    ) -> None:
        async with self.transaction():
            for operation in operations:
                await operation()

    async def _retry(self, func: Callable[[], Awaitable[None]]) -> None:
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
