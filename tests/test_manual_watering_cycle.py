"""Protocol-level short watering cycle test using captured FF8A/FF82 events.

This is a deterministic unit test. It simulates the controller notifications;
see docs/manual-watering-test.md for the opt-in physical-controller procedure.
"""

import unittest

from hunter_btt.bluetooth.transaction import HunterTransactionEngine
from hunter_btt.protocol.generation import HunterGeneration
from hunter_btt.protocol.notifications import decode_countdown
from hunter_btt.protocol.second_generation import parse_ff82
from hunter_btt.protocol.uuids import COMMAND_UUID, COUNTDOWN_UUID, NOTIFY_UUID, ZONE1_CONFIG_UUID


# Captured Zone 1 state values: 0x05 while open/running, 0x01 when closed/stopped.
FF82_ZONE1_STARTED = bytes.fromhex("01 00 01 01 01 00 01 01 00 00 05 01 80 00")
FF82_ZONE1_STOPPED = bytes.fromhex("01 00 01 01 00 00 01 01 00 00 01 01 80 00")
FF8A_TEN_SECONDS = bytes.fromhex("08 00 00 00 00 00 00 00 00 00 00 00 0A 00 00 00")


class FakeClient:
    def __init__(self):
        self.writes = []

    def characteristic_handle(self, uuid):
        return 31 if uuid == ZONE1_CONFIG_UUID else 25

    async def write(self, uuid, payload, response=None):
        self.writes.append((uuid, bytes(payload), response))


class FakeConnection:
    def __init__(self):
        self.client = FakeClient()
        self.reconnect_calls = 0

    async def ensure_connection(self):
        return None

    async def reconnect(self):
        self.reconnect_calls += 1


class ShortWateringCycleTests(unittest.IsolatedAsyncioTestCase):
    async def test_zone_one_ten_second_start_and_stop_notifications(self):
        connection = FakeConnection()
        engine = HunterTransactionEngine(connection)
        engine.set_generation(HunterGeneration.SECOND)

        # Issue the real transaction sequence under test.
        await engine.start_zone(1, 10)

        # Feed the captured-format FF8A countdown and FF82 running-state events
        # that a physical controller should emit after the start writes.
        await engine.notification(COUNTDOWN_UUID, FF8A_TEN_SECONDS)
        await engine.notification(NOTIFY_UUID, FF82_ZONE1_STARTED)

        countdown = decode_countdown(
            await engine.wait_for_notification(COUNTDOWN_UUID, timeout=0.1)
        )
        self.assertTrue(countdown.running)
        self.assertEqual(countdown.remaining_seconds, 10)
        self.assertEqual(countdown.zone, 0)

        started = parse_ff82(
            await engine.wait_for_notification(NOTIFY_UUID, timeout=0.1)
        )
        self.assertEqual(started.zone1_state, 0x05)
        self.assertEqual(started.zone2_state, 0x01)

        # Discard the start event so stop must be checked against a fresh FF82.
        engine.clear_notification(NOTIFY_UUID)
        await engine.stop()
        await engine.notification(NOTIFY_UUID, FF82_ZONE1_STOPPED)

        stopped = parse_ff82(
            await engine.wait_for_notification(NOTIFY_UUID, timeout=0.1)
        )
        self.assertEqual(stopped.zone1_state, 0x01)
        self.assertEqual(stopped.zone2_state, 0x01)

        self.assertEqual(
            [write[0] for write in connection.client.writes],
            [ZONE1_CONFIG_UUID, COMMAND_UUID, COMMAND_UUID],
        )
        self.assertEqual(connection.client.writes[-1][1], bytes.fromhex(
            "01 00 02 01 00 02 01 00 00 00 00 00"
        ))


if __name__ == "__main__":
    unittest.main()
