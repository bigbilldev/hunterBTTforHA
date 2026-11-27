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

The Android 6.1.49 capture shows this order before manual watering:

1. Enable the nine proprietary CCCDs in the order documented below.
2. Read Device Information Firmware Revision String (2A26, value handle 0x000F); response:
   `Version 5.0.1.4 1C`.
3. Read FFA5 (value handle 0x0064); response:
   `C8 7A 76 C4 AA 52`.
4. Write FF81 (value handle 0x0014), 14-byte value; Write Response received.
5. Read and write FF84 (value handle 0x001B), with the write carrying an
   eight-byte date/time-shaped payload.
6. Read FF82, read FF83, merge the status/configuration, and write FF83.
7. Only later does the app perform manual FF86 duration and FF83 ARM operations.

The important initialization input is the FFA5 read response, not an FFA5
notification. The capture shows no FFA5 notification before FF81.

## FF81 serializer decoded from Android 6.1.49

The supplied 6.1.49 XAPK contains `Second_81_Protocol.format()` and
`Second_81_Protocol.parse()`. The formatter constructs ten plaintext bytes:
four numeric passcode digits followed by the six-byte client ID obtained from
FFA5. It encrypts those ten bytes using the app's custom three-round
`flEncryptStream()` transform, then appends a one-byte `isSet` flag and a
three-character random key. The corresponding parser calls
`flDescryptStream()`.

The transform is a reversible sequence of XOR and 8-bit rotations. For each
round, the formatter XORs each byte with the current key byte, then rotates:
left on rounds 0 and 2, right on round 1. The rotation count is the corresponding
reverse-indexed key byte modulo eight. For the captured key `x47`, the
rotation counts are 7 (left), 4 (right), and 0 (left). Decryption reverses
the round order, rotation direction, and XOR order. This is not the separate
DESede/CBC helper also present in the APK.

The captured FF81 value is:

`B7 B7 B7 B7 F1 64 04 91 E2 25 00 78 34 37`

Its byte-for-byte interpretation is:

| Offset | Length | Field | Captured value |
|---:|---:|---|---|
| 0 | 10 | Ciphertext (encrypted plaintext) | `B7 B7 B7 B7 F1 64 04 91 E2 25` |
| 10 | 1 | `isSet` | `00` |
| 11 | 3 | Random key | `78 34 37` (`x47`) |

Decrypting the first ten bytes with `x47` yields:

`00 00 00 00 C8 7A 76 C4 AA 52`

That is passcode `0000` encoded as four numeric digit bytes, followed by
the exact six-byte FFA5 read response. Re-encrypting these ten bytes with the
same key reproduces the captured ciphertext exactly. The captured vector is
now a regression test for the Home Assistant codec.

The serializer implementation uses a four-digit passcode and the newer
14-byte format. The PR deliberately uses the configured passcode (falling back
to the integration's existing `0000` default), reads a fresh FFA5 client ID on
each initialization, and generates a new three-character key for each FF81
payload. The captured `isSet=0` value is used as the initial default; the
semantic meaning of this flag is not established by the capture.


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

The regression suite locks down the captured FF81 and FF86 payloads, verifies
the FF81 encrypt/decrypt round trip, and checks that missing or invalid FFA5
data leaves initialization incomplete. These are protocol-fixture tests, not
hardware validation. No watering command was sent by this change.


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
| `0x0065` | `0x0064` | `0000ffa5-0000-1000-8000-00805f9b34fb` | Six-byte client ID read and notification input used by FF81 initialization |

All six characteristic declarations advertise read + notify properties in
this capture. The descriptor-to-characteristic association is established by
the ATT characteristic declaration/value handles and the following CCCD
descriptor handles, not by guessing from UUID names.

The inspected decompiled Android 6.1.7 source (older than the user's
confirmed 6.1.49 capture) maps FF99 and FF9B to zone image receivers. This
source is semantic corroboration, not the exact app build used for the
capture. FF9E, FFA2, and FFA3 participate in the irrigation-log receiver:
FFA2 supplies the total record count and FF9E/FFA3 carry decoded zone,
timestamp, infiltration-time, and run-time fields. In the 6.1.49 XAPK,
FFA5 is handled by `Second_A5_Protocol`; its parsed six-byte ID is copied
into `AisWrapper._clientId`, which `Second_81_Protocol.format()` consumes.
The capture's FFA5 read response matches the client ID recovered by decrypting
the FF81 payload. No FFA5 notification is observed before FF81 in this capture.

FF99/FF9B and FF9E/FFA2/FFA3 appear to support optional image/history
features. FFA5 is different: the capture and 6.1.49 code establish it as an
FF81 initialization input. HA still attempts all nine CCCD subscriptions in
the captured order, and an individual subscription failure does not prevent
later subscriptions. However, successful FFA5 readability is now a hard
prerequisite for FF81. Battery Level remains a separate optional subscription
after the captured nine CCCDs.
