# Manual 10-second watering verification

This is an **opt-in physical-controller test**. It is not run by CI and must
only be performed when Zone 1 can safely discharge water.

## Before starting

- Confirm the Hunter BTT controller is connected through the intended ESPHome
  Bluetooth proxy and the integration reports second-generation initialization
  complete.
- Confirm Zone 1 is safe to water, its valve and downstream area are clear, and
  no schedule or other person is relying on that zone.
- Keep the controller and Home Assistant logs visible. Do not run this test
  unattended.

## Test

1. Start Zone 1 for **10 seconds** using the integration's existing manual
   start control.
2. Confirm an FF8A notification arrives promptly. The captured countdown
   format is 16 bytes; bytes 11 and 12 are minutes and seconds remaining.
   For this test, the first value should be near `00:10` and then decrease.
3. Confirm FF82 reports Zone 1 open/running. In the captured 14-byte FF82
   status, byte 10 (`zone1_state`) is `0x05`; Zone 2 remains `0x01`.
4. Issue Stop immediately after the start/countdown confirmation, rather than
   waiting for the 10-second timer to expire.
5. Confirm a fresh FF82 notification reports Zone 1 stopped/closed:
   byte 10 (`zone1_state`) returns to `0x01`, and Zone 2 remains `0x01`.
6. Verify physical water flow has ceased.

## Captured reference values

- FF8A 10-second example: `08 00 00 00 00 00 00 00 00 00 00 00 0A 00 00 00`
- FF82 Zone 1 running: `01 00 01 01 01 00 01 01 00 00 05 01 80 00`
- FF82 both zones stopped: `01 00 01 01 00 00 01 01 00 00 01 01 80 00`

The automated `tests/test_manual_watering_cycle.py` test exercises the same
10-second command packet sequence and validates simulated FF8A/FF82 events.
It does **not** replace this physical-controller check. Record the actual
notification payloads and whether water flow stopped when reporting the live
test result.
