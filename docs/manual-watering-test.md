# Manual watering: physical validation

These are opt-in physical-controller tests, not CI tests. Only run them when
the selected zone can safely discharge water. Keep the controller and Home
Assistant logs visible and do not leave a test unattended.

## Safety and setup

- Confirm the Hunter BTT controller is connected through the intended ESPHome
  Bluetooth proxy and second-generation initialization completed.
- Confirm Zone 1, its valve, and downstream area are safe to water.
- Ensure no schedule or other person is relying on the zone.
- Set the manual runtime to 10 seconds for both tests.

## Physical test 1: automatic 10-second shutoff

**Procedure performed:** Set the watering time to 10 seconds, pressed STOP
while idle, then pressed START. The valve opened and closed automatically
after approximately 10 seconds.

**Observed Home Assistant evidence (2026-11-28, 11:49 log):**

- FF8A emitted the countdown from 09 through 01, then returned to 0a
  (10 seconds) at the end of the run.
- FF82 first reported Zone 1 running:
  01 00 01 01 01 00 01 01 00 00 05 01 80 00
- FF82 then reported Zone 1 stopped:
  01 00 01 01 00 00 01 01 00 00 01 01 80 00
- The physical valve closed at the programmed duration.

**Result:** Passed. This validates the programmed automatic shutoff path.

## Physical test 2: manual STOP before timer expiry

**Procedure performed:** With the runtime set to 10 seconds, pressed START,
confirmed the valve opened, then pressed STOP approximately five seconds
later. The valve closed immediately after STOP.

**Observed Home Assistant evidence (2026-11-28, 11:53 log):**

- FF8A countdown values were 09, 08, 07, and 06.
- At 11:53:11.065, FF8A returned to 0a (10 seconds), consistent with the
  countdown being reset rather than continuing toward zero.
- At 11:53:11.066, FF82 reported:
  01 00 01 01 00 00 01 01 00 00 01 01 80 00
- FF82 repeated the same stopped-state payload at 11:53:11.286.
- The physical valve closed after the manual STOP command, before the
  configured 10-second runtime elapsed.

**Result:** Passed. This validates manual interruption at the physical valve
and provides correlated FF8A countdown-reset and FF82 stopped-state evidence.

**Evidence limitation:** This 11:53 excerpt contains the incoming FF8A and
FF82 notifications, but not the outbound FF83 write. The new FF83 diagnostic
logs in this PR are intended to capture that missing command-side evidence on
the next run. Therefore, this physical test proves the STOP behavior but does
not, by itself, establish the exact number of FF83 writes or their retry
behavior.

## Captured reference payloads

- FF8A 10-second countdown start:
  08 00 00 00 00 00 00 00 00 00 00 00 0A 00 00 00
- FF82 Zone 1 running:
  01 00 01 01 01 00 01 01 00 00 05 01 80 00
- FF82 both zones stopped:
  01 00 01 01 00 00 01 01 00 00 01 01 80 00

The automated tests/test_manual_watering_cycle.py test simulates the
captured-format FF8A/FF82 notifications and exercises the existing transaction
sequence. It does not operate a physical valve.

## Next physical STOP capture

After installing the diagnostic PR:

1. Set Zone 1 to 10 seconds and start watering.
2. Press STOP while the valve is open, ideally around five seconds into the run.
3. Capture the Home Assistant log from the FF83 write-begin entry through the
   subsequent FF8A and FF82 notifications.
4. Include every Hunter FF83 write begin/completed/failed entry and the
   FF82/FF8A notification entries with their sequence numbers and timestamps.

The diagnostic logs include the FF83 payload, handle, response mode, retry
attempt, and the FF82/FF8A notification sequence counters at write time.
Notifications also record the most recent FF83 write ID, command type, and
elapsed age. This makes it possible to establish whether the controller
received one STOP write or multiple attempts and how the state/countdown
notifications followed it.
