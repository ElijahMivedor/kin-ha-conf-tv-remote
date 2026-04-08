"""Config flow for TV Remote."""
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback

from .const import (
    CONF_COMMAND_TOPIC,
    CONF_NAME,
    CONF_STATE_TOPIC,
    DEFAULT_COMMAND_TOPIC,
    DEFAULT_NAME,
    DEFAULT_STATE_TOPIC,
    DOMAIN,
)

STEP_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME, default=DEFAULT_NAME): str,
        vol.Required(CONF_COMMAND_TOPIC, default=DEFAULT_COMMAND_TOPIC): str,
        vol.Required(CONF_STATE_TOPIC,   default=DEFAULT_STATE_TOPIC):   str,
    }
)


class TvRemoteConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle the initial setup UI in Home Assistant."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            # Prevent duplicate entries with the same topics
            await self.async_set_unique_id(user_input[CONF_COMMAND_TOPIC])
            self._abort_if_unique_id_configured()
            return self.async_create_entry(
                title=user_input[CONF_NAME],
                data=user_input,
            )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_SCHEMA,
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return TvRemoteOptionsFlow(config_entry)


class TvRemoteOptionsFlow(config_entries.OptionsFlow):
    """Allow editing topics after initial setup."""

    def __init__(self, config_entry):
        self._entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        schema = vol.Schema(
            {
                vol.Required(
                    CONF_COMMAND_TOPIC,
                    default=self._entry.data.get(CONF_COMMAND_TOPIC, DEFAULT_COMMAND_TOPIC),
                ): str,
                vol.Required(
                    CONF_STATE_TOPIC,
                    default=self._entry.data.get(CONF_STATE_TOPIC, DEFAULT_STATE_TOPIC),
                ): str,
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema)
