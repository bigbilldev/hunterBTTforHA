"""
transaction.py

Hunter BTT201 transaction engine.

This module serializes every BLE write to the controller and implements the
command sequences discovered during reverse engineering.

Responsibilities
----------------
* Only one transaction at a time
* Retry transient BLE failures
* Execute manual watering sequences
* Execute stop sequence
* Wait for command acknowledgements
* Small delays required by Hunter firmware

This module intentionally contains NO Home Assistant entities or coordinator
logic.
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

#
# Timing discovered from reverse engineering
#

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
    """
    Executes serialized Hunter BLE transactions.

    All writes pass through this class.
    """

    def __init__(self, connection) -> None:
        self._connection = connection

        self._lock = asyncio.Lock()

        self._ack_event = asyncio.Event()

        self._last_ack: bytes | None = None

    #
    # Notification callback
    #

    async def notification(
        self,
        uuid: str,
        payload: bytes,
    ) -> None:
        """
        Receive FF82 acknowledgement.

        manager.py forwards notifications here.
        """

        if uuid.lower().endswith("ff82-0000-1000-8000-00805f9b34fb"):
            self._last_ack = payload
            self._ack_event.set()

    #
    # Synchronization
    #

    @asynccontextmanager
    async def transaction(self):
        async with self._lock:
            self._ack_event.clear()
            self._last_ack = None
            yield

    #
    # ACK waiting
    #

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

    #
    # Generic BLE write
    #

    async def write(
        self,
        uuid: str,
        payload: bytes,
        *,
        response: bool = True,
    ) -> None:

        async def _write():
            await self._connection.client.write(
                uuid,
                payload,
                response=response,
            )

        await self._retry(_write)

    #
    # Manual watering
    #

    async def start_zone(
        self,
        zone: int,
        runtime_seconds: int,
    ) -> None:
        """
        Start manual watering.

        Sequence discovered from ESP32 firmware:

            prepare
            duration
            500 ms
            arm
        """

        async with self.transaction():

            _LOGGER.debug(
                "Starting zone %s for %s sec",
                zone,
                runtime_seconds,
            )

            #
            # Prepare
            #

            await self.write(
                COMMAND_UUID,
                build_prepare_packet(zone),
            )

            await asyncio.sleep(PREPARE_DELAY)

            #
            # Runtime
            #

            await self.write(
                COMMAND_UUID,
                build_duration_packet(runtime_seconds),
            )

            await asyncio.sleep(ARM_DELAY)

            #
            # Arm
            #

            await self.write(
                COMMAND_UUID,
                build_arm_packet(zone),
            )

            #
            # Optional acknowledgement
            #

            try:
                await self.wait_for_ack()
            except TransactionTimeout:
                _LOGGER.debug(
                    "No acknowledgement received after start."
                )

    #
    # Stop
    #

    async def stop(self) -> None:
        """
        Stop watering.

        The Hunter firmware expects the stop command twice.
        """

        async with self.transaction():

            packet = build_stop_packet()

            await self.write(
                COMMAND_UUID,
                packet,
            )

            await asyncio.sleep(STOP_DELAY)

            await self.write(
                COMMAND_UUID,
                packet,
            )

            try:
                await self.wait_for_ack()
            except TransactionTimeout:
                pass

    #
    # Generic retry wrapper
    #

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

    #
    # Convenience wrappers
    #

    async def command(
        self,
        payload: bytes,
    ) -> None:
        await self.write(
            COMMAND_UUID,
            payload,
        )

    async def read(
        self,
        uuid: str,
    ) -> bytes:

        async def _read():
            return await self._connection.client.read(uuid)

        last_error = None

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
        """
        Execute several BLE operations as a single transaction.
        """

        async with self.transaction():

            for operation in operations:
                await operation()

    @property
    def busy(self) -> bool:
        return self._lock.locked()