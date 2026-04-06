"""Open-Meteo Weather integration."""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .coordinator_air_quality import AirQualityCoordinator
from .coordinator_location import LocationCoordinator
from .coordinator_weather import WeatherCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Open-Meteo Weather from a config entry."""
    location_coordinator = LocationCoordinator(hass, entry)
    weather_coordinator = WeatherCoordinator(hass, entry)
    air_quality_coordinator = AirQualityCoordinator(hass, entry)

    # Location is fetched first — city name is needed by DeviceInfo in sensor.py
    await location_coordinator.async_config_entry_first_refresh()
    await weather_coordinator.async_config_entry_first_refresh()
    await air_quality_coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        "location": location_coordinator,
        "weather": weather_coordinator,
        "air_quality": air_quality_coordinator,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
