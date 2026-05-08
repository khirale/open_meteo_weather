"""Coordinator for Open-Meteo Forecast API."""
from __future__ import annotations

import logging
from datetime import datetime, timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    CONF_LATITUDE,
    CONF_LONGITUDE,
    DOMAIN,
    FORECAST_API_URL,
    FORECAST_DAYS,
    HOURLY_HOURS,
    UPDATE_INTERVAL_HOURS,
    WMO_CODES,
    wmo_to_fr,
)

_LOGGER = logging.getLogger(__name__)

# Open-Meteo field names
_CURRENT_FIELDS = (
    "temperature_2m",
    "relative_humidity_2m",
    "apparent_temperature",
    "precipitation",
    "wind_speed_10m",
    "wind_direction_10m",
    "wind_gusts_10m",
    "surface_pressure",
    "uv_index",
    "shortwave_radiation",
    "weather_code",
)

_HOURLY_FIELDS = (
    "temperature_2m",
    "precipitation_probability",
    "wind_speed_10m",
    "wind_direction_10m",
    "uv_index",
    "weather_code",
)

_DAILY_FIELDS = (
    "temperature_2m_max",
    "temperature_2m_min",
    "precipitation_sum",
    "weather_code",
    "uv_index_max",
    "wind_speed_10m_max",
    "sunrise",
    "sunset",
)


def _find_current_hour_index(times: list[str]) -> int:
    """Return the index in the hourly time array matching the current local hour."""
    now_str = datetime.now().strftime("%Y-%m-%dT%H:00")
    for i, t in enumerate(times):
        if t == now_str:
            return i
    return 0


def _build_hourly_dict(values: list, start_idx: int) -> dict[str, float | None]:
    """Build {h0: v, h1: v, ...} dict from a list starting at start_idx."""
    return {
        f"h{i}": values[start_idx + i]
        for i in range(HOURLY_HOURS)
        if start_idx + i < len(values)
    }


def _build_daily_dict(values: list) -> dict[str, float | None]:
    """Build {j0: v, j1: v, ...} dict from a list."""
    return {f"j{i}": values[i] for i in range(min(FORECAST_DAYS, len(values)))}


def _map_wmo_key(code: int | None) -> str:
    """Map a WMO code to its technical key string."""
    if code is None:
        return "unknown"
    return WMO_CODES.get(int(code), "unknown")


class WeatherCoordinator(DataUpdateCoordinator):
    """Coordinator that fetches data from the Open-Meteo Forecast API."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_weather",
            update_interval=timedelta(hours=UPDATE_INTERVAL_HOURS),
        )
        self._latitude: float = entry.data[CONF_LATITUDE]
        self._longitude: float = entry.data[CONF_LONGITUDE]

    async def _async_update_data(self) -> dict:
        """Fetch and parse forecast data."""
        session = async_get_clientsession(self.hass)
        params = {
            "latitude": self._latitude,
            "longitude": self._longitude,
            "current": ",".join(_CURRENT_FIELDS),
            "hourly": ",".join(_HOURLY_FIELDS),
            "daily": ",".join(_DAILY_FIELDS),
            "wind_speed_unit": "kmh",
            "timezone": "auto",
            "forecast_days": FORECAST_DAYS,
        }

        try:
            async with session.get(FORECAST_API_URL, params=params) as resp:
                resp.raise_for_status()
                raw = await resp.json()
        except Exception as err:
            raise UpdateFailed(f"Open-Meteo Forecast API error: {err}") from err

        current = raw.get("current", {})

        current_wmo_code = current.get("weather_code")
        current_condition_key = _map_wmo_key(current_wmo_code)
        current["condition_label"] = wmo_to_fr(current_condition_key)
        current["condition_key"] = current_condition_key

        hourly_raw = raw.get("hourly", {})
        times = hourly_raw.get("time", [])
        idx = _find_current_hour_index(times)

        hourly: dict[str, dict] = {}
        for field in _HOURLY_FIELDS:
            hourly[field] = _build_hourly_dict(hourly_raw.get(field, []), idx)

        wmo_values = hourly_raw.get("weather_code", [])
        hourly["condition"] = {
            f"h{i}": wmo_to_fr(_map_wmo_key(wmo_values[idx + i]))
            for i in range(HOURLY_HOURS)
            if idx + i < len(wmo_values)
        }

        daily_raw = raw.get("daily", {})
        daily: dict[str, dict] = {}
        for field in _DAILY_FIELDS:
            daily[field] = _build_daily_dict(daily_raw.get(field, []))

        daily_wmo = daily_raw.get("weather_code", [])
        daily["condition"] = {
            f"j{i}": wmo_to_fr(_map_wmo_key(daily_wmo[i] if i < len(daily_wmo) else None))
            for i in range(FORECAST_DAYS)
        }

        return {
            "current": current,
            "hourly": hourly,
            "daily": daily,
        }
