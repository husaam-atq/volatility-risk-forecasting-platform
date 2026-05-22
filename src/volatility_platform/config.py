from __future__ import annotations

from pathlib import Path

PACKAGE_DIR = Path(__file__).resolve().parent
ROOT_DIR = PACKAGE_DIR.parents[1]
DATA_DIR = ROOT_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
DATABASE_DIR = ROOT_DIR / "database"
SQL_DIR = ROOT_DIR / "sql"
REPORTS_DIR = ROOT_DIR / "reports"
NOTEBOOKS_DIR = ROOT_DIR / "notebooks"

DATABASE_PATH = DATABASE_DIR / "market_risk.duckdb"
SAMPLE_PRICES_PATH = DATA_DIR / "sample_prices.csv"

DEFAULT_START_DATE = "2015-01-02"
DEFAULT_END_DATE = "2026-05-21"
TRAIN_END = "2019-12-31"
VALIDATION_END = "2021-12-31"
TEST_START = "2022-01-01"

DEFAULT_UNIVERSE = ["SPY", "QQQ", "IWM", "TLT", "GLD", "USO", "AAPL", "MSFT", "NVDA", "JPM"]
VOL_WINDOWS = [5, 10, 21, 63]
TARGET_RV_WINDOW = 21
ANNUALISATION = 252.0
RANDOM_SEED = 20260522
