"""Sensor platform for Open-Meteo Weather integration."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    UnitOfPressure,
    UnitOfSpeed,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    SENSOR_AQI,
    SENSOR_CARBON_MONOXIDE,
    SENSOR_CONDITION,
    SENSOR_SUNRISE,
    SENSOR_SUNSET,
    SENSOR_DAILY_CONDITION,
    SENSOR_DAILY_PRECIPITATION,
    SENSOR_DAILY_TEMPERATURE_MAX,
    SENSOR_DAILY_TEMPERATURE_MIN,
    SENSOR_DAILY_UV_INDEX_MAX,
    SENSOR_DAILY_WIND_SPEED_MAX,
    SENSOR_FEELS_LIKE,
    SENSOR_HOURLY_CONDITION,
    SENSOR_HOURLY_PRECIPITATION_PROBABILITY,
    SENSOR_HOURLY_TEMPERATURE,
    SENSOR_HOURLY_UV_INDEX,
    SENSOR_HOURLY_WIND_DIRECTION,
    SENSOR_HOURLY_WIND_SPEED,
    SENSOR_HUMIDITY,
    SENSOR_NITROGEN_DIOXIDE,
    SENSOR_OZONE,
    SENSOR_PM10,
    SENSOR_PM25,
    SENSOR_POLLEN_GRASS,
    SENSOR_POLLEN_TREE,
    SENSOR_POLLEN_WEED,
    SENSOR_PRECIPITATION,
    SENSOR_PRESSURE,
    SENSOR_SOLAR_RADIATION,
    SENSOR_SULPHUR_DIOXIDE,
    SENSOR_TEMPERATURE,
    SENSOR_UV_INDEX,
    SENSOR_WIND_DIRECTION,
    SENSOR_WIND_GUST,
    SENSOR_WIND_SPEED,
    get_aqi_category,
)
from .coordinator_air_quality import AirQualityCoordinator
from .coordinator_location import LocationCoordinator
from .coordinator_weather import WeatherCoordinator

SENSOR_LOCATION = "location"

@dataclass
class OpenMeteoSensorDescription(SensorEntityDescription):
    """Extends SensorEntityDescription with value/attributes callables."""

    value_fn: Callable[[dict], Any] = field(default=lambda d: None)
    attributes_fn: Callable[[dict], dict] = field(default=lambda d: {})

WEATHER_SENSORS: tuple[OpenMeteoSensorDescription, ...] = (
    OpenMeteoSensorDescription(
        key=SENSOR_TEMPERATURE,
        name="Température",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d["current"].get("temperature_2m"),
    ),
    OpenMeteoSensorDescription(
        key=SENSOR_FEELS_LIKE,
        name="Ressenti",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d["current"].get("apparent_temperature"),
    ),
    OpenMeteoSensorDescription(
        key=SENSOR_HUMIDITY,
        name="Humidité",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.HUMIDITY,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d["current"].get("relative_humidity_2m"),
    ),
    OpenMeteoSensorDescription(
        key=SENSOR_PRECIPITATION,
        name="Précipitations",
        native_unit_of_measurement="mm",
        device_class=SensorDeviceClass.PRECIPITATION,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d["current"].get("precipitation"),
    ),
    OpenMeteoSensorDescription(
        key=SENSOR_WIND_SPEED,
        name="Vitesse du vent",
        native_unit_of_measurement=UnitOfSpeed.KILOMETERS_PER_HOUR,
        device_class=SensorDeviceClass.WIND_SPEED,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d["current"].get("wind_speed_10m"),
    ),
    OpenMeteoSensorDescription(
        key=SENSOR_WIND_DIRECTION,
        name="Direction du vent",
        native_unit_of_measurement="°",
        icon="mdi:compass",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d["current"].get("wind_direction_10m"),
    ),
    OpenMeteoSensorDescription(
        key=SENSOR_WIND_GUST,
        name="Rafales",
        native_unit_of_measurement=UnitOfSpeed.KILOMETERS_PER_HOUR,
        device_class=SensorDeviceClass.WIND_SPEED,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d["current"].get("wind_gusts_10m"),
    ),
    OpenMeteoSensorDescription(
        key=SENSOR_PRESSURE,
        name="Pression",
        native_unit_of_measurement=UnitOfPressure.HPA,
        device_class=SensorDeviceClass.ATMOSPHERIC_PRESSURE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d["current"].get("surface_pressure"),
    ),
    OpenMeteoSensorDescription(
        key=SENSOR_UV_INDEX,
        name="Indice UV",
        native_unit_of_measurement="UV index",
        icon="mdi:sun-wireless",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d["current"].get("uv_index"),
    ),
    OpenMeteoSensorDescription(
        key=SENSOR_SOLAR_RADIATION,
        name="Rayonnement solaire",
        native_unit_of_measurement="W/m²",
        device_class=SensorDeviceClass.IRRADIANCE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d["current"].get("shortwave_radiation"),
    ),
    OpenMeteoSensorDescription(
        key=SENSOR_CONDITION,
        name="Condition météo",
        icon="mdi:weather-cloudy",
        value_fn=lambda d: d["hourly"].get("condition", {}).get("h0"),
    ),
    OpenMeteoSensorDescription(
        key=SENSOR_SUNRISE,
        name="Lever du soleil",
        icon="mdi:weather-sunset-up",
        value_fn=lambda d: d["daily"].get("sunrise", {}).get("j0", "").split("T")[-1][:5] if d["daily"].get("sunrise", {}).get("j0") else None,
        attributes_fn=lambda d: {
            k: v.split("T")[-1][:5] if v else None
            for k, v in d["daily"].get("sunrise", {}).items()
        },
    ),
    OpenMeteoSensorDescription(
        key=SENSOR_SUNSET,
        name="Coucher du soleil",
        icon="mdi:weather-sunset-down",
        value_fn=lambda d: d["daily"].get("sunset", {}).get("j0", "").split("T")[-1][:5] if d["daily"].get("sunset", {}).get("j0") else None,
        attributes_fn=lambda d: {
            k: v.split("T")[-1][:5] if v else None
            for k, v in d["daily"].get("sunset", {}).items()
        },
    ),

    OpenMeteoSensorDescription(
        key=SENSOR_HOURLY_TEMPERATURE,
        name="Température horaire",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:thermometer",
        value_fn=lambda d: d["hourly"].get("temperature_2m", {}).get("h0"),
        attributes_fn=lambda d: d["hourly"].get("temperature_2m", {}),
    ),
    OpenMeteoSensorDescription(
        key=SENSOR_HOURLY_PRECIPITATION_PROBABILITY,
        name="Probabilité précipitations horaire",
        native_unit_of_measurement=PERCENTAGE,
        icon="mdi:weather-rainy",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d["hourly"].get("precipitation_probability", {}).get("h0"),
        attributes_fn=lambda d: d["hourly"].get("precipitation_probability", {}),
    ),
    OpenMeteoSensorDescription(
        key=SENSOR_HOURLY_WIND_SPEED,
        name="Vitesse vent horaire",
        native_unit_of_measurement=UnitOfSpeed.KILOMETERS_PER_HOUR,
        device_class=SensorDeviceClass.WIND_SPEED,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d["hourly"].get("wind_speed_10m", {}).get("h0"),
        attributes_fn=lambda d: d["hourly"].get("wind_speed_10m", {}),
    ),
    OpenMeteoSensorDescription(
        key=SENSOR_HOURLY_WIND_DIRECTION,
        name="Direction vent horaire",
        native_unit_of_measurement="°",
        icon="mdi:compass",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d["hourly"].get("wind_direction_10m", {}).get("h0"),
        attributes_fn=lambda d: d["hourly"].get("wind_direction_10m", {}),
    ),
    OpenMeteoSensorDescription(
        key=SENSOR_HOURLY_UV_INDEX,
        name="Indice UV horaire",
        native_unit_of_measurement="UV index",
        icon="mdi:sun-wireless",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d["hourly"].get("uv_index", {}).get("h0"),
        attributes_fn=lambda d: d["hourly"].get("uv_index", {}),
    ),
    OpenMeteoSensorDescription(
        key=SENSOR_HOURLY_CONDITION,
        name="Condition météo horaire",
        icon="mdi:weather-cloudy",
        value_fn=lambda d: d["hourly"].get("condition", {}).get("h0"),
        attributes_fn=lambda d: d["hourly"].get("condition", {}),
    ),

    OpenMeteoSensorDescription(
        key=SENSOR_DAILY_TEMPERATURE_MAX,
        name="Température max journalière",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        icon="mdi:thermometer-chevron-up",
        value_fn=lambda d: d["daily"].get("temperature_2m_max", {}).get("j0"),
        attributes_fn=lambda d: d["daily"].get("temperature_2m_max", {}),
    ),
    OpenMeteoSensorDescription(
        key=SENSOR_DAILY_TEMPERATURE_MIN,
        name="Température min journalière",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        icon="mdi:thermometer-chevron-down",
        value_fn=lambda d: d["daily"].get("temperature_2m_min", {}).get("j0"),
        attributes_fn=lambda d: d["daily"].get("temperature_2m_min", {}),
    ),
    OpenMeteoSensorDescription(
        key=SENSOR_DAILY_PRECIPITATION,
        name="Précipitations journalières",
        native_unit_of_measurement="mm",
        device_class=SensorDeviceClass.PRECIPITATION,
        icon="mdi:weather-rainy",
        value_fn=lambda d: d["daily"].get("precipitation_sum", {}).get("j0"),
        attributes_fn=lambda d: d["daily"].get("precipitation_sum", {}),
    ),
    OpenMeteoSensorDescription(
        key=SENSOR_DAILY_CONDITION,
        name="Condition météo journalière",
        icon="mdi:weather-cloudy",
        value_fn=lambda d: d["daily"].get("condition", {}).get("j0"),
        attributes_fn=lambda d: d["daily"].get("condition", {}),
    ),
    OpenMeteoSensorDescription(
        key=SENSOR_DAILY_UV_INDEX_MAX,
        name="Indice UV max journalier",
        native_unit_of_measurement="UV index",
        icon="mdi:sun-wireless",
        value_fn=lambda d: d["daily"].get("uv_index_max", {}).get("j0"),
        attributes_fn=lambda d: d["daily"].get("uv_index_max", {}),
    ),
    OpenMeteoSensorDescription(
        key=SENSOR_DAILY_WIND_SPEED_MAX,
        name="Vitesse vent max journalière",
        native_unit_of_measurement=UnitOfSpeed.KILOMETERS_PER_HOUR,
        device_class=SensorDeviceClass.WIND_SPEED,
        value_fn=lambda d: d["daily"].get("wind_speed_10m_max", {}).get("j0"),
        attributes_fn=lambda d: d["daily"].get("wind_speed_10m_max", {}),
    ),
)

AIR_QUALITY_SENSORS: tuple[OpenMeteoSensorDescription, ...] = (
    OpenMeteoSensorDescription(
        key=SENSOR_AQI,
        name="Indice qualité air",
        native_unit_of_measurement="AQI",
        icon="mdi:air-filter",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d["current"].get("european_aqi"),
        attributes_fn=lambda d: {
            **d["hourly"].get("european_aqi", {}),
            "category": get_aqi_category(d["current"].get("european_aqi")),
        },
    ),
    OpenMeteoSensorDescription(
        key=SENSOR_PM25,
        name="PM2.5",
        native_unit_of_measurement="µg/m³",
        device_class=SensorDeviceClass.PM25,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d["current"].get("pm2_5"),
        attributes_fn=lambda d: d["hourly"].get("pm2_5", {}),
    ),
    OpenMeteoSensorDescription(
        key=SENSOR_PM10,
        name="PM10",
        native_unit_of_measurement="µg/m³",
        device_class=SensorDeviceClass.PM10,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d["current"].get("pm10"),
        attributes_fn=lambda d: d["hourly"].get("pm10", {}),
    ),
    OpenMeteoSensorDescription(
        key=SENSOR_OZONE,
        name="Ozone",
        native_unit_of_measurement="µg/m³",
        device_class=SensorDeviceClass.OZONE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d["current"].get("ozone"),
        attributes_fn=lambda d: d["hourly"].get("ozone", {}),
    ),
    OpenMeteoSensorDescription(
        key=SENSOR_NITROGEN_DIOXIDE,
        name="Dioxyde d'azote",
        native_unit_of_measurement="µg/m³",
        device_class=SensorDeviceClass.NITROGEN_DIOXIDE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d["current"].get("nitrogen_dioxide"),
        attributes_fn=lambda d: d["hourly"].get("nitrogen_dioxide", {}),
    ),
    OpenMeteoSensorDescription(
        key=SENSOR_SULPHUR_DIOXIDE,
        name="Dioxyde de soufre",
        native_unit_of_measurement="µg/m³",
        device_class=SensorDeviceClass.SULPHUR_DIOXIDE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d["current"].get("sulphur_dioxide"),
        attributes_fn=lambda d: d["hourly"].get("sulphur_dioxide", {}),
    ),
    OpenMeteoSensorDescription(
        key=SENSOR_CARBON_MONOXIDE,
        name="Monoxyde de carbone",
        native_unit_of_measurement="µg/m³",
        device_class=SensorDeviceClass.CO,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d["current"].get("carbon_monoxide"),
        attributes_fn=lambda d: d["hourly"].get("carbon_monoxide", {}),
    ),
    OpenMeteoSensorDescription(
        key=SENSOR_POLLEN_TREE,
        name="Pollen arbres",
        native_unit_of_measurement="µg/m³",
        icon="mdi:tree",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d["pollen"].get("tree", {}).get("j0"),
        attributes_fn=lambda d: d["pollen"].get("tree", {}),
    ),
    OpenMeteoSensorDescription(
        key=SENSOR_POLLEN_GRASS,
        name="Pollen herbes",
        native_unit_of_measurement="µg/m³",
        icon="mdi:grass",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d["pollen"].get("grass", {}).get("j0"),
        attributes_fn=lambda d: d["pollen"].get("grass", {}),
    ),
    OpenMeteoSensorDescription(
        key=SENSOR_POLLEN_WEED,
        name="Pollen graminées",
        native_unit_of_measurement="µg/m³",
        icon="mdi:sprout",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d["pollen"].get("weed", {}).get("j0"),
        attributes_fn=lambda d: d["pollen"].get("weed", {}),
    ),
)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinators = hass.data[DOMAIN][entry.entry_id]
    location_coordinator: LocationCoordinator = coordinators["location"]
    weather_coordinator: WeatherCoordinator = coordinators["weather"]
    aq_coordinator: AirQualityCoordinator = coordinators["air_quality"]

    city = location_coordinator.data.get("city", "Unknown") if location_coordinator.data else "Unknown"

    entities: list[SensorEntity] = []

    entities.append(
        OpenMeteoLocationSensor(location_coordinator, entry, city)
    )

    for description in WEATHER_SENSORS:
        entities.append(
            OpenMeteoWeatherSensor(weather_coordinator, description, entry, city)
        )

    for description in AIR_QUALITY_SENSORS:
        entities.append(
            OpenMeteoAirQualitySensor(aq_coordinator, description, entry, city)
        )

    async_add_entities(entities)

def _build_device_info(entry: ConfigEntry, city: str) -> DeviceInfo:
    """Build shared DeviceInfo for all sensors."""
    return DeviceInfo(
        identifiers={(DOMAIN, entry.entry_id)},
        name="Open-Meteo Weather",
        manufacturer="Open-Meteo",
        model=city,
        entry_type=DeviceEntryType.SERVICE,
    )

class OpenMeteoLocationSensor(CoordinatorEntity, SensorEntity):
    """Sensor exposing the resolved city name and GPS coordinates."""

    def __init__(
        self,
        coordinator: LocationCoordinator,
        entry: ConfigEntry,
        city: str,
    ) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_{SENSOR_LOCATION}"
        self._attr_name = "Location"
        self._attr_icon = "mdi:map-marker"
        self._attr_device_info = _build_device_info(entry, city)

    @property
    def native_value(self) -> str | None:
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get("city")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        if self.coordinator.data is None:
            return {}
        data = self.coordinator.data
        return {
            "latitude": data.get("latitude"),
            "longitude": data.get("longitude"),
            "country": data.get("country"),
            "country_code": data.get("country_code"),
            "postcode": data.get("postcode"),
            "state": data.get("state"),
        }


class _OpenMeteoBaseSensor(CoordinatorEntity, SensorEntity):
    """Base class for weather and air quality sensors."""

    entity_description: OpenMeteoSensorDescription

    def __init__(
        self,
        coordinator: CoordinatorEntity,
        description: OpenMeteoSensorDescription,
        entry: ConfigEntry,
        city: str,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_device_info = _build_device_info(entry, city)

    @property
    def native_value(self) -> Any:
        if self.coordinator.data is None:
            return None
        return self.entity_description.value_fn(self.coordinator.data)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        if self.coordinator.data is None:
            return {}
        return self.entity_description.attributes_fn(self.coordinator.data)


class OpenMeteoWeatherSensor(_OpenMeteoBaseSensor):
    """Sensor backed by the Weather coordinator."""


class OpenMeteoAirQualitySensor(_OpenMeteoBaseSensor):
    """Sensor backed by the Air Quality coordinator."""
