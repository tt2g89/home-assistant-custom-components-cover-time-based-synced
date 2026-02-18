"""Config flow for cover_sync_time_based."""

from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.helpers import entity_registry as er
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


def _extract_device_id(unique_id: str | None) -> str | None:
    """Extract internal device id from entity unique id."""
    if not unique_id:
        return None
    prefix = "cover_timebased_synced_uuid_"
    if unique_id.startswith(prefix):
        return unique_id[len(prefix):]
    return unique_id


def _first_not_none(*values):
    """Return the first value that is not None."""
    for value in values:
        if value is not None:
            return value
    return None


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
    _migrate_defaults: dict = {}
    _legacy_domain = "cover_time_based_synced"

    def _lookup_yaml_device_config(self, device_id: str | None) -> dict:
        """Return YAML device config for a known device id, if available."""
        if not device_id:
            return {}
        config = self.hass.config.as_dict()
        cover_cfg = config.get("cover")
        platform_sections: list[dict] = []
        if isinstance(cover_cfg, list):
            platform_sections = [item for item in cover_cfg if isinstance(item, dict)]
        elif isinstance(cover_cfg, dict):
            platform_sections = [cover_cfg]

        for section in platform_sections:
            if section.get("platform") not in {DOMAIN, self._legacy_domain}:
                continue
            devices = section.get("devices")
            if isinstance(devices, dict) and device_id in devices:
                candidate = devices[device_id]
                if isinstance(candidate, dict):
                    return candidate
        return {}

    async def async_step_user(self, user_input: dict | None = None):
        """Entry menu."""
        return self.async_show_menu(
            step_id="user",
            menu_options=["add_cover", "migrate_cover"],
            sort=True,
        )

    async def async_step_add_cover(self, user_input: dict | None = None):
        """Create a new cover entry from scratch."""
        if user_input is not None:
            await self.async_set_unique_id(
                f"{user_input[CONF_OPEN_SWITCH_ENTITY_ID]}::{user_input[CONF_CLOSE_SWITCH_ENTITY_ID]}"
            )
            self._abort_if_unique_id_configured()
            return self.async_create_entry(title=user_input[CONF_NAME], data=user_input)

        return self.async_show_form(step_id="add_cover", data_schema=_schema_with_defaults())

    async def async_step_migrate_cover(self, user_input: dict | None = None):
        """Select an existing cover entity to migrate into a UI config entry."""
        errors = {}
        if user_input is not None:
            entity_id = user_input["entity_id"]
            registry = er.async_get(self.hass)
            entity_entry = registry.async_get(entity_id)
            platform = entity_entry.platform if entity_entry else None
            if platform not in {DOMAIN, self._legacy_domain}:
                errors["base"] = "unsupported_entity_platform"
            else:
                state = self.hass.states.get(entity_id)
                attrs = state.attributes if state else {}
                device_id = _extract_device_id(entity_entry.unique_id if entity_entry else None)
                yaml_cfg = self._lookup_yaml_device_config(device_id)
                self._migrate_defaults = {
                    CONF_NAME: attrs.get("friendly_name", entity_id.split(".")[-1]),
                    CONF_OPEN_SWITCH_ENTITY_ID: _first_not_none(
                        attrs.get(CONF_OPEN_SWITCH_ENTITY_ID),
                        yaml_cfg.get(CONF_OPEN_SWITCH_ENTITY_ID),
                    ),
                    CONF_CLOSE_SWITCH_ENTITY_ID: _first_not_none(
                        attrs.get(CONF_CLOSE_SWITCH_ENTITY_ID),
                        yaml_cfg.get(CONF_CLOSE_SWITCH_ENTITY_ID),
                    ),
                    CONF_TRAVELLING_TIME_UP: _first_not_none(
                        attrs.get(CONF_TRAVELLING_TIME_UP),
                        yaml_cfg.get(CONF_TRAVELLING_TIME_UP),
                        DEFAULT_TRAVEL_TIME,
                    ),
                    CONF_TRAVELLING_TIME_DOWN: _first_not_none(
                        attrs.get(CONF_TRAVELLING_TIME_DOWN),
                        yaml_cfg.get(CONF_TRAVELLING_TIME_DOWN),
                        DEFAULT_TRAVEL_TIME,
                    ),
                    CONF_EXTRA_TIME_OPEN: _first_not_none(
                        attrs.get(CONF_EXTRA_TIME_OPEN),
                        yaml_cfg.get(CONF_EXTRA_TIME_OPEN),
                        DEFAULT_EXTRA_TIME,
                    ),
                    CONF_EXTRA_TIME_CLOSE: _first_not_none(
                        attrs.get(CONF_EXTRA_TIME_CLOSE),
                        yaml_cfg.get(CONF_EXTRA_TIME_CLOSE),
                        DEFAULT_EXTRA_TIME,
                    ),
                    CONF_SEND_STOP_AT_ENDS: _first_not_none(
                        attrs.get(CONF_SEND_STOP_AT_ENDS),
                        yaml_cfg.get(CONF_SEND_STOP_AT_ENDS),
                        DEFAULT_SEND_STOP_AT_ENDS,
                    ),
                }
                return await self.async_step_migrate_cover_config()

        return self.async_show_form(
            step_id="migrate_cover",
            data_schema=vol.Schema(
                {
                    vol.Required("entity_id"): selector.EntitySelector(
                        selector.EntitySelectorConfig(
                            domain=["cover"],
                            multiple=False,
                        )
                    )
                }
            ),
            errors=errors,
        )

    async def async_step_migrate_cover_config(self, user_input: dict | None = None):
        """Create config entry from selected existing cover plus relay mapping."""
        if user_input is not None:
            await self.async_set_unique_id(
                f"{user_input[CONF_OPEN_SWITCH_ENTITY_ID]}::{user_input[CONF_CLOSE_SWITCH_ENTITY_ID]}"
            )
            self._abort_if_unique_id_configured()
            return self.async_create_entry(title=user_input[CONF_NAME], data=user_input)

        return self.async_show_form(
            step_id="migrate_cover_config",
            data_schema=_schema_with_defaults(self._migrate_defaults),
        )

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
