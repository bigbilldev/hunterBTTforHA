"""Regression tests for notification-driven second-generation startup."""

from contextlib import asynccontextmanager
import unittest

from hunter_btt.bluetooth.manager import HunterBLEManager
from hunter_btt.models import HunterState
from hunter_btt.protocol.uuids import COMMAND_UUID, NOTIFY_UUID


FF82_CAPTURE = bytes.fromhex("01 00 01 01 00 00 01 01 00 00 01 01 80 00")
FF83_READ_CAPTURE = bytes.fromhex("01 00 02 01 00 02 01 00 00 00 00 00")
FF83_INIT_CAPTURE = bytes.fromhex("01 00 01 01 00 01 01 00 00 00 00 00")


class FakeInitializationTransaction:
    def __init__(self):
        self.reads = []
        self.waits = []
        self.writes = []

    @asynccontextmanager
    async def transaction(self):
        yield

    async def wait_for_notification(self, uuid, *, timeout):
        self.waits.append((uuid, timeout))
        if uuid != NOTIFY_UUID:
            raise AssertionError(f"Unexpected notification UUID: {uuid}")
        return FF82_CAPTURE

    async def read(self, uuid):
        self.reads.append(uuid)
        if uuid == NOTIFY_UUID:
            raise AssertionError("FF82 must be received through notifications, not read")
        if uuid == COMMAND_UUID:
            return FF83_READ_CAPTURE
        raise AssertionError(f"Unexpected GATT read: {uuid}")

    async def write(self, uuid, payload, *, response=None):
        self.writes.append((uuid, bytes(payload), response))


class InitializationRegressionTests(unittest.IsolatedAsyncioTestCase):
    async def test_startup_uses_ff82_notification_and_never_reads_ff82(self):
        manager = HunterBLEManager.__new__(HunterBLEManager)
        manager.state = HunterState()
        manager.transaction = FakeInitializationTransaction()
        manager._zone_enabled = {1: 1, 2: 1}
        manager.protocol_initialized = False

        await manager._initialize_second_generation()

        self.assertEqual(manager.transaction.waits, [(NOTIFY_UUID, 8.0)])
        self.assertEqual(manager.transaction.reads, [COMMAND_UUID])
        self.assertEqual(
            manager.transaction.writes,
            [(COMMAND_UUID, FF83_INIT_CAPTURE, True)],
        )
        self.assertTrue(manager.protocol_initialized)
        self.assertTrue(manager.state["protocol_initialized"])
        self.assertEqual(manager.state["ff82_status"]["zone1_state"], 1)


if __name__ == "__main__":
    unittest.main()
