"""Regression tests for Android-compatible second-generation startup."""

from contextlib import asynccontextmanager
from datetime import datetime, timezone
from unittest.mock import patch
import unittest

from hunter_btt.bluetooth.manager import HunterBLEManager
from hunter_btt.bluetooth.transaction import (
    HunterTransactionEngine,
    TransactionReadNotPermitted,
    TransactionWriteNotPermitted,
)
from hunter_btt.models import HunterState
from hunter_btt.protocol.generation import HunterGeneration
from hunter_btt.protocol.uuids import (
    CLIENT_ID_UUID,
    COMMAND_UUID,
    NOTIFY_UUID,
    PASSCODE_UUID,
    TIME_UUID,
)


FF81_CAPTURE = bytes.fromhex("B7 B7 B7 B7 F1 64 04 91 E2 25 00 78 34 37")
FFA5_CLIENT_ID = bytes.fromhex("C8 7A 76 C4 AA 52")
FF82_CAPTURE = bytes.fromhex("01 00 01 01 00 00 01 01 00 00 01 01 80 00")
FF83_READ_CAPTURE = bytes.fromhex("01 00 02 01 00 02 01 00 00 00 00 00")
FF83_INIT_CAPTURE = bytes.fromhex("01 00 01 01 00 01 01 00 00 00 00 00")


class FakeInitializationTransaction:
    def __init__(self):
        self.reads = []
        self.writes = []
        self.operations = []
        self.write_errors = {}
        self.read_errors = {}
        self.ff82_payload = FF82_CAPTURE
        self.client_id = FFA5_CLIENT_ID

    @asynccontextmanager
    async def transaction(self):
        yield

    async def read(self, uuid):
        self.operations.append(("read", uuid))
        self.reads.append(uuid)
        if uuid == TIME_UUID:
            raise AssertionError("FF84 must be synchronized by write, never read")
        if uuid in self.read_errors:
            raise self.read_errors[uuid]
        if uuid == CLIENT_ID_UUID:
            return self.client_id
        if uuid == NOTIFY_UUID:
            return self.ff82_payload
        if uuid == COMMAND_UUID:
            return FF83_READ_CAPTURE
        raise AssertionError(f"Unexpected GATT read: {uuid}")

    async def write(self, uuid, payload, *, response=None):
        self.operations.append(("write", uuid, bytes(payload), response))
        self.writes.append((uuid, bytes(payload), response))
        if uuid in self.write_errors:
            raise self.write_errors[uuid]


class FakeGattClient:
    """Minimal GATT client used by the real transaction engine."""

    async def read(self, uuid):
        if uuid == CLIENT_ID_UUID:
            return FFA5_CLIENT_ID
        if uuid == NOTIFY_UUID:
            return FF82_CAPTURE
        if uuid == COMMAND_UUID:
            return FF83_READ_CAPTURE
        raise AssertionError(f"Unexpected GATT read: {uuid}")

    async def write(self, uuid, payload, *, response=None):
        return None


class FakeConnection:
    def __init__(self):
        self.client = FakeGattClient()

    async def ensure_connection(self):
        return None


class FakeCharacteristicConnection:
    def __init__(self, client_id_readable=True):
        self.client_id_readable = client_id_readable

    def characteristic_properties(self, uuid):
        if uuid == CLIENT_ID_UUID and self.client_id_readable:
            return {"read", "notify"}
        return set()


class InitializationRegressionTests(unittest.IsolatedAsyncioTestCase):
    def _manager(self, transaction=None, *, client_id_readable=True):
        manager = HunterBLEManager.__new__(HunterBLEManager)
        manager.state = HunterState()
        manager.transaction = transaction or FakeInitializationTransaction()
        manager.connection = FakeCharacteristicConnection(client_id_readable)
        manager.passcode = "0000"
        manager._zone_enabled = {1: 1, 2: 1}
        manager.protocol_initialized = False
        return manager

    def _fixed_clock(self):
        return patch(
            "hunter_btt.bluetooth.manager.dt_util.now",
            return_value=datetime(2026, 8, 3, 12, 15, 33, tzinfo=timezone.utc),
        )

    async def test_clock_sync_is_a_distinct_ff84_write_operation(self):
        manager = self._manager()

        with self._fixed_clock():
            await manager._synchronize_clock()

        expected = bytes.fromhex("07 ea 08 03 0c 0f 22 01")
        self.assertEqual(manager.transaction.writes, [(TIME_UUID, expected, True)])
        self.assertEqual(manager.transaction.reads, [])
        self.assertEqual(
            manager.transaction.operations,
            [("write", TIME_UUID, expected, True)],
        )

    async def test_android_startup_reads_ffa5_then_ff81_then_ff82_ff83(self):
        manager = self._manager()

        with (
            self._fixed_clock(),
            patch("hunter_btt.protocol.ff81._random_key", return_value=b"x47"),
        ):
            await manager._initialize_second_generation()

        expected_ff84 = bytes.fromhex("07 ea 08 03 0c 0f 22 01")
        self.assertEqual(
            manager.transaction.reads,
            [CLIENT_ID_UUID, NOTIFY_UUID, COMMAND_UUID],
        )
        self.assertEqual(
            manager.transaction.writes,
            [
                (PASSCODE_UUID, FF81_CAPTURE, True),
                (TIME_UUID, expected_ff84, True),
                (COMMAND_UUID, FF83_INIT_CAPTURE, True),
            ],
        )
        self.assertEqual(
            manager.transaction.operations,
            [
                ("read", CLIENT_ID_UUID),
                ("write", PASSCODE_UUID, FF81_CAPTURE, True),
                ("write", TIME_UUID, expected_ff84, True),
                ("read", NOTIFY_UUID),
                ("read", COMMAND_UUID),
                ("write", COMMAND_UUID, FF83_INIT_CAPTURE, True),
            ],
        )
        self.assertTrue(manager.protocol_initialized)
        self.assertTrue(manager.state["protocol_initialized"])


    async def test_missing_ffa5_characteristic_blocks_before_any_ff81_write(self):
        manager = self._manager(client_id_readable=False)

        with self.assertRaisesRegex(RuntimeError, "FFA5 client-ID characteristic"):
            await manager._initialize_second_generation()

        self.assertEqual(manager.transaction.reads, [])
        self.assertEqual(manager.transaction.writes, [])
        self.assertFalse(manager.protocol_initialized)
        self.assertFalse(manager.state["protocol_initialized"])

    async def test_ffa5_read_failure_blocks_ff81_and_later_initialization(self):
        transaction = FakeInitializationTransaction()
        transaction.read_errors[CLIENT_ID_UUID] = TransactionReadNotPermitted(
            "FFA5 Read Not Permitted"
        )
        manager = self._manager(transaction)

        with self.assertRaises(TransactionReadNotPermitted):
            await manager._initialize_second_generation()

        self.assertEqual(transaction.reads, [CLIENT_ID_UUID])
        self.assertEqual(transaction.writes, [])
        self.assertFalse(manager.protocol_initialized)

    async def test_invalid_ffa5_length_blocks_ff81(self):
        transaction = FakeInitializationTransaction()
        transaction.client_id = b"short"
        manager = self._manager(transaction)

        with self.assertRaisesRegex(ValueError, "six-byte client ID"):
            await manager._initialize_second_generation()

        self.assertEqual(transaction.reads, [CLIENT_ID_UUID])
        self.assertEqual(transaction.writes, [])
        self.assertFalse(manager.protocol_initialized)

    async def test_all_zero_ffa5_client_id_blocks_ff81(self):
        transaction = FakeInitializationTransaction()
        transaction.client_id = bytes(6)
        manager = self._manager(transaction)

        with self.assertRaisesRegex(ValueError, "non-zero six-byte client ID"):
            await manager._initialize_second_generation()

        self.assertEqual(transaction.reads, [CLIENT_ID_UUID])
        self.assertEqual(transaction.writes, [])
        self.assertFalse(manager.protocol_initialized)

    async def test_ff81_write_failure_stops_before_ff82_and_ff83(self):
        transaction = FakeInitializationTransaction()
        transaction.write_errors[PASSCODE_UUID] = RuntimeError("FF81 write failed")
        manager = self._manager(transaction)

        with self._fixed_clock():
            with self.assertRaises(RuntimeError):
                await manager._initialize_second_generation()

        self.assertEqual(transaction.reads, [CLIENT_ID_UUID])
        self.assertEqual([item[0] for item in transaction.writes], [PASSCODE_UUID])
        self.assertFalse(manager.protocol_initialized)
        self.assertFalse(manager.state["protocol_initialized"])

    async def test_ff82_read_denied_keeps_ff83_uninitialized_and_does_not_write(self):
        transaction = FakeInitializationTransaction()
        transaction.read_errors[NOTIFY_UUID] = TransactionReadNotPermitted(
            "Controller rejected read from FF82 (ATT 0x02 Read Not Permitted)"
        )
        manager = self._manager(transaction)

        with self._fixed_clock():
            with self.assertRaises(TransactionReadNotPermitted):
                await manager._initialize_second_generation()

        self.assertEqual(transaction.reads, [CLIENT_ID_UUID, NOTIFY_UUID])
        self.assertEqual([item[0] for item in transaction.writes], [PASSCODE_UUID, TIME_UUID])
        self.assertFalse(manager.protocol_initialized)
        self.assertFalse(manager.state["protocol_initialized"])

    async def test_ff84_att_03_is_best_effort_before_android_ff82_ff83_sequence(self):
        transaction = FakeInitializationTransaction()
        transaction.write_errors[TIME_UUID] = TransactionWriteNotPermitted(
            "Controller rejected write to FF84 (ATT 0x03 Write Not Permitted)"
        )
        manager = self._manager(transaction)

        with self._fixed_clock():
            await manager._initialize_second_generation()

        self.assertEqual(transaction.reads, [CLIENT_ID_UUID, NOTIFY_UUID, COMMAND_UUID])
        self.assertEqual([item[0] for item in transaction.writes], [PASSCODE_UUID, TIME_UUID, COMMAND_UUID])
        self.assertTrue(manager.protocol_initialized)
        self.assertTrue(manager.state["protocol_initialized"])

    async def test_other_ff84_clock_sync_errors_are_best_effort(self):
        transaction = FakeInitializationTransaction()
        transaction.write_errors[TIME_UUID] = RuntimeError("temporary clock write failure")
        manager = self._manager(transaction)

        with self._fixed_clock():
            await manager._initialize_second_generation()

        self.assertEqual(transaction.reads, [CLIENT_ID_UUID, NOTIFY_UUID, COMMAND_UUID])
        self.assertEqual(transaction.writes[-1][0], COMMAND_UUID)
        self.assertTrue(manager.protocol_initialized)

    async def test_ff83_read_failure_keeps_protocol_uninitialized(self):
        transaction = FakeInitializationTransaction()
        transaction.read_errors[COMMAND_UUID] = RuntimeError("FF83 read failed")
        manager = self._manager(transaction)

        with self._fixed_clock():
            with self.assertRaises(RuntimeError):
                await manager._initialize_second_generation()

        self.assertEqual(transaction.reads, [CLIENT_ID_UUID, NOTIFY_UUID, COMMAND_UUID])
        self.assertEqual([item[0] for item in transaction.writes], [PASSCODE_UUID, TIME_UUID])
        self.assertFalse(manager.protocol_initialized)
        self.assertFalse(manager.state["protocol_initialized"])

    async def test_ff83_write_failure_keeps_protocol_uninitialized(self):
        transaction = FakeInitializationTransaction()
        transaction.write_errors[COMMAND_UUID] = RuntimeError("FF83 write failed")
        manager = self._manager(transaction)

        with self._fixed_clock():
            with self.assertRaises(RuntimeError):
                await manager._initialize_second_generation()

        self.assertEqual([item[0] for item in transaction.writes], [PASSCODE_UUID, TIME_UUID, COMMAND_UUID])
        self.assertFalse(manager.protocol_initialized)
        self.assertFalse(manager.state["protocol_initialized"])

    async def test_ff82_notifications_remain_cached_after_initialization(self):
        transaction = HunterTransactionEngine(connection=FakeConnection())
        transaction.set_generation(HunterGeneration.SECOND)
        manager = self._manager(transaction)

        with (
            self._fixed_clock(),
            patch("hunter_btt.protocol.ff81._random_key", return_value=b"x47"),
        ):
            await manager._initialize_second_generation()

        notification = bytes.fromhex("01 00 01 01 00 00 01 01 00 00 01 01 80 00")
        await manager._handle_notification(NOTIFY_UUID, notification)

        self.assertEqual(transaction._notifications[NOTIFY_UUID], notification)
        self.assertEqual(transaction._notification_sequence[NOTIFY_UUID], 1)


if __name__ == "__main__":
    unittest.main()
