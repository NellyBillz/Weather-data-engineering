
import json
from pathlib import Path

SAMPLE = Path(__file__).resolve().parents[1] / 'tests' / 'fixtures' / 'sample_response.json'


def fetch_sample_weather(latitude, longitude):
    """Return a fresh copy of the saved API response for any configured city."""
    return json.loads(SAMPLE.read_text(encoding='utf-8'))
