"""Switch platform for TV Remote — calls Node.js HTTP server directly."""
import logging

import aiohttp
from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CONF_HOST, CONF_NAME, CONF_PORT, DEFAULT_NAME, DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    async_add_entities([TvRemoteSwitch(entry)], update_before_add=True)


class TvRemoteSwitch(SwitchEntity):
    """Represents the TV power switch in Home Assistant."""

    _attr_icon = "mdi:television"

    def __init__(self, entry: ConfigEntry) -> None:
        self._host           = entry.data[CONF_HOST]
        self._port           = entry.data[CONF_PORT]
        self._attr_name      = entry.data.get(CONF_NAME, DEFAULT_NAME)
        self._attr_unique_id = f"{DOMAIN}_{self._host}_{self._port}"
        self._is_on          = False
        self._available      = False

    @property
    def is_on(self) -> bool:
        return self._is_on

    @property
    def available(self) -> bool:
        return self._available

    def _base_url(self) -> str:
        return f"http://{self._host}:{self._port}"

    async def async_update(self) -> None:
        """Poll /status to sync state."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self._base_url()}/status", timeout=aiohttp.ClientTimeout(total=5)
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        self._is_on     = data.get("state", "OFF").upper() == "ON"
                        self._available = True
                    else:
                        self._available = False
        except Exception as err:
            _LOGGER.warning("TV Remote unreachable: %s", err)
            self._available = False

    async def async_turn_on(self, **kwargs) -> None:
        await self._post("/on")

    async def async_turn_off(self, **kwargs) -> None:
        await self._post("/off")

    async def _post(self, endpoint: str) -> None:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self._base_url()}{endpoint}",
                    timeout=aiohttp.ClientTimeout(total=5),
                ) as resp:
                    if resp.status in (200, 202):
                        self._available = True
                    else:
                        _LOGGER.error("TV Remote returned %s for %s", resp.status, endpoint)
        except Exception as err:
            _LOGGER.error("TV Remote request failed: %s", err)
            self._available = False
        self.async_write_ha_state()
