"""Regression tests for discovered GATT inventory logging."""

import logging
import unittest

from hunter_btt.bluetooth.client import HunterBLEClient
from hunter_btt.protocol.uuids import COMMAND_UUID


class FakeCharacteristic:
    def __init__(self, uuid, handle, properties):
        self.uuid = uuid
        self.handle = handle
        self.properties = properties


class FakeService:
    def __init__(self, uuid, characteristics):
        self.uuid = uuid
        self.characteristics = characteristics


class FakeBleakClient:
    def __init__(self, services):
        self.services = services
        self.is_connected = True


class GattInventoryLoggingTests(unittest.TestCase):
    def test_logs_full_table_and_writable_characteristics(self):
        command = FakeCharacteristic(COMMAND_UUID, 25, ["read", "write"])
        proxy_a = FakeCharacteristic(
            "0000ffa0-0000-1000-8000-00805f9b34fb",
            31,
            ["read", "write"],
        )
        proxy_b = FakeCharacteristic(
            "0000ffa1-0000-1000-8000-00805f9b34fb",
            32,
            ["read", "write"],
        )
        notify = FakeCharacteristic(
            "0000ff82-0000-1000-8000-00805f9b34fb",
            26,
            ["notify"],
        )
        service = FakeService(
            "0000ff80-0000-1000-8000-00805f9b34fb",
            [command, proxy_a, proxy_b, notify],
        )

        client = HunterBLEClient(None, "AA:BB:CC:DD:EE:FF")
        client._client = FakeBleakClient([service])

        with self.assertLogs(
            "hunter_btt.bluetooth.client", level=logging.DEBUG
        ) as logs:
            client._log_gatt_inventory()

        output = "\n".join(logs.output)
        self.assertIn("characteristics=4", output)
        self.assertIn("FF83=present", output)
        self.assertIn("uuid=0000ffa0-0000-1000-8000-00805f9b34fb", output)
        self.assertIn("uuid=0000ffa1-0000-1000-8000-00805f9b34fb", output)
        self.assertIn("handle=31", output)
        self.assertIn("properties=['read', 'write']", output)

    def test_reports_missing_ff83_and_writable_candidates_without_mapping_them(self):
        proxy_a = FakeCharacteristic(
            "0000ffa0-0000-1000-8000-00805f9b34fb",
            31,
            ["read", "write"],
        )
        proxy_b = FakeCharacteristic(
            "0000ffa1-0000-1000-8000-00805f9b34fb",
            32,
            ["read", "write"],
        )
        service = FakeService(
            "0000ff80-0000-1000-8000-00805f9b34fb",
            [proxy_a, proxy_b],
        )

        client = HunterBLEClient(None, "AA:BB:CC:DD:EE:FF")
        client._client = FakeBleakClient([service])

        with self.assertLogs(
            "hunter_btt.bluetooth.client", level=logging.INFO
        ) as logs:
            client._log_gatt_inventory()

        output = "\n".join(logs.output)
        self.assertIn("FF83=missing", output)
        self.assertIn("writable=2", output)
        self.assertIn("uuid=0000ffa0-0000-1000-8000-00805f9b34fb", output)
        self.assertIn("uuid=0000ffa1-0000-1000-8000-00805f9b34fb", output)
        self.assertNotIn("alias", output.lower())


if __name__ == "__main__":
    unittest.main()
