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
