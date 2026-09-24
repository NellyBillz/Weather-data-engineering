# Weather ETL — a beginner data engineering project

A small, real, end-to-end ETL (Extract → Transform → Load) pipeline that
pulls live weather data for five South African cities (Pretoria, Cape Town,
Bloemfontein, Johannesburg, Durban) and stores it in a local database —
built to teach the core ideas of data engineering rather than to impress
with scale.

> These cities are spread across very different climates — Cape Town's
> Mediterranean coast, Durban's subtropical coast, and the interior
> highveld/central cities — so you should see genuinely different
> temperature and humidity patterns between them, which makes for more
> interesting analysis than nearby suburbs would.

No API key needed. It uses [Open-Meteo](https://open-meteo.com), a free
weather API.

## What you'll learn

- **Extract**: calling a real HTTP API and handling network failures gracefully
- **Transform**: reshaping raw JSON into clean, typed records, with data-quality checks
- **Load**: writing to a database *idempotently* (safe to re-run without duplicating data)
- **Orchestration**: coordinating the three steps and isolating failures so one bad city doesn't kill the whole run
- **Logging**: structured, timestamped logs instead of scattered `print()` calls
- **Testing**: unit tests that don't depend on the network, using fixture data
- **Analysis**: querying your own pipeline's output with pandas and charting it

## Project structure

```
weather_etl/
├── src/
│   ├── config.py      # what cities to track, where the DB lives
│   ├── extract.py      # calls the Open-Meteo API
│   ├── transform.py     # cleans + validates raw data
│   ├── load.py            # writes to SQLite (idempotent upsert)
│   ├── pipeline.py         # orchestrates extract -> transform -> load
│   └── analyze.py           # queries the DB, prints a summary, saves a chart
├── tests/
│   ├── fixtures/sample_response.json   # a saved real API response, for offline tests
│   ├── test_transform.py
│   └── test_load.py
├── data/               # weather.db and charts land here (gitignored)
├── requirements.txt
└── README.md
```

## Setup

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Run it

```bash
# 1. Run the pipeline — fetches live weather and stores it
python src/pipeline.py

# 2. Run the pipeline again — notice it doesn't create duplicate rows
python src/pipeline.py

# 3. Analyze what you've collected
python src/analyze.py
```

Each run appends/updates one row per city. Run it a few times over a day
(or set up a cron job) and you'll start building an actual time series.

## Run the tests

```bash
pytest tests/ -v
```

The tests use a saved sample API response (`tests/fixtures/sample_response.json`)
so they run instantly and don't depend on the network or on the weather
actually cooperating.

## How the pieces fit together

```
extract.py  --raw JSON-->  transform.py  --clean dict-->  load.py  -->  weather.db
                                  ^
                          data-quality checks
                          live here (range checks,
                          type checks, fallbacks)

pipeline.py orchestrates all three, per city, with logging
and per-city error isolation.

analyze.py reads from weather.db independently — it's a
consumer of the pipeline's output, not part of the pipeline.
```

## Ideas to extend this project

Roughly in order of difficulty:

1. **Add more fields** — pull `precipitation`, `pressure`, or hourly forecasts, not just current conditions.
2. **Historical backfill** — Open-Meteo has a historical API; write a script that backfills the last 30 days.
3. **Scheduling** — run `pipeline.py` automatically every hour with `cron` (Linux/Mac) or Task Scheduler (Windows).
4. **Swap SQLite for Postgres** — change only `load.py`; everything else stays the same. This is the point of separating E/T/L.
5. **Add a `dbt`-style transform layer** — instead of transforming in Python, load raw JSON first, then transform with SQL views.
6. **Orchestrate with Airflow or Dagster** — turn `pipeline.py`'s per-city loop into individual tasks with retries and alerting.
7. **Containerize it** — write a `Dockerfile` so the pipeline runs the same way everywhere.
8. **Data quality framework** — replace the hand-written checks in `transform.py` with a library like `great_expectations` or `pandera`.

## Why it's built this way

- **Idempotent loads** (`ON CONFLICT ... DO UPDATE`) — re-running the pipeline is normal in data engineering (retries, backfills, manual triggers). A pipeline that can't handle being re-run safely will eventually corrupt your data.
- **Per-city error isolation** — one city's API hiccup shouldn't take down the whole run. This is a small taste of the fault-tolerance thinking that matters a lot more at scale.
- **Tests use fixtures, not the live API** — network calls in tests make them slow and flaky. Save a real response once, test against that.
- **Extract does no thinking** — it just gets data. All cleaning and validation logic lives in `transform.py`, so you always know where to look for it.
