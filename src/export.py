"""Export the curated observations for a spreadsheet or dashboard."""
import csv
import sqlite3
from pathlib import Path
from config import DB_PATH


def export_csv(db_path=DB_PATH, output_path='data/weather_export.csv'):
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as conn, destination.open('w', newline='', encoding='utf-8') as file:
        cursor = conn.execute('''
            SELECT city, country, observed_at, temperature_c, humidity_pct,
                   wind_speed_kmh, weather_description
            FROM weather_observations ORDER BY city, observed_at
        ''')
        writer = csv.writer(file)
        writer.writerow([column[0] for column in cursor.description])
        writer.writerows(cursor)
        return cursor.rowcount


if __name__ == '__main__':
    try:
        export_csv()
        print('Saved data/weather_export.csv')
    except sqlite3.OperationalError:
        print('No observations yet. Run python src/pipeline.py --offline first.')
