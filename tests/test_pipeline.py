"""Offline integration checks: extraction, transformation, loading, and auditing."""
import sqlite3
from pathlib import Path
from unittest.mock import patch
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import pipeline
from export import export_csv
from quality import report


def test_offline_pipeline_can_be_repeated(tmp_path):
    database = tmp_path / 'weather.db'
    with patch.object(pipeline, 'DB_PATH', str(database)):
        assert pipeline.run(offline=True) == {'succeeded': 5, 'failed': 0}
        assert pipeline.run(offline=True) == {'succeeded': 5, 'failed': 0}
    assert report(str(database))['observations'] == 5
    assert report(str(database))['duplicate_keys'] == 0
    with sqlite3.connect(database) as conn:
        assert conn.execute('SELECT COUNT(*) FROM pipeline_runs').fetchone()[0] == 2
    output = tmp_path / 'export.csv'
    export_csv(str(database), output)
    assert len(output.read_text().splitlines()) == 6
