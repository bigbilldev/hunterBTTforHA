"""Tests for declaration-based recovery of GATT attributes misgrouped by Bleak."""

import unittest
from unittest.mock import AsyncMock
from uuid import UUID

from bleak.backends.characteristic import BleakGATTCharacteristic
from bleak.backends.descriptor import BleakGATTDescriptor
from bleak.backends.service import BleakGATTService

from hunter_btt.bluetooth.client import HunterBLEClient
from hunter_btt.bluetooth.gatt_attributes import (
    normalize_uuid,
    parse_characteristic_declaration,
)
from hunter_btt.protocol.uuids import CLIENT_ID_UUID

CLIENT_ID = bytes.fromhex("FB F0 F5 77 94 4A")


def _descriptor_declaration(
    properties=0x12, value_handle=0x0064, uuid=CLIENT_ID_UUID, short=False
):
    if short:
        short_uuid = int(normalize_uuid(uuid).replace("-", "")[4:8], 16)
        encoded_uuid = short_uuid.to_bytes(2, "little")
    else:
        encoded_uuid = UUID(normalize_uuid(uuid)).bytes_le
    return bytes([properties]) + value_handle.to_bytes(2, "little") + encoded_uuid


class MisgroupedGattClient:
    def __init__(self, *, include_cccd=True):
        self.is_connected = True
        self.service = BleakGATTService(
            obj=None,
            handle=0x0012,
            uuid="0000ff80-0000-1000-8000-00805f9b34fb",
        )
        self.parent = BleakGATTCharacteristic(
            obj=None,
            handle=0x005e,
            uuid="0000ffa1-0000-1000-8000-00805f9b34fb",
            properties=["read", "write"],
            max_write_without_response_size=20,
            service=self.service,
        )
        self.service.add_characteristic(self.parent)

        self.declaration = BleakGATTDescriptor(
            obj=None, handle=0x0063,
            uuid="00002803-0000-1000-8000-00805f9b34fb",
            characteristic=self.parent,
        )
        self.value_attribute = BleakGATTDescriptor(
            obj=None, handle=0x0064, uuid=CLIENT_ID_UUID,
            characteristic=self.parent,
        )
        self.cccd = BleakGATTDescriptor(
            obj=None, handle=0x0065,
            uuid="00002902-0000-1000-8000-00805f9b34fb",
            characteristic=self.parent,
        )
        for descriptor in (self.declaration, self.value_attribute):
            self.parent.add_descriptor(descriptor)
        if include_cccd:
            self.parent.add_descriptor(self.cccd)

        self.services = [self.service]
        self.read_gatt_char = AsyncMock(
            side_effect=[_descriptor_declaration(), CLIENT_ID]
        )
        self.start_notify = AsyncMock()
        self.stop_notify = AsyncMock()


class CharacteristicDeclarationParserTests(unittest.TestCase):
    def test_parses_five_byte_16_bit_uuid(self):
        parsed = parse_characteristic_declaration(
            _descriptor_declaration(short=True), CLIENT_ID_UUID
        )
        self.assertEqual(parsed.uuid, normalize_uuid(CLIENT_ID_UUID))
        self.assertEqual(parsed.value_handle, 0x0064)
        self.assertEqual(set(parsed.properties), {"read", "notify"})

    def test_parses_nineteen_byte_128_bit_uuid(self):
        parsed = parse_characteristic_declaration(
            _descriptor_declaration(), CLIENT_ID_UUID
        )
        self.assertEqual(parsed.uuid, normalize_uuid(CLIENT_ID_UUID))
        self.assertEqual(parsed.value_handle, 0x0064)
        self.assertEqual(set(parsed.properties), {"read", "notify"})

    def test_normalizes_short_and_canonical_expected_uuid(self):
        self.assertEqual(normalize_uuid("ffa5"), normalize_uuid(CLIENT_ID_UUID))
        self.assertEqual(normalize_uuid("0000FFA5"), normalize_uuid(CLIENT_ID_UUID))

    def test_rejects_malformed_payload_lengths(self):
        for payload in (b"", b"\x12\x64\x00", bytes(6), bytes(18), bytes(20)):
            with self.subTest(length=len(payload)):
                with self.assertRaisesRegex(ValueError, "must be 5 bytes"):
                    parse_characteristic_declaration(payload, CLIENT_ID_UUID)

    def test_rejects_incorrect_16_bit_uuid(self):
        with self.assertRaisesRegex(ValueError, "does not match"):
            parse_characteristic_declaration(
                _descriptor_declaration(uuid="0000ffa4-0000-1000-8000-00805f9b34fb", short=True),
                CLIENT_ID_UUID,
            )

    def test_rejects_incorrect_128_bit_uuid(self):
        with self.assertRaisesRegex(ValueError, "does not match"):
            parse_characteristic_declaration(
                _descriptor_declaration(uuid="0000ffa4-0000-1000-8000-00805f9b34fb"),
                CLIENT_ID_UUID,
            )

    def test_rejects_zero_handle_and_empty_properties(self):
        with self.assertRaisesRegex(ValueError, "value handle"):
            parse_characteristic_declaration(
                _descriptor_declaration(value_handle=0), CLIENT_ID_UUID
            )
        with self.assertRaisesRegex(ValueError, "no properties"):
            parse_characteristic_declaration(
                _descriptor_declaration(properties=0), CLIENT_ID_UUID
            )


class GattAttributeRecoveryTests(unittest.IsolatedAsyncioTestCase):
    async def _assert_recovery(self, declaration):
        backend = MisgroupedGattClient()
        backend.read_gatt_char = AsyncMock(side_effect=[declaration, CLIENT_ID])
        client = HunterBLEClient(None, "AA:BB:CC:DD:EE:FF")
        client._client = backend

        recovered = await client._recover_misclassified_characteristic(CLIENT_ID_UUID)

        self.assertTrue(recovered)
        characteristic = client.characteristic_object(CLIENT_ID_UUID)
        self.assertIsNotNone(characteristic)
        self.assertEqual(characteristic.handle, 0x0064)
        self.assertEqual(characteristic.uuid, normalize_uuid(CLIENT_ID_UUID))
        self.assertEqual(set(characteristic.properties), {"read", "notify"})
        self.assertEqual(
            characteristic.get_descriptor(0x0065).uuid,
            "00002902-0000-1000-8000-00805f9b34fb",
        )
        value = await client.read(CLIENT_ID_UUID)
        self.assertEqual(value, CLIENT_ID)
        self.assertEqual(len(value), 6)
        self.assertTrue(any(value))
        declaration_probe = backend.read_gatt_char.await_args_list[0].args[0]
        self.assertEqual(declaration_probe.handle, 0x0063)
        self.assertEqual(declaration_probe.properties, ["read"])
        self.assertIs(backend.read_gatt_char.await_args_list[1].args[0], characteristic)

    async def test_reconstructs_ffa5_from_five_byte_declaration(self):
        await self._assert_recovery(_descriptor_declaration(short=True))

    async def test_reconstructs_ffa5_from_nineteen_byte_declaration(self):
        await self._assert_recovery(_descriptor_declaration())

    async def test_rejects_declaration_that_does_not_identify_ffa5(self):
        backend = MisgroupedGattClient()
        backend.read_gatt_char = AsyncMock(return_value=_descriptor_declaration(
            uuid="0000ffa4-0000-1000-8000-00805f9b34fb", short=True
        ))
        client = HunterBLEClient(None, "AA:BB:CC:DD:EE:FF")
        client._client = backend
        self.assertFalse(await client._recover_misclassified_characteristic(CLIENT_ID_UUID))
        self.assertIsNone(client.characteristic_object(CLIENT_ID_UUID))

    async def test_rejects_malformed_declaration(self):
        backend = MisgroupedGattClient()
        backend.read_gatt_char = AsyncMock(return_value=b"\x12\x64\x00\xA5")
        client = HunterBLEClient(None, "AA:BB:CC:DD:EE:FF")
        client._client = backend
        self.assertFalse(await client._recover_misclassified_characteristic(CLIENT_ID_UUID))
        self.assertIsNone(client.characteristic_object(CLIENT_ID_UUID))

    async def test_rejects_declaration_without_read_and_notify(self):
        backend = MisgroupedGattClient()
        backend.read_gatt_char = AsyncMock(return_value=_descriptor_declaration(properties=0x02))
        client = HunterBLEClient(None, "AA:BB:CC:DD:EE:FF")
        client._client = backend
        self.assertFalse(await client._recover_misclassified_characteristic(CLIENT_ID_UUID))
        self.assertIsNone(client.characteristic_object(CLIENT_ID_UUID))

    async def test_rejects_declaration_with_mismatched_value_handle(self):
        backend = MisgroupedGattClient()
        backend.read_gatt_char = AsyncMock(return_value=_descriptor_declaration(value_handle=0x0066))
        client = HunterBLEClient(None, "AA:BB:CC:DD:EE:FF")
        client._client = backend
        self.assertFalse(await client._recover_misclassified_characteristic(CLIENT_ID_UUID))
        self.assertIsNone(client.characteristic_object(CLIENT_ID_UUID))

    async def test_rejects_missing_cccd(self):
        backend = MisgroupedGattClient(include_cccd=False)
        backend.read_gatt_char = AsyncMock(return_value=_descriptor_declaration(short=True))
        client = HunterBLEClient(None, "AA:BB:CC:DD:EE:FF")
        client._client = backend
        self.assertFalse(await client._recover_misclassified_characteristic(CLIENT_ID_UUID))
        self.assertIsNone(client.characteristic_object(CLIENT_ID_UUID))

    async def test_ffa5_notify_failure_is_recorded_without_aborting_subscribe(self):
        backend = MisgroupedGattClient()
        backend.read_gatt_char = AsyncMock(return_value=_descriptor_declaration(short=True))
        backend.start_notify.side_effect = RuntimeError(
            "handle=100 error=135 description=Illegal parameter"
        )
        client = HunterBLEClient(None, "AA:BB:CC:DD:EE:FF")
        client._client = backend
        await client._recover_misclassified_characteristic(CLIENT_ID_UUID)
        client.register_notification_callback(lambda _uuid, _payload: None)

        status = await client.subscribe(notification_uuids=(CLIENT_ID_UUID,))

        self.assertIn("failed:", status[CLIENT_ID_UUID])
        self.assertTrue(client.connected)

    async def test_recovered_ffa5_is_used_for_notify_subscription(self):
        backend = MisgroupedGattClient()
        backend.read_gatt_char = AsyncMock(return_value=_descriptor_declaration(short=True))
        client = HunterBLEClient(None, "AA:BB:CC:DD:EE:FF")
        client._client = backend
        await client._recover_misclassified_characteristic(CLIENT_ID_UUID)
        client.register_notification_callback(lambda _uuid, _payload: None)

        await client.start_notify(CLIENT_ID_UUID)

        recovered = client.characteristic_object(CLIENT_ID_UUID)
        self.assertIs(backend.start_notify.await_args.args[0], recovered)
        # ESPHome's REMOTE_CACHING path reads the CCCD from the exact
        # characteristic object passed to start_notify, then writes its handle.
        cccd = recovered.get_descriptor(0x0065)
        self.assertIsNotNone(cccd)
        self.assertEqual(cccd.handle, 0x0065)
        self.assertEqual(
            cccd.uuid,
            "00002902-0000-1000-8000-00805f9b34fb",
        )


if __name__ == "__main__":
    unittest.main()
