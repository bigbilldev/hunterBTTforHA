"""Hunter BTT BLE transactions.

Second-generation FF83 implementation follows the decompiled Android
Second_83_Protocol: FF83 receives one serialized 12-byte state object.

The old prepare -> duration -> arm sequence is deliberately removed.
"""

from __future__ import annotations

import asyncio
import logging
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Awaitable, Callable

from bleak.exc import BleakError

from ..protocol.generation import HunterGeneration, COMMAND_UUID

_LOGGER = logging.getLogger(__name__)

MAX_RETRIES = 2
STOP_DELAY = 0.20
FF83_UUID = COMMAND_UUID


class TransactionError(RuntimeError):
    """A BLE transaction failed."""


class TransactionTimeout(TransactionError):
    """A BLE acknowledgement timed out."""


@dataclass(slots=True)
class Second83State:
    """Exact field order of Android Second_83_Protocol.a()."""

    enabled: bool = True
    suspend_watering: int = 0
    zone1_enabled: int = 0
    zone1_mode: int = 0
    zone1_enable_manual: bool = False
    zone2_enabled: int = 0
    zone2_mode: int = 0
    zone2_enable_manual: bool = False
    run_all_hh: int = 0
    run_all_mm: int = 0
    run_all_ss: int = 0
    special_setting: int = 0

    def serialize(self) -> bytes:
        """Serialize exactly as Second_83_Protocol.a()."""
        values = (
            1 if self.enabled else 0,
            self.suspend_watering & 0xFF,
            self.zone1_enabled & 0xFF,
            self.zone1_mode & 0xFF,
            1 if self.zone1_enable_manual else 0,
            self.zone2_enabled & 0xFF,
            self.zone2_mode & 0xFF,
            1 if self.zone2_enable_manual else 0,
            self.run_all_hh & 0xFF,
            self.run_all_mm & 0xFF,
            self.run_all_ss & 0xFF,
            self.special_setting & 0xFF,
        )
        return bytes(values)

    @classmethod
    def deserialize(cls, payload: bytes) -> "Second83State":
        """Decode an FF83 state returned by a compatible controller."""
        if len(payload) != 12:
            raise TransactionError(
                f"FF83 state must be 12 bytes, received {len(payload)}"
            )

        return cls(
            enabled=payload[0] != 0,
            suspend_watering=payload[1],
            zone1_enabled=payload[2],
            zone1_mode=payload[3],
            zone1_enable_manual=payload[4] != 0,
            zone2_enabled=payload[5],
            zone2_mode=payload[6],
            zone2_enable_manual=payload[7] != 0,
            run_all_hh=payload[8],
            run_all_mm=payload[9],
            run_all_ss=payload[10],
            special_setting=payload[11],
        )


def build_second83_start(zone: int, runtime_seconds: int) -> bytes:
    """Build the complete 12-byte FF83 manual-start state.

    This is intentionally based on the serialized Second_83_Protocol shape,
    not the former three-write prepare/duration/arm sequence.

    runtime is represented by runAllHH/MM/SS because those are the only
    duration fields in Second_83_Protocol.  The Android source confirms the
    field order, but does not document a separate FF83 duration command.
    """
    if zone not in (1, 2):
        raise TransactionError("Zone must be 1 or 2.")
    if not 1 <= runtime_seconds <= 3599:
        raise TransactionError("Runtime must be between 1 and 3599 seconds.")

    hours = runtime_seconds // 3600
    minutes = (runtime_seconds % 3600) // 60
    seconds = runtime_seconds % 60

    # The decompiled prepare/arm payloads in the project were already
    # 12-byte Second_83-compatible structures.  The only state change used
    # for manual activation is the zone's manual-enable byte.
    return Second83State(
        enabled=True,
        suspend_watering=0,
        zone1_enabled=zone,
        zone1_mode=0x02,
        zone1_enable_manual=True,
        zone2_enabled=0,
        zone2_mode=0,
        zone2_enable_manual=False,
        run_all_hh=hours,
        run_all_mm=minutes,
        run_all_ss=seconds,
        special_setting=0,
    ).serialize()


def build_second83_stop() -> bytes:
    """Build a complete FF83 state that disables both zones."""
    return Second83State(
        enabled=True,
        suspend_watering=0,
        zone1_enabled=0,
        zone1_mode=0,
        zone1_enable_manual=False,
        zone2_enabled=0,
        zone2_mode=0,
        zone2_enable_manual=False,
        run_all_hh=0,
        run_all_mm=0,
        run_all_ss=0,
        special_setting=0,
    ).serialize()


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

    def set_generation(self, generation) -> None:
        value = getattr(generation, "value", generation)
        try:
            self._generation = HunterGeneration(str(value).strip().lower())
        except ValueError:
            self._generation = HunterGeneration.UNKNOWN

        _LOGGER.info(
            "Hunter transaction generation=%s",
            self._generation.value,
        )

    def set_ff83_enabled(self, enabled: bool) -> None:
        """Compatibility with older manager revisions."""
        self.set_generation(
            HunterGeneration.SECOND if enabled else HunterGeneration.FIRST
        )

    @asynccontextmanager
    async def transaction(self):
        async with self._lock:
            self._ack_event.clear()
            self._last_ack = None
            yield

    async def notification(self, uuid: str, payload: bytes) -> None:
        self._last_ack = bytes(payload)
        self._ack_event.set()

    async def wait_for_ack(self, timeout: float = 5.0) -> bytes:
        try:
            await asyncio.wait_for(self._ack_event.wait(), timeout)
        except TimeoutError as exc:
            raise TransactionTimeout(
                "Timed out waiting for Hunter acknowledgement."
            ) from exc
        return self._last_ack or b""

    def _ff83_response_mode(self) -> bool:
        """Choose the BLE write mode from the actual GATT properties.

        ESPHome error 3 occurs when a write is requested using a mode the
        characteristic does not permit.  Do not blindly force response=True.
        """
        properties = set()

        client = self._connection.client
        getter = getattr(client, "characteristic_properties", None)
        if getter is not None:
            try:
                properties = {
                    str(p).strip().lower()
                    for p in getter(FF83_UUID)
                }
            except Exception:
                properties = set()

        if "write" in properties:
            return True
        if "write-without-response" in properties:
            return False

        # If the backend does not expose properties, retain Bleak's normal
        # write-with-response behavior rather than guessing a new protocol.
        return True

    async def write(
        self,
        uuid: str,
        payload: bytes,
        *,
        response: bool | None = None,
    ) -> None:
        normalized = str(uuid).strip().lower()

        if normalized == FF83_UUID.lower():
            if self._generation is not HunterGeneration.SECOND:
                raise TransactionError(
                    "FF83 write refused: controller is not SECOND generation."
                )
            if len(payload) != 12:
                raise TransactionError(
                    f"FF83 requires exactly 12 bytes, received {len(payload)}."
                )
            if response is None:
                response = self._ff83_response_mode()

        async def _write() -> None:
            await self._connection.client.write(
                uuid,
                payload,
                response=response if response is not None else True,
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
                if attempt < MAX_RETRIES:
                    await self._connection.reconnect()
                    await asyncio.sleep(0.25)

        raise TransactionError(f"Failed reading {uuid}") from last_error

    async def start_zone(self, zone: int, runtime_seconds: int) -> None:
        """Write one complete Second_83 state for manual START."""
        if self._generation is not HunterGeneration.SECOND:
            raise TransactionError(
                "Second_83 START requested but controller is not SECOND generation."
            )

        payload = build_second83_start(zone, runtime_seconds)

        _LOGGER.info(
            "SECOND START FF83: zone=%d runtime=%d payload=%s",
            zone,
            runtime_seconds,
            payload.hex(" "),
        )

        async with self.transaction():
            # Exactly ONE FF83 write.  No prepare, duration, or arm writes.
            await self.write(FF83_UUID, payload)

    async def stop(self) -> None:
        """Write one complete Second_83 state that disables watering."""
        if self._generation is not HunterGeneration.SECOND:
            raise TransactionError(
                "Second_83 STOP requested but controller is not SECOND generation."
            )

        payload = build_second83_stop()

        _LOGGER.info(
            "SECOND STOP FF83: payload=%s",
            payload.hex(" "),
        )

        async with self.transaction():
            await self.write(FF83_UUID, payload)

    async def command(self, payload: bytes) -> None:
        """Compatibility API for callers that explicitly send FF83 state."""
        if self._generation is not HunterGeneration.SECOND:
            raise TransactionError(
                "FF83 command refused: controller is not SECOND generation."
            )
        if len(payload) != 12:
            raise TransactionError(
                f"FF83 requires exactly 12 bytes, received {len(payload)}."
            )
        await self.write(FF83_UUID, payload)

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
