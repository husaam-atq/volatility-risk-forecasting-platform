from __future__ import annotations

import time
from pathlib import Path

import duckdb
import pandas as pd

from volatility_platform.config import DATABASE_PATH, REPORTS_DIR, SQL_DIR
from volatility_platform.data.cleaning import clean_prices, data_quality_checks
from volatility_platform.data.download import download_yfinance_prices
from volatility_platform.data.loaders import ensure_sample_prices
from volatility_platform.data.universe import default_universe
from volatility_platform.database.run_sql import run_sql_directory
from volatility_platform.features.lagged_features import build_volatility_features
from volatility_platform.features.realised_volatility import compute_realised_volatility
from volatility_platform.features.returns import compute_daily_returns


def insert_dataframe(con: duckdb.DuckDBPyConnection, table: str, frame: pd.DataFrame) -> None:
    con.register("_frame", frame)
    con.execute(f"DELETE FROM {table}")
    con.execute(f"INSERT INTO {table} BY NAME SELECT * FROM _frame")
    con.unregister("_frame")


def build_database(
    db_path: str | Path = DATABASE_PATH,
    use_live: bool = False,
    overwrite: bool = True,
) -> dict[str, float | str]:
    started = time.perf_counter()
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    if overwrite and db_path.exists():
        db_path.unlink()

    raw = download_yfinance_prices() if use_live else ensure_sample_prices()
    clean = clean_prices(raw)
    returns = compute_daily_returns(clean)
    realised = compute_realised_volatility(clean)
    features = build_volatility_features(clean)
    quality = data_quality_checks(raw, clean)
    universe = default_universe()

    with duckdb.connect(str(db_path)) as con:
        run_sql_directory(con, SQL_DIR)
        insert_dataframe(con, "asset_universe", universe)
        insert_dataframe(con, "raw_prices", clean)
        insert_dataframe(con, "clean_prices", clean)
        insert_dataframe(con, "daily_returns", returns)
        insert_dataframe(con, "realised_volatility", realised)
        insert_dataframe(con, "volatility_features", features)
        insert_dataframe(con, "data_quality_checks", quality)
        run_sql_directory(con, SQL_DIR)

    elapsed = time.perf_counter() - started
    if db_path.resolve() == DATABASE_PATH.resolve():
        REPORTS_DIR.mkdir(exist_ok=True)
        (REPORTS_DIR / "database_build_time.txt").write_text(f"{elapsed:.6f}\n", encoding="utf-8")
    return {
        "db_path": str(db_path),
        "source": "live" if use_live else "sample",
        "clean_price_rows": float(len(clean)),
        "return_rows": float(len(returns)),
        "realised_vol_rows": float(len(realised)),
        "feature_rows": float(len(features)),
        "elapsed_seconds": elapsed,
    }
