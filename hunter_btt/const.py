"""
Constants for the Hunter BTT Home Assistant integration.
"""

from __future__ import annotations

from datetime import timedelta
from typing import Final

DOMAIN: Final = "hunter_btt"

#
# Integration
#

NAME: Final = "Hunter BTT"

MANUFACTURER: Final = "Hunter Industries"

MODEL: Final = "BTT"

SW_VERSION: Final = "Unknown"

#
# BLE
#

SERVICE_UUID: Final = "0000ff80-0000-1000-8000-00805f9b34fb"

BATTERY_SERVICE_UUID: Final = "0000180f-0000-1000-8000-00805f9b34fb"

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

BATTERY_LEVEL_UUID: Final = "00002a19-0000-1000-8000-00805f9b34fb"

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

#
# Device
#

ZONE_COUNT: Final = 2

VALID_ZONES: Final = (1, 2)

MAX_RUNTIME_SECONDS: Final = 3600

DEFAULT_RUNTIME_SECONDS: Final = 600

MAX_START_TIMES: Final = 4

MAX_DAY_MASK: Final = 0x7F

OFF_TIME: Final = -1

#
# Coordinator
#

DEFAULT_SCAN_INTERVAL: Final = timedelta(seconds=60)

MIN_SCAN_INTERVAL: Final = timedelta(seconds=15)

FAST_SCAN_INTERVAL: Final = timedelta(seconds=5)

#
# BLE timing
#

CONNECT_TIMEOUT: Final = 15.0

COMMAND_TIMEOUT: Final = 5.0

NOTIFICATION_TIMEOUT: Final = 5.0

PREPARE_DELAY: Final = 0.20

ARM_DELAY: Final = 0.50

STOP_DELAY: Final = 0.20

RECONNECT_DELAY: Final = 1.0

MAX_RETRIES: Final = 2

#
# Config entry keys
#

CONF_RUNTIME = "runtime"

CONF_ZONE = "zone"

CONF_TIMER = "timer"

CONF_CYCLING = "cycling"

CONF_DAYS = "days"

CONF_START_TIMES = "start_times"

CONF_SOAK = "soak"

CONF_POLL_INTERVAL = "poll_interval"

CONF_AUTOMATIC_REFRESH = "automatic_refresh"

CONF_DEBUG = "debug_logging"

#
# DataUpdateCoordinator state keys
#

DATA_CONNECTED = "connected"

DATA_BATTERY = "battery"

DATA_RUNNING = "running"

DATA_ACTIVE_ZONE = "active_zone"

DATA_REMAINING_SECONDS = "remaining_seconds"

DATA_ZONES = "zones"

DATA_LAST_UPDATE = "last_update"

DATA_TIMER = "timer"

DATA_CYCLING = "cycling"

DATA_RUNTIME = "runtime"

DATA_DIAGNOSTICS = "diagnostics"

#
# Dispatcher signals
#

SIGNAL_NOTIFICATION = f"{DOMAIN}_notification"

SIGNAL_REFRESH = f"{DOMAIN}_refresh"

SIGNAL_CONNECTED = f"{DOMAIN}_connected"

SIGNAL_DISCONNECTED = f"{DOMAIN}_disconnected"

#
# Entity attribute names
#

ATTR_ZONE = "zone"

ATTR_RUNTIME = "runtime"

ATTR_REMAINING = "remaining"

ATTR_START_TIMES = "start_times"

ATTR_TIMER_ENABLED = "timer_enabled"

ATTR_CYCLING_ENABLED = "cycling_enabled"

ATTR_DAYS = "days"

ATTR_SOAK = "soak"

ATTR_CONNECTED = "connected"

ATTR_ADDRESS = "address"

ATTR_LAST_COMMAND = "last_command"

#
# Home Assistant platforms
#

PLATFORMS: Final = (
    "sensor",
    "binary_sensor",
    "switch",
    "button",
    "number",
)

#
# Logging
#

LOGGER_NAME: Final = DOMAIN

DEBUG_BLE: Final = False

DEBUG_PROTOCOL: Final = False

#
# Default passcode
#
# Replace if the protocol determines a different authentication
# mechanism for your controller.
#

DEFAULT_PASSCODE: Final = b"\x00\x00\x00\x00"

#
# Days
#

DAY_NAMES: Final = (
    "mon",
    "tue",
    "wed",
    "thu",
    "fri",
    "sat",
    "sun",
)