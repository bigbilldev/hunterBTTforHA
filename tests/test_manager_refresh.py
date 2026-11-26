"""Tests for refreshing live Hunter controller values."""

import unittest
from unittest.mock import AsyncMock

from hunter_btt.bluetooth.manager import HunterBLEManager
from hunter_btt.models import HunterState
from hunter_btt.protocol.uuids import BATTERY_LEVEL_UUID


class FakeBatteryConnection:
    async def read(self, uuid):
        if uuid != BATTERY_LEVEL_UUID:
            raise AssertionError(f"Unexpected characteristic read: {uuid}")
        return bytes((76,))


class ManagerRefreshTests(unittest.IsolatedAsyncioTestCase):
    async def test_refresh_reads_and_updates_battery_level(self):
        manager = HunterBLEManager.__new__(HunterBLEManager)
        manager.connection = FakeBatteryConnection()
        manager.state = HunterState()
        manager._listeners = set()
        manager._state_callback = None
        manager.ensure_connected = AsyncMock()

        state = await manager.refresh()

        self.assertEqual(state["battery"], 76)
        self.assertEqual(manager.state.battery, 76)
        self.assertEqual(manager.ensure_connected.await_count, 1)


if __name__ == "__main__":
    unittest.main()
