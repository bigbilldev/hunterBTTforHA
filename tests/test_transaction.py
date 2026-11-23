"""Unit tests for the captured second-generation manual BLE transactions."""

import unittest

from bleak.exc import BleakError

from hunter_btt.bluetooth.transaction import (
    HunterTransactionEngine,
    TransactionError,
    build_start_arm_packet,
    build_stop_packet,
    build_zone_duration_packet,
)
from hunter_btt.protocol.generation import HunterGeneration
from hunter_btt.protocol.uuids import (
    COMMAND_UUID,
    ZONE1_CONFIG_UUID,
    ZONE2_CONFIG_UUID,
)


class FakeClient:
    def __init__(self, write_error=None):
        self.writes = []
        self.write_error = write_error

    def characteristic_handle(self, uuid):
        return 31 if uuid == ZONE1_CONFIG_UUID else 25

    async def write(self, uuid, payload, response=None):
        self.writes.append((uuid, bytes(payload), response))
        if self.write_error is not None:
            raise self.write_error


class FakeConnection:
    def __init__(self, write_error=None):
        self.client = FakeClient(write_error=write_error)
        self.ensure_calls = 0
        self.reconnect_calls = 0

    async def ensure_connection(self):
        self.ensure_calls += 1

    async def reconnect(self):
        self.reconnect_calls += 1


class DurationPacketTests(unittest.TestCase):
    def test_captured_ten_second_packet(self):
        self.assertEqual(
            build_zone_duration_packet(10),
            bytes.fromhex("04 01 7f ff ff ff ff 00 ff ff ff 00 00 0a 00 1e 00"),
        )

    def test_pcap_captured_ten_minute_packet(self):
        # Android capture: FF86 Write Request followed by a successful
        # Write Response; countdown notification starts at 09:59.
        self.assertEqual(
            build_zone_duration_packet(600),
            bytes.fromhex(
                "04 01 7f ff ff ff ff 00 ff ff ff 00 0a 00 00 1e 00"
            ),
        )

    def test_captured_thirty_five_second_packet(self):
        self.assertEqual(
            build_zone_duration_packet(35),
            bytes.fromhex("04 01 7f ff ff ff ff 00 ff ff ff 00 00 23 00 1e 00"),
        )

    def test_duration_hour_minute_second_fields(self):
        self.assertEqual(
            build_zone_duration_packet(600)[11:14],
            bytes((0, 10, 0)),
        )
        self.assertEqual(
            build_zone_duration_packet(3600)[11:14],
            bytes((1, 0, 0)),
        )

    def test_rejects_invalid_duration(self):
        for runtime in (0, -1, 3601):
            with self.subTest(runtime=runtime):
                with self.assertRaises(TransactionError):
                    build_zone_duration_packet(runtime)

    def test_arm_and_stop_payloads_match_capture(self):
        self.assertEqual(
            build_start_arm_packet(1, 10),
            bytes.fromhex("01 00 01 01 01 01 01 00 00 00 00 00"),
        )
        self.assertEqual(
            build_start_arm_packet(2, 10),
            bytes.fromhex("01 00 01 01 01 01 01 00 00 00 00 00"),
        )
        self.assertEqual(
            build_stop_packet(),
            bytes.fromhex("01 00 02 01 00 02 01 00 00 00 00 00"),
        )


class TransactionSequenceTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.connection = FakeConnection()
        self.engine = HunterTransactionEngine(self.connection)
        self.engine.set_generation(HunterGeneration.SECOND)

    async def test_zone_one_start_writes_duration_then_arm(self):
        await self.engine.start_zone(1, 35)
        self.assertEqual(
            self.connection.client.writes,
            [
                (
                    ZONE1_CONFIG_UUID,
                    bytes.fromhex(
                        "04 01 7f ff ff ff ff 00 ff ff ff 00 00 23 00 1e 00"
                    ),
                    True,
                ),
                (
                    COMMAND_UUID,
                    bytes.fromhex("01 00 01 01 01 01 01 00 00 00 00 00"),
                    True,
                ),
            ],
        )

    async def test_zone_two_start_uses_zone_two_config(self):
        await self.engine.start_zone(2, 10)
        self.assertEqual(
            self.connection.client.writes[0][0],
            ZONE2_CONFIG_UUID,
        )
        self.assertEqual(self.connection.client.writes[1][0], COMMAND_UUID)

    async def test_stop_is_one_ff83_write(self):
        await self.engine.stop()
        self.assertEqual(
            self.connection.client.writes,
            [
                (
                    COMMAND_UUID,
                    bytes.fromhex("01 00 02 01 00 02 01 00 00 00 00 00"),
                    True,
                )
            ],
        )

    async def test_att_write_not_permitted_fails_without_retry_or_reconnect(self):
        self.connection.client.write_error = BleakError(
            "handle=31 error=3 description=Write not permitted"
        )

        with self.assertRaisesRegex(
            TransactionError,
            "ATT 0x03 Write Not Permitted",
        ):
            await self.engine.start_zone(1, 10)

        self.assertEqual(len(self.connection.client.writes), 1)
        self.assertEqual(self.connection.reconnect_calls, 0)
        self.assertEqual(self.connection.client.writes[0][2], True)

    async def test_other_bleak_errors_keep_retry_behavior(self):
        self.connection.client.write_error = BleakError("temporary transport failure")

        with self.assertRaises(TransactionError):
            await self.engine.start_zone(1, 10)

        self.assertEqual(len(self.connection.client.writes), 3)
        self.assertEqual(self.connection.reconnect_calls, 2)

    async def test_invalid_zone_does_not_write(self):
        with self.assertRaises(TransactionError):
            await self.engine.start_zone(3, 10)
        self.assertEqual(self.connection.client.writes, [])

    async def test_non_second_generation_is_blocked(self):
        self.engine.set_generation(HunterGeneration.FIRST)
        with self.assertRaises(TransactionError):
            await self.engine.start_zone(1, 10)
        with self.assertRaises(TransactionError):
            await self.engine.stop()
        self.assertEqual(self.connection.client.writes, [])


if __name__ == "__main__":
    unittest.main()
