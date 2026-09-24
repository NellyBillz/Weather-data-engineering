# Weather Data Engineering

A beginner-friendly pipeline that collects current weather for five South African cities from [Open-Meteo](https://open-meteo.com/). It cleans and checks the API response, saves observations in SQLite, and provides an audit trail, quality report, CSV export, and optional chart.

## Run it on Windows (PowerShell)

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python src/pipeline.py --offline
python src/quality.py
python src/export.py
python -m pytest tests -q
```

`--offline` reads a saved API response, so you can practise without internet. For live weather, run `python src/pipeline.py`. Run it again to see that the same city and observation time update one row instead of creating duplicates. The offline fixture gives every city the same weather values; use the live command to compare real cities.

For a chart and city summary, run `python src/analyze.py` after collecting observations. Output files go in `data/`: `weather.db`, `weather_export.csv`, and `temperature_by_city.png`. They are ignored by Git.

## How the pipeline works

1. **Extract** (`src/extract.py` or `src/sample.py`): get the raw response.
2. **Transform** (`src/transform.py`): select fields, assign types, and reject suspicious values.
3. **Load** (`src/load.py`): save by city and observation time using a SQLite upsert.
4. **Orchestrate** (`src/pipeline.py`): process each city independently and record a run summary in `pipeline_runs`.
5. **Consume** (`src/quality.py`, `src/export.py`, `src/analyze.py`): inspect and use the stored data.

A scheduled job can call `python src/pipeline.py` periodically. The GitHub Actions workflow runs the offline version on each push, without relying on a live API. A run returns a nonzero exit status only if every city fails; inspect the `failed` count or `pipeline_runs` table to detect partial failures.

## Push these commits

From the repository folder:

```powershell
git log --oneline -10
git status
git push -u origin main
```

The included history contains ten small commits. The Git remote is configured as `https://github.com/NellyBillz/Weather-data-engineering.git`.
