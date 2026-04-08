"""Config flow for TV Remote."""
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback

from .const import CONF_HOST, CONF_NAME, CONF_PORT, DEFAULT_NAME, DEFAULT_PORT, DOMAIN

STEP_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME, default=DEFAULT_NAME): str,
        vol.Required(CONF_HOST): str,
        vol.Required(CONF_PORT, default=DEFAULT_PORT): int,
    }
)


class TvRemoteConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle the initial setup UI in Home Assistant."""

    VERSION = 2

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            await self.async_set_unique_id(f"{user_input[CONF_HOST]}:{user_input[CONF_PORT]}")
            self._abort_if_unique_id_configured()
            return self.async_create_entry(title=user_input[CONF_NAME], data=user_input)

        return self.async_show_form(step_id="user", data_schema=STEP_SCHEMA)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return TvRemoteOptionsFlow(config_entry)


class TvRemoteOptionsFlow(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self._entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        schema = vol.Schema(
            {
                vol.Required(CONF_HOST, default=self._entry.data.get(CONF_HOST, "")): str,
                vol.Required(CONF_PORT, default=self._entry.data.get(CONF_PORT, DEFAULT_PORT)): int,
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema)
