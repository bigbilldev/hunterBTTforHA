"""Regression tests for notification-driven second-generation startup."""

from contextlib import asynccontextmanager
from datetime import datetime, timezone
from unittest.mock import patch
import unittest

from hunter_btt.bluetooth.manager import HunterBLEManager
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

    @asynccontextmanager
    async def transaction(self):
        yield

    async def wait_for_notification(self, uuid, *, timeout):
        self.operations.append(("notify", uuid))
        self.waits.append((uuid, timeout))
        if uuid != NOTIFY_UUID:
            raise AssertionError(f"Unexpected notification UUID: {uuid}")
        return FF82_CAPTURE

    async def read(self, uuid):
        self.operations.append(("read", uuid))
        self.reads.append(uuid)
        if uuid == NOTIFY_UUID:
            raise AssertionError("FF82 must be received through notifications, not read")
        if uuid == TIME_UUID:
            return bytes.fromhex("07 ea 08 03 0c 0f 22 01")
        if uuid == COMMAND_UUID:
            return FF83_READ_CAPTURE
        raise AssertionError(f"Unexpected GATT read: {uuid}")

    async def write(self, uuid, payload, *, response=None):
        self.operations.append(("write", uuid, bytes(payload), response))
        self.writes.append((uuid, bytes(payload), response))


class InitializationRegressionTests(unittest.IsolatedAsyncioTestCase):
    async def test_ff84_invalid_clock_aborts_before_ff83_write(self):
        manager = HunterBLEManager.__new__(HunterBLEManager)
        manager.state = HunterState()
        manager.transaction = FakeInitializationTransaction()
        manager._zone_enabled = {1: 1, 2: 1}
        manager.protocol_initialized = False

        async def invalid_clock_read(uuid):
            if uuid == TIME_UUID:
                return b"invalid"
            raise AssertionError(f"Unexpected GATT read: {uuid}")

        manager.transaction.read = invalid_clock_read
        with self.assertRaisesRegex(ValueError, "FF84 payload must be 8 bytes"):
            await manager._initialize_second_generation()

        self.assertEqual(manager.transaction.writes, [])

    async def test_ff84_read_failure_logs_gatt_context_and_does_not_write_ff83(self):
        from types import SimpleNamespace

        manager = HunterBLEManager.__new__(HunterBLEManager)
        manager.state = HunterState()
        manager.transaction = FakeInitializationTransaction()
        manager._zone_enabled = {1: 1, 2: 1}
        manager.protocol_initialized = False
        manager.connection = SimpleNamespace(
            gatt_inventory=[
                {
                    "uuid": TIME_UUID,
                    "handle": 27,
                    "properties": ["read", "write"],
                }
            ]
        )

        async def failed_clock_read(uuid):
            if uuid == TIME_UUID:
                raise RuntimeError("GATT Error 133")
            raise AssertionError(f"Unexpected GATT read: {uuid}")

        manager.transaction.read = failed_clock_read
        with self.assertLogs("hunter_btt.bluetooth.manager", level="WARNING") as logs:
            with self.assertRaisesRegex(RuntimeError, "GATT Error 133"):
                await manager._initialize_second_generation()

        self.assertIn("uuid=" + TIME_UUID, logs.output[0])
        self.assertIn("handle=27", logs.output[0])
        self.assertIn("properties=['read', 'write']", logs.output[0])
        self.assertIn("error_type=RuntimeError", logs.output[0])
        self.assertEqual(manager.transaction.writes, [])

    async def test_startup_uses_ff82_notification_and_never_reads_ff82(self):
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
        self.assertEqual(manager.transaction.reads, [TIME_UUID, COMMAND_UUID])
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
                ("read", TIME_UUID),
                ("write", TIME_UUID, expected_ff84, True),
                ("notify", NOTIFY_UUID),
                ("read", COMMAND_UUID),
                ("write", COMMAND_UUID, FF83_INIT_CAPTURE, True),
            ],
        )
        self.assertTrue(manager.protocol_initialized)
        self.assertTrue(manager.state["protocol_initialized"])


if __name__ == "__main__":
    unittest.main()
