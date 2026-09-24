import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent / "src"))
from load import get_connection, load_records

SAMPLE_RECORD = {
    "city": "Johannesburg",
    "country": "South Africa",
    "observed_at": "2026-09-11T14:00",
    "temperature_c": 21.3,
    "humidity_pct": 34,
    "wind_speed_kmh": 14.2,
    "weather_code": 1,
    "weather_description": "Mainly clear",
    "ingested_at": "2026-09-11T12:00:00+00:00",
}


def test_load_inserts_record(tmp_path):
    db_path = str(tmp_path / "test.db")
    conn = get_connection(db_path)

    load_records(conn, [SAMPLE_RECORD])

    rows = conn.execute("SELECT city, temperature_c FROM weather_observations").fetchall()
    assert rows == [("Johannesburg", 21.3)]
    conn.close()


def test_load_is_idempotent_upsert(tmp_path):
    """Loading the same (city, observed_at) twice should update, not duplicate."""
    db_path = str(tmp_path / "test.db")
    conn = get_connection(db_path)

    load_records(conn, [SAMPLE_RECORD])
    updated = dict(SAMPLE_RECORD, temperature_c=25.0)
    load_records(conn, [updated])

    rows = conn.execute("SELECT temperature_c FROM weather_observations").fetchall()
    assert rows == [(25.0,)]  # updated in place, still only one row
    conn.close()
