from __future__ import annotations

from pathlib import Path

import duckdb
import pandas as pd

from volatility_platform.config import DATABASE_PATH


def query_df(sql: str, db_path: str | Path = DATABASE_PATH) -> pd.DataFrame:
    with duckdb.connect(str(db_path), read_only=True) as con:
        return con.execute(sql).fetchdf()


def table_row_counts(db_path: str | Path = DATABASE_PATH) -> pd.DataFrame:
    tables = [
        "asset_universe",
        "raw_prices",
        "clean_prices",
        "daily_returns",
        "realised_volatility",
        "volatility_features",
        "volatility_forecasts",
        "model_metrics",
        "var_estimates",
        "expected_shortfall_estimates",
        "breach_events",
        "var_backtest_results",
        "regime_labels",
        "portfolio_risk",
        "sql_query_benchmarks",
    ]
    with duckdb.connect(str(db_path), read_only=True) as con:
        rows = []
        for table in tables:
            try:
                count = con.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            except duckdb.CatalogException:
                count = 0
            rows.append({"table_name": table, "row_count": count})
    return pd.DataFrame(rows)
