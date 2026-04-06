"""Constants for Open-Meteo Weather integration."""

DOMAIN = "open_meteo_weather"

CONF_LATITUDE = "latitude"
CONF_LONGITUDE = "longitude"
CONF_USE_HOME = "use_home"

FORECAST_API_URL = "https://api.open-meteo.com/v1/forecast"
AIR_QUALITY_API_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"

UPDATE_INTERVAL_HOURS = 1

FORECAST_DAYS = 7

HOURLY_HOURS = 24

WMO_CODES: dict[int, str] = {
    0:  "clear_sky",
    1:  "mainly_clear",
    2:  "partly_cloudy",
    3:  "overcast",
    45: "fog",
    48: "icy_fog",
    51: "light_drizzle",
    53: "moderate_drizzle",
    55: "heavy_drizzle",
    56: "light_freezing_drizzle",
    57: "heavy_freezing_drizzle",
    61: "light_rain",
    63: "moderate_rain",
    65: "heavy_rain",
    66: "light_freezing_rain",
    67: "heavy_freezing_rain",
    71: "light_snow",
    73: "moderate_snow",
    75: "heavy_snow",
    77: "snow_grains",
    80: "light_showers",
    81: "moderate_showers",
    82: "heavy_showers",
    85: "light_snow_showers",
    86: "heavy_snow_showers",
    95: "thunderstorm",
    96: "thunderstorm_light_hail",
    99: "thunderstorm_heavy_hail",
}

WMO_LABELS_FR: dict[str, str] = {
    "clear_sky":                "Ciel dégagé",
    "mainly_clear":             "Principalement dégagé",
    "partly_cloudy":            "Partiellement nuageux",
    "overcast":                 "Couvert",
    "fog":                      "Brouillard",
    "icy_fog":                  "Brouillard givrant",
    "light_drizzle":            "Bruine légère",
    "moderate_drizzle":         "Bruine modérée",
    "heavy_drizzle":            "Bruine forte",
    "light_freezing_drizzle":   "Bruine verglaçante légère",
    "heavy_freezing_drizzle":   "Bruine verglaçante forte",
    "light_rain":               "Pluie légère",
    "moderate_rain":            "Pluie modérée",
    "heavy_rain":               "Pluie forte",
    "light_freezing_rain":      "Pluie verglaçante légère",
    "heavy_freezing_rain":      "Pluie verglaçante forte",
    "light_snow":               "Neige légère",
    "moderate_snow":            "Neige modérée",
    "heavy_snow":               "Neige forte",
    "snow_grains":              "Grésil",
    "light_showers":            "Averses légères",
    "moderate_showers":         "Averses modérées",
    "heavy_showers":            "Averses fortes",
    "light_snow_showers":       "Averses de neige légères",
    "heavy_snow_showers":       "Averses de neige fortes",
    "thunderstorm":             "Orage",
    "thunderstorm_light_hail":  "Orage avec grêle légère",
    "thunderstorm_heavy_hail":  "Orage avec grêle forte",
    "unknown":                  "Inconnu",
}


def wmo_to_fr(key: str) -> str:
    """Return the French label for a WMO condition key."""
    return WMO_LABELS_FR.get(key, key)

AQI_CATEGORIES: dict[str, tuple[int, int]] = {
    "good":      (0,   20),
    "fair":      (21,  40),
    "moderate":  (41,  60),
    "poor":      (61,  80),
    "very_poor": (81,  100),
    "extremely_poor": (101, 500),
}


def get_aqi_category(value: float | None) -> str:
    """Return AQI category string from numeric value."""
    if value is None:
        return "unknown"
    for category, (low, high) in AQI_CATEGORIES.items():
        if low <= value <= high:
            return category
    return "extremely_poor"

SENSOR_TEMPERATURE             = "temperature"
SENSOR_FEELS_LIKE              = "feels_like"
SENSOR_HUMIDITY                = "humidity"
SENSOR_PRECIPITATION           = "precipitation"
SENSOR_WIND_SPEED              = "wind_speed"
SENSOR_WIND_DIRECTION          = "wind_direction"
SENSOR_WIND_GUST               = "wind_gust"
SENSOR_PRESSURE                = "pressure"
SENSOR_UV_INDEX                = "uv_index"
SENSOR_SOLAR_RADIATION         = "solar_radiation"
SENSOR_CONDITION               = "condition"

SENSOR_HOURLY_TEMPERATURE              = "hourly_temperature"
SENSOR_HOURLY_PRECIPITATION_PROBABILITY = "hourly_precipitation_probability"
SENSOR_HOURLY_WIND_SPEED               = "hourly_wind_speed"
SENSOR_HOURLY_WIND_DIRECTION           = "hourly_wind_direction"
SENSOR_HOURLY_UV_INDEX                 = "hourly_uv_index"
SENSOR_HOURLY_CONDITION                = "hourly_condition"

SENSOR_DAILY_TEMPERATURE_MAX   = "daily_temperature_max"
SENSOR_DAILY_TEMPERATURE_MIN   = "daily_temperature_min"
SENSOR_DAILY_PRECIPITATION     = "daily_precipitation"
SENSOR_DAILY_CONDITION         = "daily_condition"
SENSOR_DAILY_UV_INDEX_MAX      = "daily_uv_index_max"
SENSOR_DAILY_WIND_SPEED_MAX    = "daily_wind_speed_max"

SENSOR_AQI                     = "aqi"
SENSOR_PM25                    = "pm25"
SENSOR_PM10                    = "pm10"
SENSOR_OZONE                   = "ozone"
SENSOR_NITROGEN_DIOXIDE        = "nitrogen_dioxide"
SENSOR_SULPHUR_DIOXIDE         = "sulphur_dioxide"
SENSOR_CARBON_MONOXIDE         = "carbon_monoxide"

SENSOR_POLLEN_TREE             = "pollen_tree"
SENSOR_POLLEN_GRASS            = "pollen_grass"
SENSOR_POLLEN_WEED             = "pollen_weed"
