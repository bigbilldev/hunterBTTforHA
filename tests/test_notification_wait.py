"""Tests for the per-characteristic BLE notification cache."""

import asyncio
import unittest

from hunter_btt.bluetooth.transaction import (
    HunterTransactionEngine,
    TransactionTimeout,
)
from hunter_btt.protocol.uuids import NOTIFY_UUID


class NotificationWaitTests(unittest.IsolatedAsyncioTestCase):
    async def test_wait_returns_cached_notification(self):
        engine = HunterTransactionEngine(None)
        payload = bytes.fromhex("01 00 01 01 00 00 01 01 00 00 01 01 80 00")

        await engine.notification(NOTIFY_UUID, payload)

        self.assertEqual(
            await engine.wait_for_notification(NOTIFY_UUID, timeout=0.1),
            payload,
        )

    async def test_wait_wakes_when_notification_arrives(self):
        engine = HunterTransactionEngine(None)
        waiter = asyncio.create_task(
            engine.wait_for_notification(NOTIFY_UUID, timeout=0.5)
        )
        await asyncio.sleep(0)
        payload = b"ff82-notification"

        await engine.notification(NOTIFY_UUID, payload)

        self.assertEqual(await waiter, payload)

    async def test_clear_discards_stale_notification(self):
        engine = HunterTransactionEngine(None)
        await engine.notification(NOTIFY_UUID, b"stale")
        engine.clear_notification(NOTIFY_UUID)

        with self.assertRaisesRegex(
            TransactionTimeout,
            "Timed out waiting for notification",
        ):
            await engine.wait_for_notification(NOTIFY_UUID, timeout=0.01)


if __name__ == "__main__":
    unittest.main()
