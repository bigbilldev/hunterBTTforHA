"""Constants for the Hunter BTT Home Assistant integration."""

from __future__ import annotations

from datetime import timedelta
from typing import Final

# Integration identity.
# IMPORTANT: the installed integration directory and manifest use hunter_btt.
DOMAIN: Final = "hunter_btt"
NAME: Final = "Hunter BTT"
MANUFACTURER: Final = "Hunter Industries"
MODEL: Final = "BTT"
SW_VERSION: Final = "Unknown"
DEFAULT_NAME: Final = "Hunter BTT"

# BLE services.
FIRST_SERVICE_UUID: Final = "0000fcc0-0000-1000-8000-00805f9b34fb"
SECOND_SERVICE_UUID: Final = "0000ff80-0000-1000-8000-00805f9b34fb"
SERVICE_UUID: Final = SECOND_SERVICE_UUID
BATTERY_SERVICE_UUID: Final = "0000180f-0000-1000-8000-00805f9b34fb"

# Second-generation characteristics.
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

# First-generation characteristic aliases.
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

# Per-zone maps.
ZONE_CONFIG_UUID: Final = {1: ZONE1_CONFIG_UUID, 2: ZONE2_CONFIG_UUID}
ZONE_TIMER_UUID: Final = {1: ZONE1_TIMER_UUID, 2: ZONE2_TIMER_UUID}
ZONE_CYCLING_UUID: Final = {1: ZONE1_CYCLING_UUID, 2: ZONE2_CYCLING_UUID}
ZONE_DIAGNOSTIC_UUID: Final = {1: ZONE1_DIAGNOSTIC_UUID, 2: ZONE2_DIAGNOSTIC_UUID}

# Home Assistant config-entry keys.
# CONF_ADDRESS is also exported by homeassistant.const; keeping this local
# alias preserves compatibility with existing project imports.
CONF_ADDRESS: Final = "address"
CONF_NAME: Final = "name"
CONF_PASSCODE: Final = "passcode"
CONF_RUNTIME: Final = "runtime"
CONF_ZONE: Final = "zone"
CONF_TIMER: Final = "timer"
CONF_CYCLING: Final = "cycling"
CONF_DAYS: Final = "days"
CONF_START_TIMES: Final = "start_times"
CONF_SOAK: Final = "soak"
CONF_POLL_INTERVAL: Final = "poll_interval"
CONF_AUTOMATIC_REFRESH: Final = "automatic_refresh"
CONF_DEBUG: Final = "debug_logging"

# Runtime limits.
MIN_RUNTIME: Final = 0
DEFAULT_RUNTIME: Final = 600
MAX_RUNTIME: Final = 3600
ZONE_COUNT: Final = 2
VALID_ZONES: Final = (1, 2)

# Timing/retry values.
DEFAULT_SCAN_INTERVAL: Final = timedelta(seconds=30)
CONNECTION_TIMEOUT: Final = 15
COMMAND_TIMEOUT: Final = 5.0
NOTIFICATION_TIMEOUT: Final = 5.0
COMMAND_DELAY: Final = 0.20
PREPARE_DELAY: Final = 0.20
ARM_DELAY: Final = 0.50
STOP_DELAY: Final = 0.20
RECONNECT_DELAY: Final = 1.0
MAX_RETRIES: Final = 3

# State/data keys.
DATA_CONNECTED: Final = "connected"
DATA_BATTERY: Final = "battery"
DATA_RUNNING: Final = "running"
DATA_ACTIVE_ZONE: Final = "active_zone"
DATA_REMAINING_SECONDS: Final = "remaining_seconds"
DATA_ZONES: Final = "zones"
DATA_LAST_UPDATE: Final = "last_update"
DATA_TIMER: Final = "timer"
DATA_CYCLING: Final = "cycling"
DATA_RUNTIME: Final = "runtime"
DATA_DIAGNOSTICS: Final = "diagnostics"

# Attributes.
ATTR_ZONE: Final = "zone"
ATTR_RUNTIME: Final = "runtime"
ATTR_REMAINING: Final = "remaining"
ATTR_START_TIMES: Final = "start_times"
ATTR_TIMER_ENABLED: Final = "timer_enabled"
ATTR_CYCLING_ENABLED: Final = "cycling_enabled"
ATTR_DAYS: Final = "days"
ATTR_SOAK: Final = "soak"
ATTR_CONNECTED: Final = "connected"
ATTR_ADDRESS: Final = "address"
ATTR_LAST_COMMAND: Final = "last_command"
ATTR_BATTERY: Final = "battery"

# Services.
SERVICE_START_ZONE: Final = "start_zone"
SERVICE_STOP: Final = "stop"
SERVICE_REFRESH: Final = "refresh"
SERVICE_SYNC: Final = "sync"

# Platforms.
PLATFORMS: Final = (
    "sensor",
    "binary_sensor",
    "switch",
    "button",
    "number",
)

# Days.
DAY_NAMES: Final = (
    "mon", "tue", "wed", "thu", "fri", "sat", "sun",
)

# Defaults/logging.
DEFAULT_PASSCODE: Final = b"\x00\x00\x00\x00"
LOGGER_NAME: Final = DOMAIN
DEBUG_BLE: Final = False
DEBUG_PROTOCOL: Final = False

SIGNAL_NOTIFICATION: Final = f"{DOMAIN}_notification"
SIGNAL_REFRESH: Final = f"{DOMAIN}_refresh"
SIGNAL_CONNECTED: Final = f"{DOMAIN}_connected"
SIGNAL_DISCONNECTED: Final = f"{DOMAIN}_disconnected"
