"""Regression tests for Android second-generation CCCD subscription order."""

from types import SimpleNamespace
import unittest
from unittest.mock import patch

from hunter_btt.bluetooth.client import HunterBLEClient
from hunter_btt.bluetooth.manager import HunterBLEManager
from hunter_btt.protocol.generation import HunterCapabilities, HunterGeneration
from hunter_btt.protocol.uuids import (
    BATTERY_LEVEL_UUID,
    COMMAND_UUID,
    SECOND_GEN_INIT_NOTIFICATION_UUIDS,
    SECOND_SERVICE_UUID,
    ZONE1_CONFIG_UUID,
    ZONE2_CONFIG_UUID,
)


class NotificationSubscriptionTests(unittest.IsolatedAsyncioTestCase):
    async def test_android_cccds_are_subscribed_in_captured_order(self):
        client = HunterBLEClient.__new__(HunterBLEClient)
        client._client = SimpleNamespace(is_connected=True)
        client._notification_callback = None
        client._notification_status = {}

        subscribed = []

        def properties(_uuid):
            return {"notify", "read"}

        def handle(_uuid):
            return 42

        async def start_notify(uuid):
            subscribed.append(uuid)

        client.characteristic_properties = properties
        client.characteristic_handle = handle
        client.start_notify = start_notify

        callback = lambda _uuid, _payload: None
        status = await client.subscribe(
            callback,
            notification_uuids=SECOND_GEN_INIT_NOTIFICATION_UUIDS,
        )

        self.assertEqual(
            subscribed,
            [*SECOND_GEN_INIT_NOTIFICATION_UUIDS, BATTERY_LEVEL_UUID],
        )
        self.assertEqual(
            tuple(subscribed[:9]),
            SECOND_GEN_INIT_NOTIFICATION_UUIDS,
        )
        self.assertTrue(all(value == "subscribed" for value in status.values()))


    async def test_manager_subscribes_all_android_cccds_before_ff81_init(self):
        events = []

        class FakeConnection:
            service_uuids = {SECOND_SERVICE_UUID}
            characteristic_uuids = {
                COMMAND_UUID,
                ZONE1_CONFIG_UUID,
                ZONE2_CONFIG_UUID,
            }
            gatt_inventory = []

            async def connect(self):
                events.append("connect")

            async def disconnect(self):
                return None

            def characteristic_properties(self, uuid):
                return {"read", "write"} if uuid == COMMAND_UUID else set()

        class FakeTransaction:
            def clear_notification(self, uuid):
                return None

            def set_generation(self, generation):
                return None

        class FakeClient:
            async def subscribe(self, callback, *, notification_uuids=None):
                events.append(("subscribe", notification_uuids))
                return {}

        manager = HunterBLEManager.__new__(HunterBLEManager)
        manager._hass = None
        manager.address = "AA:BB:CC:DD:EE:FF"
        manager.name = "Hunter BTT"
        manager._zone_enabled = {1: 1, 2: 1}
        manager.protocol_initialized = False
        manager.client = FakeClient()
        manager.connection = FakeConnection()
        manager.transaction = FakeTransaction()
        manager._generation = HunterGeneration.UNKNOWN
        manager._capabilities = HunterCapabilities(
            generation=HunterGeneration.UNKNOWN,
            zone_count=0,
        )
        manager.connected = False
        manager._state_callback = None
        manager._listeners = set()
        manager.state = {}

        async def initialize():
            events.append("ff81-initialization")

        async def notify_state():
            return None

        manager._initialize_second_generation_if_supported = initialize
        manager._notify_state_changed = notify_state

        with (
            patch(
                "hunter_btt.bluetooth.manager.detect_generation",
                return_value=HunterGeneration.SECOND,
            ),
            patch(
                "hunter_btt.bluetooth.manager.detect_zone_count",
                return_value=2,
            ),
        ):
            await manager.connect()

        self.assertEqual(events[0], "connect")
        self.assertEqual(events[1][0], "subscribe")
        self.assertEqual(events[1][1], SECOND_GEN_INIT_NOTIFICATION_UUIDS)
        self.assertEqual(events[2], "ff81-initialization")

    async def test_subscription_failures_remain_independent(self):
        client = HunterBLEClient.__new__(HunterBLEClient)
        client._client = SimpleNamespace(is_connected=True)
        client._notification_callback = None
        client._notification_status = {}

        subscribed = []

        def properties(_uuid):
            return {"notify"}

        def handle(_uuid):
            return 42

        async def start_notify(uuid):
            if uuid == SECOND_GEN_INIT_NOTIFICATION_UUIDS[1]:
                raise RuntimeError("descriptor rejected")
            subscribed.append(uuid)

        client.characteristic_properties = properties
        client.characteristic_handle = handle
        client.start_notify = start_notify

        status = await client.subscribe(
            lambda _uuid, _payload: None,
            notification_uuids=SECOND_GEN_INIT_NOTIFICATION_UUIDS,
        )

        failed_uuid = SECOND_GEN_INIT_NOTIFICATION_UUIDS[1]
        self.assertTrue(status[failed_uuid].startswith("failed:"))
        self.assertIn(SECOND_GEN_INIT_NOTIFICATION_UUIDS[0], subscribed)
        self.assertIn(SECOND_GEN_INIT_NOTIFICATION_UUIDS[2], subscribed)
        self.assertEqual(len(status), 10)


if __name__ == "__main__":
    unittest.main()
