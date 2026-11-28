# FFA5 notification subscription diagnostics

The 16-bit FFA5 declaration parser is retained unchanged. It reconstructs a
Bleak characteristic with:

- value handle `0x0064`;
- properties `read` and `notify`;
- Client Characteristic Configuration Descriptor (UUID `0x2902`) at
  handle `0x0065`.

The recovered object is held in `HunterBLEClient._recovered_characteristics`
and returned by `characteristic_object()`. It is not inserted into the
ESPHome client's original service collection. Instead, the exact reconstructed
characteristic object is passed to `BleakClient.start_notify()`; its attached
descriptor is therefore available to the backend.

## ESPHome backend behavior

The ESPHome Bleak backend first calls the proxy's
`bluetooth_gatt_start_notify(address, characteristic.handle, ...)`. If the
proxy advertises the `REMOTE_CACHING` feature, the backend then obtains the
CCCD using `characteristic.get_descriptor(CCCD_UUID)` and explicitly writes
that descriptor's handle with `01 00` (notify enable). For FFA5, that should be
handle `0x0065`. Without `REMOTE_CACHING`, the backend returns after the
proxy subscription call and does not issue that separate host-side descriptor
write.

This order is diagnostically important: an error reported against
characteristic handle `0x0064` is from the initial proxy
`bluetooth_gatt_start_notify` operation; an error from the explicit CCCD
write should identify descriptor handle `0x0065`. The new log records the
backend class, backend feature flags, characteristic handle, and attached
CCCD handle immediately before subscription and on failure.

## Initialization remains independent

FFA5 notification subscription is best-effort. The client records the failure
and continues through the remaining subscription list. The manager then
performs the successful FFA5 live read and FF81 initialization sequence as
before. No initialization prerequisite or watering command packet was changed.

## Next hardware log to collect

After updating the integration, reconnect once and capture these log entries:

- `Hunter FFA5 notify path` — should report characteristic handle 100 and
  CCCD handle 101;
- the backend feature flags;
- `Hunter FFA5 notify activation failed`, if it still fails, including the
  actual failing ATT handle;
- `Hunter FF81 initialization packet written` and
  `Hunter second-generation initialization completed`.

If the feature flags show `REMOTE_CACHING` enabled and the failure is still
reported at handle 100, the proxy's initial notification-registration request
is failing before the explicit CCCD write. If the error moves to handle 101,
the failure is specifically in the descriptor write.


## FFA5 notification failure: current investigation

The 2026-11-28 connection log showed that FFA5 was recovered from its
declaration as value handle 0x0064 with a CCCD at 0x0065. Its live read and
the FF81 initialization write succeeded, but FFA5 notification activation
failed with ESPHome GATT error 135 (0x87), described as Illegal parameter.
Other notification subscriptions, including FF82 and FF8A, succeeded.

The distinction between the two notification stages matters. The ESPHome
Bleak backend implementation first sends the proxy notification-registration
request for the characteristic value handle. Only after that succeeds, and
when REMOTE_CACHING is enabled, it writes 01 00 to the CCCD descriptor handle.
See the upstream
[ESPHome Bleak start_notify implementation](https://github.com/Bluetooth-Devices/bleak-esphome/blob/b2fb6bf4cb2ea4bf52284ce8664d11e3de46fdf4/src/bleak_esphome/backend/client.py).

Consequently, the observed error naming handle 100 (0x0064) is evidence that
the first proxy registration stage failed. The backend did not reach the
subsequent CCCD write to handle 101 (0x0065). This is not evidence that the
CCCD payload 01 00 itself was rejected.

ESPHome's proxy forwards the registration request to its GATT connection's
notify-characteristic operation and reports any returned GATT error against
the characteristic handle. See
[ESPHome bluetooth_proxy.cpp](https://github.com/esphome/esphome/blob/dev/esphome/components/bluetooth_proxy/bluetooth_proxy.cpp).
The ESP-IDF GATT client API documents that notification-registration
validation can report ESP_GATT_ILLEGAL_PARAMETER when the characteristic
handle fails its service-cache validation; the documentation also notes that
validation may be skipped if the cache is not yet ready. See the
[ESP-IDF GATT client registration documentation](https://docs.espressif.com/projects/esp-idf/en/latest/esp32h21/api-reference/bluetooth/esp_gattc.html).

This makes a proxy-side GATT service/handle-cache mismatch a plausible
investigation target, not a confirmed root cause. The new diagnostics record
whether the recovered FFA5 handle/UUID also appears in the Bleak service
collection returned by the proxy, the total characteristic count, the proxy
ESPHome version, the backend feature flags, and the recovered service/CCCD
handles. The FFA5 subscription remains best-effort; successful FFA5 reads,
FF81 initialization, FF82/FF8A subscriptions, and watering commands are not
changed.

### Next evidence needed

On the next reconnect, retain the new Hunter FFA5 notify path and
Hunter FFA5 notify activation failed entries. If backend_service_match is
false, compare the proxy-returned service table with the recovered declaration
and Android's service table. Also collect ESPHome proxy logs around service
discovery and notification registration, including the proxy firmware version.

If backend_service_match is true but the proxy still returns error 135 at
handle 100, the next investigation should move below the Home Assistant
Bleak service collection: inspect the proxy's internal GATT client cache and
the result of its notify-characteristic registration call. Do not work around
this by writing handle 100 as if it were a CCCD, and do not make FFA5
notification failure fatal while the live FFA5 read/FF81 initialization path
continues to work.
