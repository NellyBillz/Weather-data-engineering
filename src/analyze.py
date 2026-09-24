"""
ANALYZE

A small "consumption layer" on top of the data the pipeline collected.
Not part of the ETL pipeline itself — this is what a downstream
analyst or dashboard would do with the data once it's loaded.

Usage:
    python src/analyze.py
"""

import sqlite3
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # render without a display, needed for headless/servers
import matplotlib.pyplot as plt
import pandas as pd

sys.path.append(str(Path(__file__).parent))
from config import DB_PATH


def load_dataframe(db_path: str = DB_PATH) -> pd.DataFrame:
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query("SELECT * FROM weather_observations ORDER BY observed_at", conn)
    conn.close()
    return df


def summarize(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("city")
        .agg(
            avg_temp_c=("temperature_c", "mean"),
            min_temp_c=("temperature_c", "min"),
            max_temp_c=("temperature_c", "max"),
            avg_humidity_pct=("humidity_pct", "mean"),
            observations=("id", "count"),
        )
        .round(1)
        .sort_values("avg_temp_c", ascending=False)
    )


def plot_temperatures(df: pd.DataFrame, output_path: str = "data/temperature_by_city.png") -> None:
    latest = df.sort_values("observed_at").groupby("city").tail(1)
    fig, ax = plt.subplots(figsize=(8, 5))
    latest.sort_values("temperature_c").plot.barh(
        x="city", y="temperature_c", ax=ax, legend=False, color="#4C72B0"
    )
    ax.set_xlabel("Temperature (°C)")
    ax.set_ylabel("")
    ax.set_title("Current Temperature by City")
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    df = load_dataframe()
    if df.empty:
        print("No data yet — run `python src/pipeline.py` first.")
    else:
        print(summarize(df))
        plot_temperatures(df)
        print("\nSaved chart to data/temperature_by_city.png")
