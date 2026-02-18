"""Constants for cover_sync_time_based."""

DOMAIN = "cover_sync_time_based"
PLATFORMS = ["cover"]

CONF_TRAVELLING_TIME_DOWN = "travelling_time_down"
CONF_TRAVELLING_TIME_UP = "travelling_time_up"
CONF_EXTRA_TIME_OPEN = "extra_time_open"
CONF_EXTRA_TIME_CLOSE = "extra_time_close"
CONF_SEND_STOP_AT_ENDS = "send_stop_at_ends"
CONF_OPEN_SWITCH_ENTITY_ID = "open_switch_entity_id"
CONF_CLOSE_SWITCH_ENTITY_ID = "close_switch_entity_id"

DEFAULT_TRAVEL_TIME = 25
DEFAULT_EXTRA_TIME = 0
DEFAULT_SEND_STOP_AT_ENDS = False
