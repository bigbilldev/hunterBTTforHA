"""Regression tests for Android second-generation CCCD subscription order."""

from types import SimpleNamespace
import unittest

from hunter_btt.bluetooth.client import HunterBLEClient
from hunter_btt.protocol.uuids import (
    BATTERY_LEVEL_UUID,
    SECOND_GEN_INIT_NOTIFICATION_UUIDS,
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
