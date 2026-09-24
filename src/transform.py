"""
TRANSFORM

Takes raw, source-shaped data and turns it into clean, analysis-ready
records. This is also where basic data-quality checks belong — catching
bad data here is far cheaper than catching it after it's in your
warehouse and someone's dashboard is showing a -900C reading.
"""

import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

# WMO weather codes -> human-readable description.
# https://open-meteo.com/en/docs (see "WMO Weather interpretation codes")
WEATHER_CODES = {
    0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Fog", 48: "Depositing rime fog",
    51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
    61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
    71: "Slight snow", 73: "Moderate snow", 75: "Heavy snow",
    80: "Slight rain showers", 81: "Moderate rain showers", 82: "Violent rain showers",
    95: "Thunderstorm",
}


class TransformError(Exception):
    """Raised when a record can't be cleaned/validated into a usable shape."""


def transform_weather(raw: dict, city_name: str, country: str) -> dict:
    """
    Turn one raw Open-Meteo response into a flat, typed record ready
    for loading.
    """
    try:
        current = raw["current"]
        record = {
            "city": city_name,
            "country": country,
            "observed_at": current["time"],
            "temperature_c": round(float(current["temperature_2m"]), 1),
            "humidity_pct": int(current["relative_humidity_2m"]),
            "wind_speed_kmh": round(float(current["wind_speed_10m"]), 1),
            "weather_code": int(current["weather_code"]),
            "weather_description": WEATHER_CODES.get(int(current["weather_code"]), "Unknown"),
            "ingested_at": datetime.now(timezone.utc).isoformat(),
        }
    except (KeyError, TypeError, ValueError) as e:
        raise TransformError(f"Malformed weather payload for {city_name}: {e}") from e

    # --- basic data-quality checks ---
    # Real pipelines validate ranges, not just types. This is the kind
    # of check that would have caught many real-world sensor glitches.
    if not (-90 <= record["temperature_c"] <= 60):
        raise TransformError(f"Suspicious temperature for {city_name}: {record['temperature_c']}°C")
    if not (0 <= record["humidity_pct"] <= 100):
        raise TransformError(f"Suspicious humidity for {city_name}: {record['humidity_pct']}%")

    if record["wind_speed_kmh"] < 0 or record["wind_speed_kmh"] > 400:
        raise TransformError(f"Suspicious wind speed for {city_name}")
    if not (0 <= record["weather_code"] <= 99):
        raise TransformError(f"Suspicious weather code for {city_name}")

    return record
