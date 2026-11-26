"""Tests for BLE notification subscription and receive diagnostics."""

import unittest

from hunter_btt.bluetooth.client import HunterBLEClient
from hunter_btt.protocol.uuids import COUNTDOWN_UUID, NOTIFY_UUID, STATUS_NOTIFY_UUID


class FakeCharacteristic:
    def __init__(self, uuid, handle, properties):
        self.uuid = uuid
        self.handle = handle
        self.properties = properties


class FakeService:
    def __init__(self, characteristics):
        self.uuid = "0000ff80-0000-1000-8000-00805f9b34fb"
        self.characteristics = characteristics


class FakeBleakClient:
    def __init__(self, characteristics):
        self.services = [FakeService(characteristics)]
        self.is_connected = True
        self.callbacks = {}

    async def start_notify(self, uuid, callback):
        self.callbacks[uuid] = callback


class NotificationDiagnosticsTests(unittest.IsolatedAsyncioTestCase):
    async def test_subscription_status_and_notification_receipt_are_logged(self):
        characteristics = [
            FakeCharacteristic(NOTIFY_UUID, 22, ["notify"]),
            FakeCharacteristic(COUNTDOWN_UUID, 39, ["indicate"]),
            FakeCharacteristic(STATUS_NOTIFY_UUID, 50, ["read"]),
        ]
        fake_client = FakeBleakClient(characteristics)
        client = HunterBLEClient(None, "AA:BB:CC:DD:EE:FF")
        client._client = fake_client
        received = []

        def notification_callback(uuid, payload):
            received.append((uuid, payload))

        with self.assertLogs("hunter_btt.bluetooth.client", level="DEBUG") as logs:
            status = await client.subscribe(notification_callback)
            fake_client.callbacks[NOTIFY_UUID](
                characteristics[0],
                bytes.fromhex("01 02 03"),
            )

        self.assertEqual(status[NOTIFY_UUID], "subscribed")
        self.assertEqual(status[COUNTDOWN_UUID], "subscribed")
        self.assertEqual(status[STATUS_NOTIFY_UUID], "unsupported properties=read")
        self.assertEqual(received, [(NOTIFY_UUID, bytes.fromhex("01 02 03"))])

        output = "\n".join(logs.output)
        self.assertIn("notification subscription successful uuid=" + NOTIFY_UUID, output)
        self.assertIn("notification subscription successful uuid=" + COUNTDOWN_UUID, output)
        self.assertIn("notification subscription unavailable uuid=" + STATUS_NOTIFY_UUID, output)
        self.assertIn("notification received uuid=" + NOTIFY_UUID, output)
        self.assertIn("payload_len=3", output)


if __name__ == "__main__":
    unittest.main()
