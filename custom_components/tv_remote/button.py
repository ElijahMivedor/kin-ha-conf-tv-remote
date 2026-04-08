"""Button platform for TV Remote — Turn On, Turn Off, Toggle."""
import logging

import aiohttp
from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CONF_HOST, CONF_PORT, DOMAIN

_LOGGER = logging.getLogger(__name__)

BUTTONS = [
    {"key": "on",     "name": "Turn On",  "icon": "mdi:television-play"},
    {"key": "off",    "name": "Turn Off", "icon": "mdi:television-off"},
    {"key": "toggle", "name": "Toggle",   "icon": "mdi:television"},
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    host = entry.data[CONF_HOST]
    port = entry.data[CONF_PORT]
    async_add_entities([TvButton(entry, host, port, b) for b in BUTTONS])


class TvButton(ButtonEntity):
    def __init__(self, entry: ConfigEntry, host: str, port: int, btn: dict) -> None:
        self._host           = host
        self._port           = port
        self._endpoint       = btn["key"]
        self._attr_name      = btn["name"]
        self._attr_icon      = btn["icon"]
        self._attr_unique_id = f"{DOMAIN}_{host}_{port}_{btn['key']}"

    async def async_press(self) -> None:
        url = f"http://{self._host}:{self._port}/{self._endpoint}"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                    if resp.status not in (200, 202):
                        _LOGGER.error("TV Remote /%s returned %s", self._endpoint, resp.status)
        except Exception as err:
            _LOGGER.error("TV Remote request failed: %s", err)
