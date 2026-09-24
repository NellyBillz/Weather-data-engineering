"""Inspect loaded data quality without changing observations."""
import sqlite3
from config import DB_PATH


def report(db_path=DB_PATH):
    with sqlite3.connect(db_path) as conn:
        count, cities, first, last = conn.execute("""
            SELECT COUNT(*), COUNT(DISTINCT city), MIN(observed_at), MAX(observed_at)
            FROM weather_observations
        """).fetchone()
        duplicates = conn.execute("""
            SELECT COUNT(*) FROM (
                SELECT city, observed_at FROM weather_observations
                GROUP BY city, observed_at HAVING COUNT(*) > 1
            )
        """).fetchone()[0]
    return {"observations": count, "cities": cities, "first": first,
            "last": last, "duplicate_keys": duplicates}


if __name__ == '__main__':
    try:
        for name, value in report().items():
            print(f'{name}: {value}')
    except sqlite3.OperationalError:
        print('No observations yet. Run python src/pipeline.py --offline first.')
