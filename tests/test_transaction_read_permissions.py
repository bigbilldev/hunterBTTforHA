"""Tests for permanent ATT read-permission failures."""

import unittest

from bleak.exc import BleakError

from hunter_btt.bluetooth.transaction import (
    HunterTransactionEngine,
    TransactionReadNotPermitted,
)
from hunter_btt.protocol.uuids import NOTIFY_UUID


class FakeConnection:
    def __init__(self, error):
        self.error = error
        self.client = self
        self.reconnects = 0
        self.reads = []

    async def ensure_connection(self):
        return None

    async def read(self, uuid):
        self.reads.append(uuid)
        raise self.error

    async def reconnect(self):
        self.reconnects += 1


class TransactionReadPermissionTests(unittest.IsolatedAsyncioTestCase):
    async def test_att_read_not_permitted_is_not_retried_or_reconnected(self):
        connection = FakeConnection(
            BleakError("ATT Error 0x02: Read Not Permitted")
        )
        engine = HunterTransactionEngine(connection)

        with self.assertRaises(TransactionReadNotPermitted):
            await engine.read(NOTIFY_UUID)

        self.assertEqual(connection.reads, [NOTIFY_UUID])
        self.assertEqual(connection.reconnects, 0)


if __name__ == "__main__":
    unittest.main()
