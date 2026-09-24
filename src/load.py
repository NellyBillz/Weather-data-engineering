"""
LOAD

Writes clean records to storage. We use SQLite because it needs zero
setup (it's just a file), which keeps the focus on data engineering
concepts rather than database administration. Swapping this for
Postgres later means changing this one file.

Loading is written to be idempotent: running the pipeline twice for
the same city at the same timestamp updates the row instead of
duplicating it. That matters because in the real world, pipelines
get re-run — after failures, backfills, manual triggers — and a
pipeline that can't handle being re-run safely will eventually
duplicate or corrupt your data.
"""

import sqlite3
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS weather_observations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    city TEXT NOT NULL,
    country TEXT NOT NULL,
    observed_at TEXT NOT NULL,
    temperature_c REAL NOT NULL,
    humidity_pct INTEGER NOT NULL,
    wind_speed_kmh REAL NOT NULL,
    weather_code INTEGER NOT NULL,
    weather_description TEXT NOT NULL,
    ingested_at TEXT NOT NULL,
    UNIQUE(city, observed_at)
);
"""

INSERT_SQL = """
INSERT INTO weather_observations
    (city, country, observed_at, temperature_c, humidity_pct, wind_speed_kmh,
     weather_code, weather_description, ingested_at)
VALUES
    (:city, :country, :observed_at, :temperature_c, :humidity_pct, :wind_speed_kmh,
     :weather_code, :weather_description, :ingested_at)
ON CONFLICT(city, observed_at) DO UPDATE SET
    temperature_c        = excluded.temperature_c,
    humidity_pct          = excluded.humidity_pct,
    wind_speed_kmh         = excluded.wind_speed_kmh,
    weather_code            = excluded.weather_code,
    weather_description      = excluded.weather_description,
    ingested_at               = excluded.ingested_at;
"""


def get_connection(db_path: str) -> sqlite3.Connection:
    """Open (and create, if needed) the SQLite database and its schema."""
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.execute(SCHEMA)
    return conn


def load_records(conn: sqlite3.Connection, records: list[dict]) -> int:
    """Insert or update a batch of records. Returns the number processed."""
    with conn:
        conn.executemany(INSERT_SQL, records)
    return len(records)

RUN_SCHEMA = """
CREATE TABLE IF NOT EXISTS pipeline_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    started_at TEXT NOT NULL,
    finished_at TEXT NOT NULL,
    source TEXT NOT NULL,
    succeeded INTEGER NOT NULL,
    failed INTEGER NOT NULL
);
"""


def save_run(conn: sqlite3.Connection, started_at: str, finished_at: str,
             source: str, succeeded: int, failed: int) -> None:
    """Keep a small audit trail of pipeline executions."""
    with conn:
        conn.execute(RUN_SCHEMA)
        conn.execute(
            "INSERT INTO pipeline_runs (started_at, finished_at, source, succeeded, failed) "
            "VALUES (?, ?, ?, ?, ?)",
            (started_at, finished_at, source, succeeded, failed),
        )
