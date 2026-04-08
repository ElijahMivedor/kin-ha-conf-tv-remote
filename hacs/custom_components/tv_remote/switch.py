"""Switch platform for TV Remote — publishes ON/OFF over MQTT."""
import logging

from homeassistant.components import mqtt
from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    CONF_COMMAND_TOPIC,
    CONF_NAME,
    CONF_STATE_TOPIC,
    DEFAULT_NAME,
    DOMAIN,
    PAYLOAD_OFF,
    PAYLOAD_ON,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    async_add_entities([TvRemoteSwitch(entry)])


class TvRemoteSwitch(SwitchEntity):
    """Represents the TV power switch in Home Assistant."""

    _attr_has_entity_name = True
    _attr_icon = "mdi:television"

    def __init__(self, entry: ConfigEntry) -> None:
        self._entry          = entry
        self._command_topic  = entry.data[CONF_COMMAND_TOPIC]
        self._state_topic    = entry.data[CONF_STATE_TOPIC]
        self._attr_name      = entry.data.get(CONF_NAME, DEFAULT_NAME)
        self._attr_unique_id = f"{DOMAIN}_{self._command_topic}"
        self._is_on          = False
        self._available      = False

    @property
    def is_on(self) -> bool:
        return self._is_on

    @property
    def available(self) -> bool:
        return self._available

    async def async_added_to_hass(self) -> None:
        """Subscribe to the state topic when added to HA."""

        @callback
        def state_received(msg):
            payload = msg.payload.strip().upper()
            _LOGGER.debug("State message received: %s", payload)

            if payload == "OFFLINE":
                self._available = False
            elif payload == "TRANSITIONING":
                # Keep current is_on; mark as unavailable briefly so UI shows spinner
                self._available = True
            elif payload == PAYLOAD_ON:
                self._is_on     = True
                self._available = True
            elif payload == PAYLOAD_OFF:
                self._is_on     = False
                self._available = True
            else:
                _LOGGER.warning("Unexpected state payload: %s", payload)
                return

            self.async_write_ha_state()

        await mqtt.async_subscribe(
            self.hass,
            self._state_topic,
            state_received,
            qos=1,
        )

    async def async_turn_on(self, **kwargs) -> None:
        await mqtt.async_publish(
            self.hass,
            self._command_topic,
            PAYLOAD_ON,
            qos=1,
            retain=False,
        )

    async def async_turn_off(self, **kwargs) -> None:
        await mqtt.async_publish(
            self.hass,
            self._command_topic,
            PAYLOAD_OFF,
            qos=1,
            retain=False,
        )
