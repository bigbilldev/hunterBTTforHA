"""Constants for the Hunter BTT Home Assistant integration."""

from __future__ import annotations

from datetime import timedelta
from typing import Final

# ---------------------------------------------------------------------------
# Integration identity
# ---------------------------------------------------------------------------

DOMAIN: Final = "hunter_btt"
NAME: Final = "Hunter BTT"
MANUFACTURER: Final = "Hunter Industries"
DEFAULT_NAME: Final = "Hunter BTT"

# ---------------------------------------------------------------------------
# Home Assistant config-entry keys
#
# These are intentionally defined here because the current project imports
# them from hunter_btt.const in coordinator.py and diagnostics.py.
# ---------------------------------------------------------------------------

CONF_ADDRESS: Final = "address"
CONF_NAME: Final = "name"
CONF_PASSCODE: Final = "passcode"
CONF_RUNTIME: Final = "runtime"

# ---------------------------------------------------------------------------
# BLE services
# ---------------------------------------------------------------------------

FIRST_SERVICE_UUID: Final = "0000fcc0-0000-1000-8000-00805f9b34fb"
SECOND_SERVICE_UUID: Final = "0000ff80-0000-1000-8000-00805f9b34fb"

# Current config-flow discovery uses this name.
# The Android/reference protocol identifies FF80 as the second-generation
# Hunter service.
SERVICE_UUID: Final = SECOND_SERVICE_UUID

BATTERY_SERVICE_UUID: Final = "0000180f-0000-1000-8000-00805f9b34fb"
BATTERY_LEVEL_UUID: Final = "00002a19-0000-1000-8000-00805f9b34fb"

# ---------------------------------------------------------------------------
# Second-generation Hunter characteristics
# ---------------------------------------------------------------------------

PASSCODE_UUID: Final = "0000ff81-0000-1000-8000-00805f9b34fb"
NOTIFY_UUID: Final = "0000ff82-0000-1000-8000-00805f9b34fb"
COMMAND_UUID: Final = "0000ff83-0000-1000-8000-00805f9b34fb"
TIME_UUID: Final = "0000ff84-0000-1000-8000-00805f9b34fb"

ZONE1_CONFIG_UUID: Final = "0000ff86-0000-1000-8000-00805f9b34fb"
ZONE1_TIMER_UUID: Final = "0000ff87-0000-1000-8000-00805f9b34fb"
ZONE1_CYCLING_UUID: Final = "0000ff88-0000-1000-8000-00805f9b34fb"
ZONE1_DIAGNOSTIC_UUID: Final = "0000ff89-0000-1000-8000-00805f9b34fb"
COUNTDOWN_UUID: Final = "0000ff8a-0000-1000-8000-00805f9b34fb"

ZONE2_CONFIG_UUID: Final = "0000ff8b-0000-1000-8000-00805f9b34fb"
ZONE2_TIMER_UUID: Final = "0000ff8c-0000-1000-8000-00805f9b34fb"
ZONE2_CYCLING_UUID: Final = "0000ff8d-0000-1000-8000-00805f9b34fb"
ZONE2_DIAGNOSTIC_UUID: Final = "0000ff8e-0000-1000-8000-00805f9b34fb"
STATUS_NOTIFY_UUID: Final = "0000ff8f-0000-1000-8000-00805f9b34fb"

# Compatibility aliases used by some current project files.
FF81_UUID: Final = PASSCODE_UUID
FF82_UUID: Final = NOTIFY_UUID
FF83_UUID: Final = COMMAND_UUID
FF84_UUID: Final = TIME_UUID
FF86_UUID: Final = ZONE1_CONFIG_UUID
FF87_UUID: Final = ZONE1_TIMER_UUID
FF88_UUID: Final = ZONE1_CYCLING_UUID
FF89_UUID: Final = ZONE1_DIAGNOSTIC_UUID
FF8A_UUID: Final = COUNTDOWN_UUID
FF8B_UUID: Final = ZONE2_CONFIG_UUID
FF8C_UUID: Final = ZONE2_TIMER_UUID
FF8D_UUID: Final = ZONE2_CYCLING_UUID
FF8E_UUID: Final = ZONE2_DIAGNOSTIC_UUID
FF8F_UUID: Final = STATUS_NOTIFY_UUID

ZONE_CONFIG_UUID: Final = {
    1: ZONE1_CONFIG_UUID,
    2: ZONE2_CONFIG_UUID,
}

ZONE_TIMER_UUID: Final = {
    1: ZONE1_TIMER_UUID,
    2: ZONE2_TIMER_UUID,
}

ZONE_CYCLING_UUID: Final = {
    1: ZONE1_CYCLING_UUID,
    2: ZONE2_CYCLING_UUID,
}

ZONE_DIAGNOSTIC_UUID: Final = {
    1: ZONE1_DIAGNOSTIC_UUID,
    2: ZONE2_DIAGNOSTIC_UUID,
}

# ---------------------------------------------------------------------------
# First-generation FCC0 characteristics
# ---------------------------------------------------------------------------

FIRST_C1_UUID: Final = "0000fcc1-0000-1000-8000-00805f9b34fb"
FIRST_C2_UUID: Final = "0000fcc2-0000-1000-8000-00805f9b34fb"
FIRST_C3_UUID: Final = "0000fcc3-0000-1000-8000-00805f9b34fb"
FIRST_C4_UUID: Final = "0000fcc4-0000-1000-8000-00805f9b34fb"

FIRST_D1_UUID: Final = "0000fcd1-0000-1000-8000-00805f9b34fb"
FIRST_D2_UUID: Final = "0000fcd2-0000-1000-8000-00805f9b34fb"
FIRST_D3_UUID: Final = "0000fcd3-0000-1000-8000-00805f9b34fb"
FIRST_D4_UUID: Final = "0000fcd4-0000-1000-8000-00805f9b34fb"
FIRST_D5_UUID: Final = "0000fcd5-0000-1000-8000-00805f9b34fb"
FIRST_D6_UUID: Final = "0000fcd6-0000-1000-8000-00805f9b34fb"
FIRST_D7_UUID: Final = "0000fcd7-0000-1000-8000-00805f9b34fb"
FIRST_D8_UUID: Final = "0000fcd8-0000-1000-8000-00805f9b34fb"
FIRST_D9_UUID: Final = "0000fcd9-0000-1000-8000-00805f9b34fb"

FIRST_COMMAND_UUID: Final = FIRST_D9_UUID

# ---------------------------------------------------------------------------
# Coordinator / runtime constants
# ---------------------------------------------------------------------------

DEFAULT_SCAN_INTERVAL: Final = timedelta(seconds=30)
CONNECTION_TIMEOUT: Final = 15
COMMAND_DELAY: Final = 0.20
MAX_RETRIES: Final = 3

MIN_RUNTIME: Final = 0
DEFAULT_RUNTIME: Final = 600
MAX_RUNTIME: Final = 3600

ZONE_1: Final = 1
ZONE_2: Final = 2
VALID_ZONES: Final = (ZONE_1, ZONE_2)

ZONE_NAMES: Final = {
    ZONE_1: "Zone 1",
    ZONE_2: "Zone 2",
}

DAY_NAMES: Final = (
    "mon", "tue", "wed", "thu", "fri", "sat", "sun",
)

# ---------------------------------------------------------------------------
# HA platforms
# ---------------------------------------------------------------------------

PLATFORMS: Final = (
    "binary_sensor",
    "button",
    "number",
    "select",
    "sensor",
    "switch",
    "text",
)

# ---------------------------------------------------------------------------
# Entity attributes / state keys
# ---------------------------------------------------------------------------

ATTR_ZONE: Final = "zone"
ATTR_RUNTIME: Final = "runtime"
ATTR_REMAINING: Final = "remaining"
ATTR_BATTERY: Final = "battery"
ATTR_TIMER_ENABLED: Final = "timer_enabled"
ATTR_CYCLING_ENABLED: Final = "cycling_enabled"

STATE_IDLE: Final = "idle"
STATE_RUNNING: Final = "running"
STATE_PAUSED: Final = "paused"
STATE_FINISHED: Final = "finished"
STATE_ERROR: Final = "error"

KEY_BATTERY: Final = "battery"
KEY_CONNECTED: Final = "connected"
KEY_ACTIVE_ZONE: Final = "active_zone"
KEY_REMAINING_SECONDS: Final = "remaining_seconds"
KEY_TIMER: Final = "timer"
KEY_CYCLING: Final = "cycling"

# ---------------------------------------------------------------------------
# Services / logging
# ---------------------------------------------------------------------------

SERVICE_START_ZONE: Final = "start_zone"
SERVICE_STOP: Final = "stop"
SERVICE_REFRESH: Final = "refresh"
SERVICE_SYNC: Final = "sync"

LOGGER_NAME: Final = "custom_components.hunter_btt"
