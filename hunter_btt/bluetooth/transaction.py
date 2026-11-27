"""Hunter BTT transaction engine.

Second-generation manual control follows the captured Android BLE sequence:
1. Write the requested runtime to FF86 (zone 1) or FF8B (zone 2).
2. Await the GATT write response.
3. Write the captured 12-byte ARM command to FF83 and await its response.

STOP is one FF83 write using the captured STOP command. No FF83 read is
performed before either operation.

Second-generation connection initialization is performed by the BLE manager
using the FF82/FF83/FF84 codecs. FF81 remains intentionally excluded: the
observed 14-byte FF81 value must not be treated as a passcode or hard-coded
because it differs from the four-byte serializer in the separately inspected
6.1.7 APK.
"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone
from contextlib import asynccontextmanager
from typing import Awaitable, Callable

from bleak.exc import BleakError

from ..protocol.generation import HunterGeneration
from ..protocol.uuids import (
    COMMAND_UUID,
    ZONE_CONFIG_UUID,
)

_LOGGER = logging.getLogger(__name__)

FF83_UUID = COMMAND_UUID
MAX_RUNTIME = 3600
MAX_RETRIES = 2

# Captured manual ARM and STOP writes from
# protocol/second/Some interesting results from sniff.txt.
START_ARM_PACKET = bytes.fromhex("01 00 01 01 01 01 01 00 00 00 00 00")
STOP_PACKET = bytes.fromhex("01 00 02 01 00 02 01 00 00 00 00 00")

# Captured FF86 duration-write structure. The runtime occupies zmHour,
# zmMinute and zmSecond (bytes 11..13) in Second_86_Protocol.a().
# The capture confirms this 0x7f ztmDays variant for a 10-minute run. It also
# contains a successful 10-second run with byte 2 set to 0x04; the reason for
# that state difference is unresolved, so do not infer that 0x7f is universal.
_DURATION_TEMPLATE = bytes.fromhex(
    "04 01 7f ff ff ff ff 00 ff ff ff 00 00 00 00 1e 00"
)


class TransactionError(RuntimeError):
    """A Hunter BLE transaction failed."""


class TransactionWriteNotPermitted(TransactionError):
    """The controller explicitly rejected a GATT write with ATT 0x03."""


class TransactionTimeout(TransactionError):
    """A Hunter BLE transaction timed out."""


def _is_att_write_not_permitted(error: BaseException) -> bool:
    """Identify the controller's permanent ATT Write Not Permitted rejection."""
    current: BaseException | None = error
    visited: set[int] = set()
    while current is not None and id(current) not in visited:
        visited.add(id(current))
        message = str(current).casefold()
        if "write not permitted" in message:
            return True
        if (
            ("error=3" in message or "error = 3" in message or "0x03" in message)
            and ("att" in message or "write" in message)
        ):
            return True
        current = current.__cause__ or current.__context__
    return False


def _hms(seconds: int) -> tuple[int, int, int]:
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    if hours > 255:
        raise TransactionError("Runtime exceeds the 1-byte hour field.")
    return hours, minutes, seconds


def build_zone_duration_packet(runtime_seconds: int) -> bytes:
    """Encode the captured 17-byte Second_86 manual duration packet.

    Source field order: ais/Second_86_Protocol.java. Captured examples for
    10 seconds, 35 seconds, 10 minutes and 10 hours place the runtime in
    zmHour/zmMinute/zmSecond (offsets 11, 12 and 13).
    """
    if not 0 < runtime_seconds <= MAX_RUNTIME:
        raise TransactionError(
            f"Runtime must be between 1 and {MAX_RUNTIME} seconds."
        )
    hours, minutes, seconds = _hms(runtime_seconds)
    packet = bytearray(_DURATION_TEMPLATE)
    packet[11:14] = bytes((hours, minutes, seconds))
    return bytes(packet)


def build_start_arm_packet(zone: int, runtime_seconds: int) -> bytes:
    """Return the captured FF83 ARM payload after validating the request.

    The duration is sent separately to the zone's FF86/FF8B characteristic.
    The captured FF83 ARM packet is identical for either zone.
    """
    if zone not in (1, 2):
        raise TransactionError(f"Unsupported zone {zone}.")
    # Validate duration here as well, so callers cannot build an ARM command
    # for an invalid runtime without also building the duration packet.
    build_zone_duration_packet(runtime_seconds)
    return START_ARM_PACKET


def build_stop_packet() -> bytes:
    """Return the captured single-write FF83 STOP payload."""
    return STOP_PACKET


class HunterTransactionEngine:
    """Serialize Hunter protocol operations."""

    def __init__(self, connection) -> None:
        self._connection = connection
        self._lock = asyncio.Lock()
        self._ack_event = asyncio.Event()
        self._last_ack: bytes | None = None
        self._notifications: dict[str, bytes] = {}
        self._notification_events: dict[str, asyncio.Event] = {}
        self._notification_sequence: dict[str, int] = {}
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

    def set_ff83_enabled(self, enabled: bool) -> None:
        """Compatibility API retained for existing manager/config code."""
        self.set_generation(
            HunterGeneration.SECOND if enabled else HunterGeneration.FIRST
        )

    async def notification(self, uuid: str, payload: bytes) -> None:
        """Cache a characteristic notification and wake its waiter."""
        key = str(uuid).strip().lower()
        value = bytes(payload)
        self._notifications[key] = value
        sequence = self._notification_sequence.get(key, 0) + 1
        self._notification_sequence[key] = sequence
        self._last_ack = value
        self._ack_event.set()
        event = self._notification_events.get(key)
        received_at = datetime.now(timezone.utc).isoformat(timespec="milliseconds")
        if key == "0000ff82-0000-1000-8000-00805f9b34fb":
            _LOGGER.info(
                "Hunter FF82 notification cached at=%s sequence=%d payload_len=%d "
                "payload=%s waiter_registered=%s",
                received_at,
                sequence,
                len(value),
                value.hex(" "),
                event is not None,
            )
        if event is not None:
            event.set()

    def clear_notification(self, uuid: str) -> None:
        """Discard a cached value before starting a new BLE subscription."""
        key = str(uuid).strip().lower()
        self._notifications.pop(key, None)
        event = self._notification_events.get(key)
        if event is not None:
            event.clear()
        if key == "0000ff82-0000-1000-8000-00805f9b34fb":
            _LOGGER.debug("Hunter FF82 notification cache cleared for new connection")

    async def wait_for_notification(
        self,
        uuid: str,
        *,
        timeout: float = 8.0,
    ) -> bytes:
        """Wait for the next cached notification value for a characteristic."""
        key = str(uuid).strip().lower()
        cached = self._notifications.get(key)
        if cached is not None:
            if key == "0000ff82-0000-1000-8000-00805f9b34fb":
                _LOGGER.info(
                    "Hunter FF82 waiter consumed notification already cached "
                    "before waiter registration: sequence=%d payload=%s",
                    self._notification_sequence.get(key, 0),
                    cached.hex(" "),
                )
            return cached

        event = self._notification_events.setdefault(key, asyncio.Event())
        if key == "0000ff82-0000-1000-8000-00805f9b34fb":
            _LOGGER.info(
                "Hunter FF82 waiter registered; waiting up to %.1f seconds "
                "for notification sequence after=%d",
                timeout,
                self._notification_sequence.get(key, 0),
            )
        try:
            await asyncio.wait_for(event.wait(), timeout=timeout)
        except TimeoutError as err:
            raise TransactionTimeout(
                f"Timed out waiting for notification from {uuid}."
            ) from err

        payload = self._notifications.get(key)
        if key == "0000ff82-0000-1000-8000-00805f9b34fb" and payload is not None:
            _LOGGER.info(
                "Hunter FF82 waiter released by notification sequence=%d payload=%s",
                self._notification_sequence.get(key, 0),
                payload.hex(" "),
            )
        if payload is None:
            raise TransactionError(
                f"Notification event for {uuid} completed without a payload."
            )
        return payload

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

        await self._retry(
            operation,
            uuid=target,
            response=response,
            payload_length=len(payload),
        )

    async def start_zone(self, zone: int, runtime_seconds: int) -> None:
        """Start one zone using its duration characteristic, then FF83 ARM."""
        if self._generation is not HunterGeneration.SECOND:
            raise TransactionError(
                "START currently requires the second-generation protocol."
            )
        if zone not in ZONE_CONFIG_UUID:
            raise TransactionError(f"Unsupported zone {zone}.")

        duration_payload = build_zone_duration_packet(runtime_seconds)
        arm_payload = build_start_arm_packet(zone, runtime_seconds)
        config_uuid = ZONE_CONFIG_UUID[zone]

        async with self.transaction():
            # A response write ensures the FF86/FF8B write has completed
            # before the ARM command is issued, matching the captured order.
            await self.write(config_uuid, duration_payload, response=True)
            await self.write(FF83_UUID, arm_payload, response=True)

    async def stop(self) -> None:
        """Stop watering with one captured FF83 STOP write."""
        if self._generation is not HunterGeneration.SECOND:
            raise TransactionError(
                "STOP currently requires the second-generation protocol."
            )

        payload = build_stop_packet()
        async with self.transaction():
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
        *,
        uuid: str | None = None,
        response: bool | None = None,
        payload_length: int | None = None,
    ) -> None:
        last_error: Exception | None = None
        mode = (
            "with-response" if response is True
            else "without-response" if response is False
            else "auto"
        )
        for attempt in range(MAX_RETRIES + 1):
            try:
                await func()
                return
            except BleakError as err:
                last_error = err
                if _is_att_write_not_permitted(err):
                    handle_getter = getattr(
                        self._connection.client,
                        "characteristic_handle",
                        None,
                    )
                    handle = (
                        handle_getter(uuid)
                        if uuid is not None and callable(handle_getter)
                        else None
                    )
                    _LOGGER.error(
                        "Hunter BLE write rejected by controller: "
                        "uuid=%s handle=%s mode=%s payload_len=%s "
                        "ATT error=0x03 (Write Not Permitted); not retrying: %s",
                        uuid,
                        handle,
                        mode,
                        payload_length,
                        err,
                    )
                    raise TransactionWriteNotPermitted(
                        f"Controller rejected write to {uuid} "
                        "(ATT 0x03 Write Not Permitted); retry suppressed."
                    ) from err

                handle_getter = getattr(
                    self._connection.client,
                    "characteristic_handle",
                    None,
                )
                handle = (
                    handle_getter(uuid)
                    if uuid is not None and callable(handle_getter)
                    else None
                )
                _LOGGER.warning(
                    "BLE transaction failed uuid=%s handle=%s mode=%s "
                    "payload_len=%s attempt=%s/%s: %s",
                    uuid,
                    handle,
                    mode,
                    payload_length,
                    attempt + 1,
                    MAX_RETRIES + 1,
                    err,
                )
                if attempt < MAX_RETRIES:
                    await self._connection.reconnect()
                    await asyncio.sleep(0.25)
        raise TransactionError("BLE transaction failed.") from last_error
