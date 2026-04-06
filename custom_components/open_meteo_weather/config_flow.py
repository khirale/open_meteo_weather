"""Config flow for Open-Meteo Weather integration."""
from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv

from .const import DOMAIN, CONF_LATITUDE, CONF_LONGITUDE, CONF_USE_HOME


class OpenMeteoWeatherConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle the config flow for Open-Meteo Weather."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict | None = None
    ) -> config_entries.FlowResult:
        """Step 1: ask the user whether to use the HA home zone or manual GPS."""
        if user_input is not None:
            if user_input[CONF_USE_HOME]:
                return await self.async_step_home()
            return await self.async_step_manual()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_USE_HOME, default=True): bool,
                }
            ),
        )

    async def async_step_home(
        self, user_input: dict | None = None
    ) -> config_entries.FlowResult:
        """Use the latitude/longitude from the HA home zone."""
        latitude = self.hass.config.latitude
        longitude = self.hass.config.longitude

        await self.async_set_unique_id(f"{DOMAIN}_home")
        self._abort_if_unique_id_configured()

        return self.async_create_entry(
            title="Open-Meteo Weather (Home)",
            data={
                CONF_LATITUDE: latitude,
                CONF_LONGITUDE: longitude,
                CONF_USE_HOME: True,
            },
        )

    async def async_step_manual(
        self, user_input: dict | None = None
    ) -> config_entries.FlowResult:
        """Step 2 (optional): manual GPS coordinates."""
        errors: dict[str, str] = {}

        if user_input is not None:
            lat = user_input[CONF_LATITUDE]
            lon = user_input[CONF_LONGITUDE]

            await self.async_set_unique_id(f"{DOMAIN}_{lat}_{lon}")
            self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title=f"Open-Meteo Weather ({lat}, {lon})",
                data={
                    CONF_LATITUDE: lat,
                    CONF_LONGITUDE: lon,
                    CONF_USE_HOME: False,
                },
            )

        return self.async_show_form(
            step_id="manual",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_LATITUDE): cv.latitude,
                    vol.Required(CONF_LONGITUDE): cv.longitude,
                }
            ),
            errors=errors,
        )
