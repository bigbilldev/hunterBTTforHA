"""Regression tests for notification-driven second-generation startup."""

from contextlib import asynccontextmanager
from datetime import datetime, timezone
from unittest.mock import patch
import unittest

from hunter_btt.bluetooth.manager import HunterBLEManager
from hunter_btt.bluetooth.transaction import TransactionTimeout, TransactionWriteNotPermitted
from hunter_btt.models import HunterState
from hunter_btt.protocol.uuids import COMMAND_UUID, NOTIFY_UUID, TIME_UUID


FF82_CAPTURE = bytes.fromhex("01 00 01 01 00 00 01 01 00 00 01 01 80 00")
FF83_READ_CAPTURE = bytes.fromhex("01 00 02 01 00 02 01 00 00 00 00 00")
FF83_INIT_CAPTURE = bytes.fromhex("01 00 01 01 00 01 01 00 00 00 00 00")


class FakeInitializationTransaction:
    def __init__(self):
        self.reads = []
        self.waits = []
        self.writes = []
        self.operations = []
        self.write_errors = {}
        self.read_errors = {}
        self.wait_error = None

    @asynccontextmanager
    async def transaction(self):
        yield

    async def wait_for_notification(self, uuid, *, timeout):
        self.operations.append(("notify", uuid))
        self.waits.append((uuid, timeout))
        if uuid != NOTIFY_UUID:
            raise AssertionError(f"Unexpected notification UUID: {uuid}")
        if self.wait_error is not None:
            raise self.wait_error
        return FF82_CAPTURE

    async def read(self, uuid):
        self.operations.append(("read", uuid))
        self.reads.append(uuid)
        if uuid == TIME_UUID:
            raise AssertionError("FF84 must be synchronized by write, never read")
        if uuid == NOTIFY_UUID:
            raise AssertionError("FF82 must be received through notifications, not read")
        if uuid == COMMAND_UUID:
            if uuid in self.read_errors:
                raise self.read_errors[uuid]
            return FF83_READ_CAPTURE
        raise AssertionError(f"Unexpected GATT read: {uuid}")

    async def write(self, uuid, payload, *, response=None):
        self.operations.append(("write", uuid, bytes(payload), response))
        self.writes.append((uuid, bytes(payload), response))
        if uuid in self.write_errors:
            raise self.write_errors[uuid]


class InitializationRegressionTests(unittest.IsolatedAsyncioTestCase):
    async def test_clock_sync_is_a_distinct_ff84_write_operation(self):
        manager = HunterBLEManager.__new__(HunterBLEManager)
        manager.transaction = FakeInitializationTransaction()

        fixed_now = datetime(2026, 8, 3, 12, 15, 33, tzinfo=timezone.utc)
        with patch("hunter_btt.bluetooth.manager.dt_util.now", return_value=fixed_now):
            await manager._synchronize_clock()

        self.assertEqual(
            manager.transaction.writes,
            [(TIME_UUID, bytes.fromhex("07 ea 08 03 0c 0f 22 01"), True)],
        )
        self.assertEqual(manager.transaction.reads, [])
        self.assertEqual(
            manager.transaction.operations,
            [("write", TIME_UUID, bytes.fromhex("07 ea 08 03 0c 0f 22 01"), True)],
        )

    async def test_startup_does_not_read_ff84_and_enables_ff83_after_status_merge(self):
        manager = HunterBLEManager.__new__(HunterBLEManager)
        manager.state = HunterState()
        manager.transaction = FakeInitializationTransaction()
        manager._zone_enabled = {1: 1, 2: 1}
        manager.protocol_initialized = False

        fixed_now = datetime(2026, 8, 3, 12, 15, 33, tzinfo=timezone.utc)
        with patch("hunter_btt.bluetooth.manager.dt_util.now", return_value=fixed_now):
            await manager._initialize_second_generation()

        expected_ff84 = bytes.fromhex("07 ea 08 03 0c 0f 22 01")
        self.assertEqual(manager.transaction.waits, [(NOTIFY_UUID, 8.0)])
        self.assertEqual(manager.transaction.reads, [COMMAND_UUID])
        self.assertEqual(
            manager.transaction.writes,
            [
                (TIME_UUID, expected_ff84, True),
                (COMMAND_UUID, FF83_INIT_CAPTURE, True),
            ],
        )
        self.assertEqual(
            manager.transaction.operations,
            [
                ("write", TIME_UUID, expected_ff84, True),
                ("notify", NOTIFY_UUID),
                ("read", COMMAND_UUID),
                ("write", COMMAND_UUID, FF83_INIT_CAPTURE, True),
            ],
        )
        self.assertTrue(manager.protocol_initialized)
        self.assertTrue(manager.state["protocol_initialized"])


    async def test_ff84_att_03_is_unsupported_but_ff82_ff83_initialization_continues(self):
        manager = HunterBLEManager.__new__(HunterBLEManager)
        manager.state = HunterState()
        manager.transaction = FakeInitializationTransaction()
        manager.transaction.write_errors[TIME_UUID] = TransactionWriteNotPermitted(
            "Controller rejected write to FF84 (ATT 0x03 Write Not Permitted)"
        )
        manager._zone_enabled = {1: 1, 2: 1}
        manager.protocol_initialized = False

        fixed_now = datetime(2026, 8, 3, 12, 15, 33, tzinfo=timezone.utc)
        with patch("hunter_btt.bluetooth.manager.dt_util.now", return_value=fixed_now):
            await manager._initialize_second_generation()

        self.assertEqual(manager.transaction.waits, [(NOTIFY_UUID, 8.0)])
        self.assertEqual(manager.transaction.reads, [COMMAND_UUID])
        self.assertEqual([item[0] for item in manager.transaction.writes], [TIME_UUID, COMMAND_UUID])
        self.assertTrue(manager.protocol_initialized)
        self.assertTrue(manager.state["protocol_initialized"])

    async def test_other_ff84_clock_sync_errors_are_best_effort(self):
        manager = HunterBLEManager.__new__(HunterBLEManager)
        manager.state = HunterState()
        manager.transaction = FakeInitializationTransaction()
        manager.transaction.write_errors[TIME_UUID] = RuntimeError("temporary clock write failure")
        manager._zone_enabled = {1: 1, 2: 1}
        manager.protocol_initialized = False

        fixed_now = datetime(2026, 8, 3, 12, 15, 33, tzinfo=timezone.utc)
        with patch("hunter_btt.bluetooth.manager.dt_util.now", return_value=fixed_now):
            await manager._initialize_second_generation()

        self.assertEqual(manager.transaction.waits, [(NOTIFY_UUID, 8.0)])
        self.assertEqual(manager.transaction.reads, [COMMAND_UUID])
        self.assertEqual(manager.transaction.writes[-1][0], COMMAND_UUID)
        self.assertTrue(manager.protocol_initialized)

    async def test_missing_ff82_notification_keeps_ff83_uninitialized(self):
        manager = HunterBLEManager.__new__(HunterBLEManager)
        manager.state = HunterState()
        manager.transaction = FakeInitializationTransaction()
        manager.transaction.wait_error = TransactionTimeout("FF82 notification timeout")
        manager._zone_enabled = {1: 1, 2: 1}
        manager.protocol_initialized = False

        fixed_now = datetime(2026, 8, 3, 12, 15, 33, tzinfo=timezone.utc)
        with patch("hunter_btt.bluetooth.manager.dt_util.now", return_value=fixed_now):
            with self.assertRaises(TransactionTimeout):
                await manager._initialize_second_generation()

        self.assertEqual(manager.transaction.reads, [])
        self.assertEqual([item[0] for item in manager.transaction.writes], [TIME_UUID])
        self.assertFalse(manager.protocol_initialized)
        self.assertFalse(manager.state["protocol_initialized"])

    async def test_ff83_read_failure_keeps_protocol_uninitialized(self):
        manager = HunterBLEManager.__new__(HunterBLEManager)
        manager.state = HunterState()
        manager.transaction = FakeInitializationTransaction()
        manager.transaction.read_errors[COMMAND_UUID] = RuntimeError("FF83 read failed")
        manager._zone_enabled = {1: 1, 2: 1}
        manager.protocol_initialized = False

        fixed_now = datetime(2026, 8, 3, 12, 15, 33, tzinfo=timezone.utc)
        with patch("hunter_btt.bluetooth.manager.dt_util.now", return_value=fixed_now):
            with self.assertRaises(RuntimeError):
                await manager._initialize_second_generation()

        self.assertEqual(manager.transaction.reads, [COMMAND_UUID])
        self.assertEqual([item[0] for item in manager.transaction.writes], [TIME_UUID])
        self.assertFalse(manager.protocol_initialized)
        self.assertFalse(manager.state["protocol_initialized"])

    async def test_ff83_write_failure_keeps_protocol_uninitialized(self):
        manager = HunterBLEManager.__new__(HunterBLEManager)
        manager.state = HunterState()
        manager.transaction = FakeInitializationTransaction()
        manager.transaction.write_errors[COMMAND_UUID] = RuntimeError("FF83 write failed")
        manager._zone_enabled = {1: 1, 2: 1}
        manager.protocol_initialized = False

        fixed_now = datetime(2026, 8, 3, 12, 15, 33, tzinfo=timezone.utc)
        with patch("hunter_btt.bluetooth.manager.dt_util.now", return_value=fixed_now):
            with self.assertRaises(RuntimeError):
                await manager._initialize_second_generation()

        self.assertEqual([item[0] for item in manager.transaction.writes], [TIME_UUID, COMMAND_UUID])
        self.assertFalse(manager.protocol_initialized)
        self.assertFalse(manager.state["protocol_initialized"])



if __name__ == "__main__":
    unittest.main()
