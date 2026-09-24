"""
EXTRACT

Pulls raw data from a source system and hands it back untouched.
The extract step should do as little "thinking" as possible — its only
job is to get bytes from the source into Python, and fail loudly and
clearly if it can't.

We use Open-Meteo (https://open-meteo.com) because it's free, requires
no API key, and is perfect for learning.
"""

import logging

import requests

logger = logging.getLogger(__name__)

BASE_URL = "https://api.open-meteo.com/v1/forecast"
CURRENT_FIELDS = "temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code"


class ExtractError(Exception):
    """Raised when we can't get usable data out of the source system."""


def fetch_current_weather(latitude: float, longitude: float, timeout: int = 10) -> dict:
    """
    Fetch current weather conditions for one location.

    Returns the raw JSON payload as a dict. Deliberately does NOT
    reshape the data — that's the transform step's job.
    """
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": CURRENT_FIELDS,
        "timezone": "auto",
    }

    logger.debug("Requesting weather for (%s, %s)", latitude, longitude)

    try:
        response = requests.get(BASE_URL, params=params, timeout=timeout)
        response.raise_for_status()
    except requests.RequestException as e:
        raise ExtractError(f"Failed to fetch weather data: {e}") from e

    try:
        return response.json()
    except ValueError as e:
        raise ExtractError(f"Source returned invalid JSON: {e}") from e
