# Android BLE capture findings

This note records evidence from the supplied Android HCI/ATT capture. The capture
file itself is intentionally not committed because it contains device-identifying
information.

## GATT handle mapping

The FF80 service discovery responses map these ATT value handles:

| ATT value handle | Characteristic |
|---:|---|
| 0x0014 (20) | FF81 |
| 0x0019 (25) | FF83 |
| 0x001B (27) | FF84 |
| 0x001F (31) | FF86 |
| 0x0021 (33) | FF87 |

The handle mapping is taken from the characteristic declarations in this capture,
not inferred from the Home Assistant connection.

## Connection initialization observed before manual control

In capture order, the Android app sends successful ATT Write Requests:

1. FF81 (handle 0x0014): 14-byte value; Write Response received.
2. FF84 (handle 0x001B): 8-byte value containing a date/time-shaped payload; Write Response received.
3. FF83 (handle 0x0019): 12-byte state payload; Write Response received.

These occur before the first manual FF86/FF83 start transaction. Their purpose and
whether each is required to enable FF86 writes are not established by this capture.

The capture was made with HunterBTT Android app version 6.1.49 (confirmed by the
user). Its FF81 value is 14 bytes:

`B7 B7 B7 B7 F1 64 04 91 E2 25 00 78 34 37`

The older 5.0 APK was separately inspected. Its `BTT2.FF81(String)` serializer
converts each input character to a zero-prefixed hexadecimal numeric value and
returns a hex string for the FF81 write. That is a different, passcode-derived
format and does not generate the captured 14-byte value. The previously inspected
6.1.7 source also has a different four-byte password serializer. Neither older
implementation explains the 6.1.49 capture. The integration therefore uses the
exact 14-byte value observed in the 6.1.49 ATT Write Request; it does not attempt
to recreate either older serializer.

## Captured manual START and STOP

The first observed manual start:

- FF86 Write Request, 17-byte value:
  `04 01 7f ff ff ff ff 00 ff ff ff 00 0a 00 00 1e 00`
- Successful ATT Write Response.
- FF83 Write Request, 12-byte ARM value:
  `01 00 01 01 01 01 01 00 00 00 00 00`
- Successful ATT Write Response.
- The countdown notification begins at 09:59, corroborating a 10-minute run.

The observed STOP:

- FF83 Write Request, 12-byte value:
  `01 00 02 01 00 02 01 00 00 00 00 00`
- Successful ATT Write Response.

A later successful 10-second start uses this FF86 value before the same FF83 ARM
value:

`04 01 04 ff ff ff ff 00 ff ff ff 00 00 0a 00 1e 00`

The two successful FF86 writes differ at byte offset 2 (0x7f versus 0x04), which
maps to `ztmDays` in `Second_86_Protocol`. The capture does not establish why
that field differs. The existing builder preserves 0x7f; it must not be treated
as a universally correct value for every controller state without further
protocol analysis.

## Implementation implications

- The captured manual control sequence is confirmed as FF86 duration write,
  await Write Response, then FF83 ARM write, await Write Response.
- STOP is one FF83 Write Request followed by a successful Write Response.
- Android uses ATT Write Request for these writes; changing HA to Write Command
  is not supported by this evidence.
- The capture contains FF81/FF84/FF83 initialization writes before manual control.
  FF81 is now sent as the exact 14-byte value captured from app version 6.1.49,
  before the best-effort FF84 clock write and FF82/FF83 state exchange. The
  semantic meaning of the opaque FF81 value remains unresolved, and its
  portability across controller firmware/device variants still requires
  hardware validation. It may be relevant to the HA FF86 `Write Not Permitted`
  rejection, but causality is not proven.
- The FF81 initialization write is limited to the single captured 6.1.49 value.
  Do not infer that it is a general password algorithm or reuse it for other
  firmware/device variants without additional captures.

## Validation status

The new test locks down the exact captured 10-minute FF86 payload. This is a
protocol-fixture regression test, not hardware validation. No watering command
was sent by this change.


## Additional notification CCCDs enabled before FF81

The ATT discovery responses and CCCD Write Requests in the same Android
6.1.49 capture identify six additional notification characteristics. The
CCCD descriptor handles receive `01 00` writes before FF81. The six additional
CCCD writes are packets 420, 423, 427, 433, 439, and 445; the three previously
mapped core CCCD writes are packets 430 (FF8F), 436 (FF8A), and 442 (FF82):

| CCCD handle | Characteristic value handle | Characteristic UUID | Captured Android-side role |
|---:|---:|---|---|
| `0x0048` | `0x0047` | `0000ff99-0000-1000-8000-00805f9b34fb` | Zone 1 image-transfer chunks |
| `0x004D` | `0x004C` | `0000ff9b-0000-1000-8000-00805f9b34fb` | Zone 2 image-transfer chunks |
| `0x0054` | `0x0053` | `0000ffa2-0000-1000-8000-00805f9b34fb` | Irrigation-log total-record count |
| `0x0057` | `0x0056` | `0000ff9e-0000-1000-8000-00805f9b34fb` | Irrigation-log records (two-zone record payload) |
| `0x005A` | `0x0059` | `0000ffa3-0000-1000-8000-00805f9b34fb` | Irrigation-log record payload |
| `0x0065` | `0x0064` | `0000ffa5-0000-1000-8000-00805f9b34fb` | Unknown; no matching application protocol handler identified |

All six characteristic declarations advertise read + notify properties in
this capture. The descriptor-to-characteristic association is established by
the ATT characteristic declaration/value handles and the following CCCD
descriptor handles, not by guessing from UUID names.

The inspected decompiled Android 6.1.7 source (older than the user's
confirmed 6.1.49 capture) maps FF99 and FF9B to zone image receivers. This
source is semantic corroboration, not the exact app build used for the
capture. FF9E, FFA2, and FFA3 participate in the irrigation-log receiver:
FFA2 supplies the total record count and FF9E/FFA3 carry decoded zone,
timestamp, infiltration-time, and run-time fields. In the capture, FFA3
notifications occur after watering countdown activity, not in the startup
exchange. FFA5 has no identified handler in the inspected source and no
matching notification payload in this capture.

These channels therefore appear to support optional image/history features,
not the controller's FF81/FF84/FF82/FF83 initialization handshake. The
capture proves Android subscribes to all six before FF81; it does not prove
that any of the six is required for initialization. HA now enables them in
the same nine-CCCD order observed in the capture before sending FF81. They
are treated as optional notification subscriptions: an individual
subscription failure is logged and does not abort the remaining
subscriptions or alter the existing FF81/FF84/FF82/FF83 readiness guard.
Battery Level remains a separate optional subscription after the captured
nine CCCDs.
