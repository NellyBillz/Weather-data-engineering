"""
PIPELINE

The orchestrator. Its job is *coordination*, not logic — it calls
extract, then transform, then load, for each city, and makes sure one
city's failure doesn't take down the whole run. This is the file you
run directly.

Usage:
    python src/pipeline.py
"""

import logging
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from config import CITIES, DB_PATH
from extract import ExtractError, fetch_current_weather
from load import get_connection, load_records
from transform import TransformError, transform_weather

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("pipeline")


def run() -> dict:
    logger.info("Starting weather ETL pipeline for %d cities", len(CITIES))
    conn = get_connection(DB_PATH)
    succeeded, failed = 0, 0

    for city in CITIES:
        try:
            raw = fetch_current_weather(city["lat"], city["lon"])
            record = transform_weather(raw, city["name"], city["country"])
            load_records(conn, [record])
            logger.info(
                "Loaded %-14s %5.1f°C  %s",
                city["name"], record["temperature_c"], record["weather_description"],
            )
            succeeded += 1
        except ExtractError as e:
            logger.error("Extract failed for %s: %s", city["name"], e)
            failed += 1
        except TransformError as e:
            logger.error("Transform failed for %s: %s", city["name"], e)
            failed += 1
        except Exception:
            # Catch-all so one unexpected bug doesn't kill the whole run.
            # In production you'd also alert someone here.
            logger.exception("Unexpected error while processing %s", city["name"])
            failed += 1

    conn.close()
    logger.info("Pipeline finished. Succeeded: %d, Failed: %d", succeeded, failed)
    return {"succeeded": succeeded, "failed": failed}


if __name__ == "__main__":
    result = run()
    # Non-zero exit code if nothing succeeded, useful for cron/CI alerting.
    sys.exit(0 if result["succeeded"] > 0 else 1)
