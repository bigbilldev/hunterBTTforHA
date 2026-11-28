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

**Follow-up command-side evidence (2026-11-28, 12:11 PR #30 log):**

- A separate session using the PR #30 instrumentation recorded START_ARM as
  write_id=3 and STOP as write_id=4.
- STOP was one FF83 write attempt, completed in 132 ms; no retry or second
  STOP write was logged.
- FF8A returned to 0a 126 ms after STOP began.
- FF82 reported the stopped-state payload 129 ms after STOP began and repeated
  it 239 ms after STOP began.
- The physical valve closed.

**Result:** Passed. The PR #30 capture establishes that one STOP write was
sufficient in this run and directly correlates the STOP write with the
countdown reset and stopped-state notifications. It does not establish that
one write is sufficient under every controller condition.

## Physical test 3: HA START while valve was already opened locally

**Procedure performed (2026-11-28, 12:18 log):** The valve was manually opened
locally at the controller. In Home Assistant, the manual runtime was set to
10 seconds and START was pressed. The valve did not respond to the HA START
command, and it did not close automatically after 10 seconds. STOP was then
pressed in Home Assistant, and the valve closed.

**Observed Home Assistant evidence:**

- FF83 START_ARM write_id=5 began at 12:18:38.157 and completed in 114 ms.
- FF8A continued reporting 10 (0A) once per second; it did not count down
  through 09..01.
- No FF82 running-state transition followed the HA START.
- FF83 STOP write_id=6 began at 12:18:57.224 and completed in 125 ms, with no
  retry.
- FF8A still reported 10 shortly after STOP; FF82 reported the stopped-state
  payload 123 ms after STOP began and repeated it 459 ms after STOP began.
- The physical valve closed after STOP.

**Result:** HA START was not confirmed as a watering start in this pre-opened
valve condition. A successful FF83 write alone is not proof that the controller
started the timed run; the expected FF8A countdown and FF82 running-state
transition were absent. STOP was confirmed by FF82 and the physical valve.
This is an atypical local/manual operating condition and should not be
generalized to a normal HA START test.

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

## Diagnostic interpretation

The PR #30 FF83 logs include the payload, handle, response mode, retry
attempt, and FF82/FF8A sequence counters at write time. Notifications also
record the most recent FF83 write ID, command type, and elapsed age. Use the
notification evidence to confirm a watering state transition; do not treat a
successful GATT write as proof that the valve started or stopped.
