"""
Central configuration for the pipeline.

Keeping config separate from logic means you can change *what* the
pipeline does (which cities, where data lands) without touching *how*
it does it (extract/transform/load code).
"""

CITIES = [
    {"name": "Pretoria", "country": "South Africa", "lat": -25.7479, "lon": 28.2293},
    {"name": "Cape Town", "country": "South Africa", "lat": -33.9249, "lon": 18.4241},
    {"name": "Bloemfontein", "country": "South Africa", "lat": -29.0852, "lon": 26.1596},
    {"name": "Johannesburg", "country": "South Africa", "lat": -26.2041, "lon": 28.0473},
    {"name": "Durban", "country": "South Africa", "lat": -29.8587, "lon": 31.0218},
]

DB_PATH = "data/weather.db"
