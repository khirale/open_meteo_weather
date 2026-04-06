"""Coordinator for reverse geocoding via Nominatim (OpenStreetMap)."""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import CONF_LATITUDE, CONF_LONGITUDE, DOMAIN

_LOGGER = logging.getLogger(__name__)

NOMINATIM_URL = "https://nominatim.openstreetmap.org/reverse"


class LocationCoordinator(DataUpdateCoordinator):
    """
    Coordinator that performs a single reverse geocoding call via Nominatim.

    update_interval=None — no automatic refresh.
    Data is fetched once via async_config_entry_first_refresh.
    """

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_location",
            update_interval=None,
        )
        self._latitude: float = entry.data[CONF_LATITUDE]
        self._longitude: float = entry.data[CONF_LONGITUDE]

    async def _async_update_data(self) -> dict:
        session = async_get_clientsession(self.hass)
        params = {
            "lat": self._latitude,
            "lon": self._longitude,
            "format": "json",
            "addressdetails": 1,
        }
        headers = {
            "User-Agent": "HomeAssistant/open_meteo_weather (+https://github.com/khirale/open_meteo_weather)",
        }

        try:
            async with session.get(
                NOMINATIM_URL, params=params, headers=headers
            ) as resp:
                resp.raise_for_status()
                raw = await resp.json()
        except Exception as err:
            raise UpdateFailed(f"Nominatim reverse geocoding error: {err}") from err

        address = raw.get("address", {})

        city = (
            address.get("city")
            or address.get("town")
            or address.get("village")
            or address.get("hamlet")
            or address.get("municipality")
            or raw.get("display_name", "Unknown")
        )

        return {
            "city": city,
            "latitude": self._latitude,
            "longitude": self._longitude,
            "country": address.get("country"),
            "country_code": address.get("country_code", "").upper(),
            "postcode": address.get("postcode"),
            "state": address.get("state"),
        }
