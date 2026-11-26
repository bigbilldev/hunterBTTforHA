"""Regression tests for second-generation GATT command preflight."""

import unittest

from hunter_btt.bluetooth.manager import HunterBLEManager
from hunter_btt.bluetooth.transaction import TransactionTimeout
from hunter_btt.models import HunterState
from hunter_btt.protocol.generation import HunterGeneration
from hunter_btt.protocol.uuids import COMMAND_UUID


class FakeConnection:
    def __init__(self, command_properties):
        self._command_properties = command_properties
        self.gatt_inventory = [
            {
                "service_uuid": "0000ff80-0000-1000-8000-00805f9b34fb",
                "uuid": "0000ffa0-0000-1000-8000-00805f9b34fb",
                "handle": 25,
                "properties": ["read", "write"],
            },
            {
                "service_uuid": "0000ff80-0000-1000-8000-00805f9b34fb",
                "uuid": "0000ffa1-0000-1000-8000-00805f9b34fb",
                "handle": 26,
                "properties": ["read", "write"],
            },
        ]

    def characteristic_properties(self, uuid):
        if uuid == COMMAND_UUID:
            return self._command_properties
        return set()


class GattCommandPreflightTests(unittest.IsolatedAsyncioTestCase):
    def make_manager(self, command_properties):
        manager = HunterBLEManager.__new__(HunterBLEManager)
        manager._generation = HunterGeneration.SECOND
        manager.connection = FakeConnection(command_properties)
        manager.state = HunterState()
        manager.protocol_initialized = False
        return manager

    async def test_missing_ff83_skips_init_without_guessing_ffa_alias(self):
        manager = self.make_manager(set())

        await manager._initialize_second_generation_if_supported()

        self.assertFalse(manager.protocol_initialized)
        self.assertFalse(manager.state["protocol_initialized"])

    async def test_ff82_timeout_keeps_connection_setup_nonfatal(self):
        manager = self.make_manager({"write"})

        async def timeout_initialization():
            raise TransactionTimeout("Timed out waiting for FF82")

        manager._initialize_second_generation = timeout_initialization

        await manager._initialize_second_generation_if_supported()

        self.assertFalse(manager.protocol_initialized)
        self.assertFalse(manager.state["protocol_initialized"])

    async def test_successful_initialization_marks_protocol_ready(self):
        manager = self.make_manager({"write"})

        async def initialize():
            manager.protocol_initialized = True
            manager.state["protocol_initialized"] = True

        manager._initialize_second_generation = initialize

        await manager._initialize_second_generation_if_supported()

        self.assertTrue(manager.protocol_initialized)
        self.assertTrue(manager.state["protocol_initialized"])


if __name__ == "__main__":
    unittest.main()
