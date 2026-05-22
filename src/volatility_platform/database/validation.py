from __future__ import annotations

from pathlib import Path

import duckdb
import pandas as pd

from volatility_platform.config import DATABASE_PATH

VALIDATION_VIEWS = [
    "v_validation_duplicate_prices",
    "v_validation_non_positive_prices",
    "v_validation_forecast_leakage",
    "v_validation_negative_forecasts",
]


def run_validation_queries(db_path: str | Path = DATABASE_PATH) -> pd.DataFrame:
    rows = []
    with duckdb.connect(str(db_path), read_only=True) as con:
        for view in VALIDATION_VIEWS:
            count = con.execute(f"SELECT COUNT(*) FROM {view}").fetchone()[0]
            rows.append(
                {
                    "validation_query": view,
                    "failing_rows": count,
                    "status": "pass" if count == 0 else "fail",
                }
            )
    return pd.DataFrame(rows)
