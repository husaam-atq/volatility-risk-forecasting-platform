from __future__ import annotations

from pathlib import Path

import duckdb

from volatility_platform.config import DATABASE_PATH


def connect(
    db_path: str | Path = DATABASE_PATH, read_only: bool = False
) -> duckdb.DuckDBPyConnection:
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    return duckdb.connect(str(path), read_only=read_only)
