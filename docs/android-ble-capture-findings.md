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

The FF81 value is 14 bytes. Do not copy it into the integration or assume it is a
passcode. The separately inspected 6.1.7 APK's `Second_81_Protocol` serializer
produces four bytes, and the capture identifies the app version as 5.0.1.4. The
version and payload discrepancy must be resolved before implementing FF81 setup.

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
  Their semantics are unresolved. They may be relevant to the HA FF86
  `Write Not Permitted` rejection, but causality is not proven.
- Do not hard-code the observed 14-byte FF81 value, add speculative
  authentication, or issue experimental watering commands until the initialization
  sequence is understood.

## Validation status

The new test locks down the exact captured 10-minute FF86 payload. This is a
protocol-fixture regression test, not hardware validation. No watering command
was sent by this change.
