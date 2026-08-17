"""Hunter BTT transaction engine.

Second-generation START/STOP path based on the Android Second_83 protocol.

Important:
- Do NOT read FF83 before START/STOP.
- FF83 is written as a normal acknowledged GATT characteristic.
- The Android Second_83 serializer is a 12-byte structure in this order:
  enabled, suspendWatering, zone1Enabled, zone1Mode, zone1EnableManual,
  zone2Enabled, zone2Mode, zone2EnableManual, runAllHH, runAllMM,
  runAllSS, specialSetting.
- This module therefore sends a complete 12-byte FF83 packet directly.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Awaitable, Callable

from bleak.exc import BleakError

from ..protocol.generation import COMMAND_UUID
from ..protocol.uuids import FF82_UUID, FF83_UUID

_LOGGER = logging.getLogger(__name__)

MAX_RETRIES = 3
RETRY_DELAY = 0.25
STOP_DELAY = 0.20
ACK_TIMEOUT = 8.0


class TransactionError(RuntimeError):
    """Hunter BLE transaction failure."""


class TransactionTimeout(TransactionError):
    """Hunter BLE acknowledgement timeout."""


def _u8(value: int) -> int:
    return max(0, min(255, int(value)))


def build_second_83_start_packet(zone: int, runtime_seconds: int) -> bytes:
    """Build the Android Second_83 12-byte START structure.

    The Android class serializes fields in exactly this order. For manual
    watering, the controller is enabled, watering is not suspended, the
    selected zone is enabled/manual, and run-all time carries the requested
    runtime.
    """
    if zone not in (1, 2):
        raise ValueError(f"Unsupported Hunter zone: {zone}")

    runtime = max(0, int(runtime_seconds))
    hours, remainder = divmod(runtime, 3600)
    minutes, seconds = divmod(remainder, 60)

    if hours > 255:
        raise ValueError("Hunter runtime exceeds 255 hours")

    zone1_enabled = 1 if zone == 1 else 0
    zone2_enabled = 1 if zone == 2 else 0

    # Mode 1 is the manual/timer mode used by the Android protocol model.
    zone1_mode = 1 if zone == 1 else 0
    zone2_mode = 1 if zone == 2 else 0

    return bytes(
        (
            1,                  # enabled
            0,                  # suspendWatering
            zone1_enabled,      # zone1Enabled
            zone1_mode,         # zone1Mode
            zone1_enabled,      # zone1EnableManual
            zone2_enabled,      # zone2Enabled
            zone2_mode,         # zone2Mode
            zone2_enabled,      # zone2EnableManual
            _u8(hours),         # runAllHH
            _u8(minutes),       # runAllMM
            _u8(seconds),       # runAllSS
            0,                  # specialSetting
        )
    )


def build_second_83_stop_packet() -> bytes:
    """Build the Android Second_83 STOP structure."""
    return bytes(
        (
            1,  # enabled
            0,  # suspendWatering
            0,  # zone1Enabled
            0,  # zone1Mode
            0,  # zone1EnableManual
            0,  # zone2Enabled
            0,  # zone2Mode
            0,  # zone2EnableManual
            0,  # runAllHH
            0,  # runAllMM
            0,  # runAllSS
            0,  # specialSetting
        )
    )


class HunterTransactionEngine:
    """Serialize Hunter BLE commands."""

    def __init__(self, connection) -> None:
        self._connection = connection
        self._lock = asyncio.Lock()
        self._ack_event = asyncio.Event()
        self._last_ack: bytes | None = None

    async def notification(self, uuid: str, payload: bytes) -> None:
        """Accept controller notifications for command confirmation."""
        if str(uuid).strip().lower() == str(FF82_UUID).strip().lower():
            self._last_ack = bytes(payload)
            self._ack_event.set()

    async def _write_ff83(self, payload: bytes) -> None:
        if len(payload) != 12:
            raise TransactionError(
                f"FF83 requires 12 bytes; got {len(payload)}"
            )

        _LOGGER.debug(
            "Hunter FF83 write: %s",
            payload.hex(" "),
        )

        await self._connection.ensure_connection()

        # Explicitly use acknowledged/normal GATT write, matching Android's
        # BluetoothGatt.writeCharacteristic() path.
        await self._connection.client.write(
            FF83_UUID,
            payload,
            response=True,
        )

    async def _write_with_retry(self, payload: bytes) -> None:
        last_error: Exception | None = None

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                await self._write_ff83(payload)
                return
            except (BleakError, TransactionError) as err:
                last_error = err
                _LOGGER.warning(
                    "Hunter FF83 write failed (%s/%s): %s",
                    attempt,
                    MAX_RETRIES,
                    err,
                )
                if attempt < MAX_RETRIES:
                    # Reconnect only AFTER an actual write failure. Never
                    # reconnect merely because FF83 cannot/should not be read.
                    try:
                        await self._connection.reconnect()
                    except Exception as reconnect_err:
                        _LOGGER.debug(
                            "Hunter reconnect after FF83 failure failed: %s",
                            reconnect_err,
                        )
                    await asyncio.sleep(RETRY_DELAY)

        raise TransactionError("Hunter FF83 write failed") from last_error

    async def _wait_for_ack(self) -> bytes:
        try:
            await asyncio.wait_for(
                self._ack_event.wait(),
                timeout=ACK_TIMEOUT,
            )
        except TimeoutError as err:
            raise TransactionTimeout(
                "Timed out waiting for Hunter FF82 acknowledgement"
            ) from err

        return self._last_ack or b""

    async def start_zone(self, zone: int, runtime_seconds: int) -> None:
        """Start a zone without performing an FF83 read."""
        async with self._lock:
            payload = build_second_83_start_packet(
                zone,
                runtime_seconds,
            )

            self._ack_event.clear()
            self._last_ack = None

            _LOGGER.info(
                "Hunter START: zone=%s runtime=%ss FF83=%s",
                zone,
                runtime_seconds,
                payload.hex(" "),
            )

            await self._write_with_retry(payload)

            try:
                ack = await self._wait_for_ack()
                _LOGGER.info(
                    "Hunter START acknowledgement FF82=%s",
                    ack.hex(" ") if ack else "<empty>",
                )
            except TransactionTimeout:
                # The GATT write itself succeeded. Do not turn a missing
                # notification into a second command or an FF83 read.
                _LOGGER.warning(
                    "Hunter START write succeeded but no FF82 acknowledgement "
                    "arrived within %ss",
                    ACK_TIMEOUT,
                )

    async def stop(self) -> None:
        """Stop watering using the Second_83 FF83 structure."""
        async with self._lock:
            payload = build_second_83_stop_packet()

            self._ack_event.clear()
            self._last_ack = None

            _LOGGER.info(
                "Hunter STOP: FF83=%s",
                payload.hex(" "),
            )

            await self._write_with_retry(payload)
            await asyncio.sleep(STOP_DELAY)

            # Android-style command path may require the stop command to be
            # issued twice. Do not read FF83 between the two writes.
            await self._write_with_retry(payload)

            try:
                ack = await self._wait_for_ack()
                _LOGGER.info(
                    "Hunter STOP acknowledgement FF82=%s",
                    ack.hex(" ") if ack else "<empty>",
                )
            except TransactionTimeout:
                _LOGGER.warning(
                    "Hunter STOP writes succeeded but no FF82 acknowledgement "
                    "arrived within %ss",
                    ACK_TIMEOUT,
                )

    async def write(self, uuid: str, payload: bytes, *, response: bool = True) -> None:
        """Compatibility method for callers that write characteristics."""
        if str(uuid).strip().lower() == str(FF83_UUID).strip().lower():
            if not response:
                raise TransactionError(
                    "FF83 must use acknowledged GATT write"
                )
            if len(payload) != 12:
                raise TransactionError(
                    f"FF83 requires 12 bytes; got {len(payload)}"
                )
            async with self._lock:
                await self._write_with_retry(bytes(payload))
            return

        await self._connection.ensure_connection()
        await self._connection.client.write(
            uuid,
            payload,
            response=response,
        )

    async def read(self, uuid: str) -> bytes:
        """Read non-command characteristics.

        FF83 is deliberately not read by START/STOP.
        """
        await self._connection.ensure_connection()
        return await self._connection.client.read(uuid)

    async def write_characteristic(
        self,
        uuid: str,
        payload: bytes,
    ) -> None:
        await self.write(uuid, payload, response=True)

    async def command(self, payload: bytes) -> None:
        if len(payload) != 12:
            raise TransactionError("FF83 command must contain 12 bytes")
        await self.write(FF83_UUID, payload, response=True)

    @property
    def busy(self) -> bool:
        return self._lock.locked()
