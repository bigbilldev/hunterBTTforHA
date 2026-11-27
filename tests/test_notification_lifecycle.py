"""Regression tests for early FF82 notifications and exact GATT subscription."""

import asyncio
import unittest

from hunter_btt.bluetooth.client import HunterBLEClient
from hunter_btt.bluetooth.transaction import HunterTransactionEngine
from hunter_btt.protocol.uuids import NOTIFY_UUID


class FakeCharacteristic:
    def __init__(self, uuid=NOTIFY_UUID, handle=22):
        self.uuid = uuid
        self.handle = handle
        self.properties = ["notify"]


class FakeService:
    def __init__(self, characteristic):
        self.uuid = "0000ff80-0000-1000-8000-00805f9b34fb"
        self.characteristics = [characteristic]


class FakeBleakClient:
    def __init__(self, characteristic):
        self.is_connected = True
        self.services = [FakeService(characteristic)]
        self.subscribed_characteristic = None
        self.callback = None

    async def start_notify(self, characteristic, callback):
        self.subscribed_characteristic = characteristic
        self.callback = callback


class NotificationLifecycleTests(unittest.IsolatedAsyncioTestCase):
    async def test_notification_arriving_before_waiter_is_consumed_from_cache(self):
        engine = HunterTransactionEngine(connection=None)
        payload = bytes.fromhex("01 00 01 01 00 00 01 01 00 00 01 01 80 00")

        await engine.notification(NOTIFY_UUID, payload)
        result = await engine.wait_for_notification(NOTIFY_UUID, timeout=0.01)

        self.assertEqual(result, payload)
        self.assertEqual(engine._notification_sequence[NOTIFY_UUID], 1)

    async def test_notification_arriving_after_waiter_registration_releases_waiter(self):
        engine = HunterTransactionEngine(connection=None)
        payload = bytes.fromhex("01 00 01 01 00 00 01 01 00 00 01 01 80 00")
        waiter = asyncio.create_task(
            engine.wait_for_notification(NOTIFY_UUID, timeout=1.0)
        )
        await asyncio.sleep(0)
        await engine.notification(NOTIFY_UUID, payload)

        self.assertEqual(await waiter, payload)

    async def test_ff82_subscription_uses_exact_active_database_characteristic(self):
        characteristic = FakeCharacteristic()
        fake_client = FakeBleakClient(characteristic)
        client = HunterBLEClient.__new__(HunterBLEClient)
        client._client = fake_client
        client._notification_callback = lambda uuid, payload: None

        await client.start_notify(NOTIFY_UUID)

        self.assertIs(fake_client.subscribed_characteristic, characteristic)
        self.assertIsNotNone(fake_client.callback)

    async def test_ff82_callback_rejects_same_uuid_from_different_characteristic_object(self):
        characteristic = FakeCharacteristic()
        other_characteristic = FakeCharacteristic()
        fake_client = FakeBleakClient(characteristic)
        received = []
        client = HunterBLEClient.__new__(HunterBLEClient)
        client._client = fake_client
        client._notification_callback = lambda uuid, payload: received.append(
            (uuid.lower(), bytes(payload))
        )

        await client.start_notify(NOTIFY_UUID)
        fake_client.callback(other_characteristic, b"not-from-subscribed-object")

        self.assertEqual(received, [])

    async def test_ff82_callback_forwards_payload_from_expected_characteristic(self):
        characteristic = FakeCharacteristic()
        fake_client = FakeBleakClient(characteristic)
        received = []
        client = HunterBLEClient.__new__(HunterBLEClient)
        client._client = fake_client
        client._notification_callback = lambda uuid, payload: received.append(
            (uuid.lower(), bytes(payload))
        )

        await client.start_notify(NOTIFY_UUID)
        payload = bytes.fromhex("01 00 01 01 00 00 01 01 00 00 01 01 80 00")
        fake_client.callback(characteristic, payload)

        self.assertEqual(received, [(NOTIFY_UUID, payload)])


if __name__ == "__main__":
    unittest.main()
