import json
import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).parent.parent / "src"))
from transform import TransformError, transform_weather

FIXTURE = Path(__file__).parent / "fixtures" / "sample_response.json"


@pytest.fixture
def sample_raw():
    return json.loads(FIXTURE.read_text())


def test_transform_happy_path(sample_raw):
    record = transform_weather(sample_raw, "Johannesburg", "South Africa")

    assert record["city"] == "Johannesburg"
    assert record["temperature_c"] == 21.3
    assert record["humidity_pct"] == 34
    assert record["weather_description"] == "Mainly clear"
    assert "ingested_at" in record


def test_transform_rejects_missing_field(sample_raw):
    del sample_raw["current"]["temperature_2m"]
    with pytest.raises(TransformError):
        transform_weather(sample_raw, "Johannesburg", "South Africa")


def test_transform_rejects_impossible_temperature(sample_raw):
    sample_raw["current"]["temperature_2m"] = 999
    with pytest.raises(TransformError):
        transform_weather(sample_raw, "Johannesburg", "South Africa")


def test_transform_unknown_weather_code_falls_back(sample_raw):
    sample_raw["current"]["weather_code"] = 12345
    record = transform_weather(sample_raw, "Johannesburg", "South Africa")
    assert record["weather_description"] == "Unknown"
