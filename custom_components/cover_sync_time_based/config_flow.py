"""Config flow for cover_sync_time_based."""

from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.helpers import selector

from .const import (
    DOMAIN,
    CONF_OPEN_SWITCH_ENTITY_ID,
    CONF_CLOSE_SWITCH_ENTITY_ID,
    CONF_TRAVELLING_TIME_UP,
    CONF_TRAVELLING_TIME_DOWN,
    CONF_EXTRA_TIME_OPEN,
    CONF_EXTRA_TIME_CLOSE,
    CONF_SEND_STOP_AT_ENDS,
    DEFAULT_TRAVEL_TIME,
    DEFAULT_EXTRA_TIME,
    DEFAULT_SEND_STOP_AT_ENDS,
)


def _schema_with_defaults(user_input: dict | None = None) -> vol.Schema:
    """Return schema for create/update."""
    user_input = user_input or {}
    return vol.Schema(
        {
            vol.Required(CONF_NAME, default=user_input.get(CONF_NAME, "Rollo")): selector.TextSelector(),
            vol.Required(
                CONF_OPEN_SWITCH_ENTITY_ID,
                default=user_input.get(CONF_OPEN_SWITCH_ENTITY_ID),
            ): selector.EntitySelector(
                selector.EntitySelectorConfig(domain=["switch"], multiple=False)
            ),
            vol.Required(
                CONF_CLOSE_SWITCH_ENTITY_ID,
                default=user_input.get(CONF_CLOSE_SWITCH_ENTITY_ID),
            ): selector.EntitySelector(
                selector.EntitySelectorConfig(domain=["switch"], multiple=False)
            ),
            vol.Required(
                CONF_TRAVELLING_TIME_UP,
                default=user_input.get(CONF_TRAVELLING_TIME_UP, DEFAULT_TRAVEL_TIME),
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(min=1, max=300, mode=selector.NumberSelectorMode.BOX)
            ),
            vol.Required(
                CONF_TRAVELLING_TIME_DOWN,
                default=user_input.get(CONF_TRAVELLING_TIME_DOWN, DEFAULT_TRAVEL_TIME),
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(min=1, max=300, mode=selector.NumberSelectorMode.BOX)
            ),
            vol.Optional(
                CONF_EXTRA_TIME_OPEN,
                default=user_input.get(CONF_EXTRA_TIME_OPEN, DEFAULT_EXTRA_TIME),
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(min=0, max=30, step=0.5, mode=selector.NumberSelectorMode.BOX)
            ),
            vol.Optional(
                CONF_EXTRA_TIME_CLOSE,
                default=user_input.get(CONF_EXTRA_TIME_CLOSE, DEFAULT_EXTRA_TIME),
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(min=0, max=30, step=0.5, mode=selector.NumberSelectorMode.BOX)
            ),
            vol.Optional(
                CONF_SEND_STOP_AT_ENDS,
                default=user_input.get(CONF_SEND_STOP_AT_ENDS, DEFAULT_SEND_STOP_AT_ENDS),
            ): selector.BooleanSelector(),
        }
    )


class CoverSyncTimeBasedConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for cover_sync_time_based."""

    VERSION = 1

    async def async_step_user(self, user_input: dict | None = None):
        """Handle first step."""
        if user_input is not None:
            await self.async_set_unique_id(
                f"{user_input[CONF_OPEN_SWITCH_ENTITY_ID]}::{user_input[CONF_CLOSE_SWITCH_ENTITY_ID]}"
            )
            self._abort_if_unique_id_configured()
            return self.async_create_entry(title=user_input[CONF_NAME], data=user_input)

        return self.async_show_form(step_id="user", data_schema=_schema_with_defaults())

    @staticmethod
    def async_get_options_flow(config_entry):
        """Get options flow."""
        return CoverSyncTimeBasedOptionsFlow(config_entry)


class CoverSyncTimeBasedOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self.config_entry = config_entry

    async def async_step_init(self, user_input: dict | None = None):
        """Manage options."""
        current = {**self.config_entry.data, **self.config_entry.options}
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(step_id="init", data_schema=_schema_with_defaults(current))
