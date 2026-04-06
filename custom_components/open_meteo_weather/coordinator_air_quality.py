"""Coordinator for Open-Meteo Air Quality API."""
from __future__ import annotations

import logging
from datetime import datetime, timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    AIR_QUALITY_API_URL,
    CONF_LATITUDE,
    CONF_LONGITUDE,
    DOMAIN,
    FORECAST_DAYS,
    HOURLY_HOURS,
    UPDATE_INTERVAL_HOURS,
)

_LOGGER = logging.getLogger(__name__)

_CURRENT_AQ_FIELDS = (
    "european_aqi",
    "pm2_5",
    "pm10",
    "ozone",
    "nitrogen_dioxide",
    "sulphur_dioxide",
    "carbon_monoxide",
)

_HOURLY_AQ_FIELDS = (
    "european_aqi",
    "pm2_5",
    "pm10",
    "ozone",
    "nitrogen_dioxide",
    "sulphur_dioxide",
    "carbon_monoxide",
)

_HOURLY_POLLEN_FIELDS = (
    "birch_pollen",
    "grass_pollen",
    "ragweed_pollen",
)

_HOURS_PER_DAY = 24


def _find_current_hour_index(times: list[str]) -> int:
    """Return the index matching the current local hour."""
    now_str = datetime.now().strftime("%Y-%m-%dT%H:00")
    for i, t in enumerate(times):
        if t == now_str:
            return i
    return 0


def _build_hourly_dict(values: list, start_idx: int) -> dict[str, float | None]:
    """Build {h0: v, h1: v, ...} from start_idx."""
    return {
        f"h{i}": values[start_idx + i]
        for i in range(HOURLY_HOURS)
        if start_idx + i < len(values)
    }


def _build_daily_pollen(values: list, start_idx: int) -> dict[str, float | None]:
    result: dict[str, float | None] = {}
    for day in range(FORECAST_DAYS):
        day_start = day * _HOURS_PER_DAY
        raw_start = day * _HOURS_PER_DAY
        raw_end = raw_start + _HOURS_PER_DAY
        day_values = [
            v for v in values[raw_start:raw_end] if v is not None
        ]
        result[f"j{day}"] = max(day_values) if day_values else None
    return result


class AirQualityCoordinator(DataUpdateCoordinator):

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_air_quality",
            update_interval=timedelta(hours=UPDATE_INTERVAL_HOURS),
        )
        self._latitude: float = entry.data[CONF_LATITUDE]
        self._longitude: float = entry.data[CONF_LONGITUDE]

    async def _async_update_data(self) -> dict:
        session = async_get_clientsession(self.hass)

        all_hourly = list(_HOURLY_AQ_FIELDS) + list(_HOURLY_POLLEN_FIELDS)

        params = {
            "latitude": self._latitude,
            "longitude": self._longitude,
            "current": ",".join(_CURRENT_AQ_FIELDS),
            "hourly": ",".join(all_hourly),
            "timezone": "auto",
            "forecast_days": FORECAST_DAYS,
        }

        try:
            async with session.get(AIR_QUALITY_API_URL, params=params) as resp:
                resp.raise_for_status()
                raw = await resp.json()
        except Exception as err:
            raise UpdateFailed(f"Open-Meteo Air Quality API error: {err}") from err

        current = raw.get("current", {})
        hourly_raw = raw.get("hourly", {})
        times = hourly_raw.get("time", [])
        idx = _find_current_hour_index(times)

        hourly: dict[str, dict] = {}
        for field in _HOURLY_AQ_FIELDS:
            hourly[field] = _build_hourly_dict(hourly_raw.get(field, []), idx)

        pollen: dict[str, dict] = {}
        pollen["tree"] = _build_daily_pollen(
            hourly_raw.get("birch_pollen", []), idx
        )
        pollen["grass"] = _build_daily_pollen(
            hourly_raw.get("grass_pollen", []), idx
        )
        pollen["weed"] = _build_daily_pollen(
            hourly_raw.get("ragweed_pollen", []), idx
        )

        return {
            "current": current,
            "hourly": hourly,
            "pollen": pollen,
        }
