"""Regression tests for stale BLE GATT service-cache recovery."""

import unittest
from unittest.mock import AsyncMock, patch

from hunter_btt.bluetooth.client import HunterBLEClient
from hunter_btt.protocol.uuids import CLIENT_ID_UUID


class FakeCharacteristic:
    def __init__(self, uuid, handle, properties):
        self.uuid = uuid
        self.handle = handle
        self.properties = properties
        self.descriptors = []


class FakeService:
    def __init__(self, characteristics):
        self.uuid = "0000ff80-0000-1000-8000-00805f9b34fb"
        self.characteristics = characteristics


class FakeBleakClient:
    def __init__(self, characteristics):
        self.services = [FakeService(characteristics)]
        self.is_connected = True
        self.clear_cache = AsyncMock(return_value=True)
        self.disconnect = AsyncMock(side_effect=self._disconnect)

    async def _disconnect(self):
        self.is_connected = False


class GattCacheRecoveryTests(unittest.IsolatedAsyncioTestCase):
    async def test_missing_ffa5_clears_cache_and_retries_uncached_via_ha_proxy(self):
        stale = FakeBleakClient(
            [
                FakeCharacteristic(
                    "0000ff82-0000-1000-8000-00805f9b34fb",
                    0x0016,
                    ["notify"],
                )
            ]
        )
        fresh = FakeBleakClient(
            [FakeCharacteristic(CLIENT_ID_UUID, 0x0064, ["read", "notify"])]
        )
        device = object()
        resolver = AsyncMock(return_value=device)
        establish = AsyncMock(side_effect=[stale, fresh])
        client = HunterBLEClient(None, "AA:BB:CC:DD:EE:FF")

        with (
            patch(
                "hunter_btt.bluetooth.client.bluetooth.async_ble_device_from_address",
                resolver,
            ),
            patch(
                "hunter_btt.bluetooth.client.establish_connection",
                establish,
            ),
        ):
            await client.connect()

        self.assertIs(client._client, fresh)
        self.assertTrue(client.connected)
        stale.clear_cache.assert_awaited_once_with()
        stale.disconnect.assert_awaited_once_with()
        self.assertEqual(resolver.await_count, 2)
        self.assertEqual(establish.await_count, 2)
        self.assertTrue(establish.await_args_list[0].kwargs["use_services_cache"])
        self.assertFalse(establish.await_args_list[1].kwargs["use_services_cache"])
        self.assertEqual(establish.await_args_list[1].args[1], device)

    async def test_present_ffa5_does_not_trigger_cache_reset(self):
        fresh = FakeBleakClient(
            [FakeCharacteristic(CLIENT_ID_UUID, 0x0064, ["read", "notify"])]
        )
        establish = AsyncMock(return_value=fresh)
        client = HunterBLEClient(None, "AA:BB:CC:DD:EE:FF")

        with (
            patch(
                "hunter_btt.bluetooth.client.bluetooth.async_ble_device_from_address",
                return_value=object(),
            ),
            patch(
                "hunter_btt.bluetooth.client.establish_connection",
                establish,
            ),
        ):
            await client.connect()

        self.assertIs(client._client, fresh)
        self.assertEqual(establish.await_count, 1)
        self.assertTrue(establish.await_args.kwargs["use_services_cache"])


if __name__ == "__main__":
    unittest.main()
