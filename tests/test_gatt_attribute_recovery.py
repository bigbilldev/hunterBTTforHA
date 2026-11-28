"""Tests for declaration-based recovery of GATT attributes misgrouped by Bleak."""

import unittest
from unittest.mock import AsyncMock

from bleak.backends.characteristic import BleakGATTCharacteristic
from bleak.backends.descriptor import BleakGATTDescriptor
from bleak.backends.service import BleakGATTService

from hunter_btt.bluetooth.client import HunterBLEClient
from hunter_btt.protocol.uuids import CLIENT_ID_UUID

CLIENT_ID = bytes.fromhex("FB F0 F5 77 94 4A")


def _descriptor_declaration(properties=0x12, value_handle=0x0064, uuid=CLIENT_ID_UUID):
    from uuid import UUID

    return bytes([properties]) + value_handle.to_bytes(2, "little") + UUID(uuid).bytes_le


class MisgroupedGattClient:
    def __init__(self):
        self.is_connected = True
        self.service = BleakGATTService(obj=None, handle=0x0012, uuid="0000ff80-0000-1000-8000-00805f9b34fb")
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
        for descriptor in (self.declaration, self.value_attribute, self.cccd):
            self.parent.add_descriptor(descriptor)

        self.services = [self.service]
        self.read_gatt_descriptor = AsyncMock(
            return_value=_descriptor_declaration()
        )
        self.read_gatt_char = AsyncMock(return_value=CLIENT_ID)
        self.start_notify = AsyncMock()
        self.stop_notify = AsyncMock()


class GattAttributeRecoveryTests(unittest.IsolatedAsyncioTestCase):
    async def test_reconstructs_ffa5_from_2803_and_reads_live_six_bytes(self):
        backend = MisgroupedGattClient()
        client = HunterBLEClient(None, "AA:BB:CC:DD:EE:FF")
        client._client = backend

        recovered = await client._recover_misclassified_characteristic(CLIENT_ID_UUID)

        self.assertTrue(recovered)
        characteristic = client.characteristic_object(CLIENT_ID_UUID)
        self.assertIsNotNone(characteristic)
        self.assertEqual(characteristic.handle, 0x0064)
        self.assertEqual(characteristic.uuid, CLIENT_ID_UUID)
        self.assertEqual(set(characteristic.properties), {"read", "notify"})
        self.assertEqual(characteristic.get_descriptor(0x0065).uuid,
                         "00002902-0000-1000-8000-00805f9b34fb")

        value = await client.read(CLIENT_ID_UUID)

        self.assertEqual(value, CLIENT_ID)
        backend.read_gatt_descriptor.assert_awaited_once_with(backend.declaration)
        backend.read_gatt_char.assert_awaited_once_with(characteristic)
        self.assertEqual(len(value), 6)
        self.assertTrue(any(value))

    async def test_rejects_declaration_that_does_not_identify_ffa5(self):
        backend = MisgroupedGattClient()
        backend.read_gatt_descriptor = AsyncMock(
            return_value=_descriptor_declaration(
                uuid="0000ffa4-0000-1000-8000-00805f9b34fb"
            )
        )
        client = HunterBLEClient(None, "AA:BB:CC:DD:EE:FF")
        client._client = backend

        self.assertFalse(
            await client._recover_misclassified_characteristic(CLIENT_ID_UUID)
        )
        self.assertIsNone(client.characteristic_object(CLIENT_ID_UUID))
        backend.read_gatt_char.assert_not_awaited()

    async def test_rejects_declaration_without_read_property(self):
        backend = MisgroupedGattClient()
        backend.read_gatt_descriptor = AsyncMock(
            return_value=_descriptor_declaration(properties=0x10)
        )
        client = HunterBLEClient(None, "AA:BB:CC:DD:EE:FF")
        client._client = backend

        self.assertFalse(
            await client._recover_misclassified_characteristic(CLIENT_ID_UUID)
        )
        self.assertIsNone(client.characteristic_object(CLIENT_ID_UUID))
        backend.read_gatt_char.assert_not_awaited()

    async def test_recovered_ffa5_is_used_for_notify_subscription(self):
        backend = MisgroupedGattClient()
        client = HunterBLEClient(None, "AA:BB:CC:DD:EE:FF")
        client._client = backend
        await client._recover_misclassified_characteristic(CLIENT_ID_UUID)
        client.register_notification_callback(lambda _uuid, _payload: None)

        await client.start_notify(CLIENT_ID_UUID)

        self.assertIs(backend.start_notify.await_args.args[0],
                      client.characteristic_object(CLIENT_ID_UUID))


if __name__ == "__main__":
    unittest.main()
