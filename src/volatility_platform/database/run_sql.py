from __future__ import annotations

from pathlib import Path

import duckdb

from volatility_platform.config import SQL_DIR


def run_sql_file(con: duckdb.DuckDBPyConnection, path: str | Path) -> None:
    sql = Path(path).read_text(encoding="utf-8")
    con.execute(sql)


def run_sql_directory(con: duckdb.DuckDBPyConnection, sql_dir: str | Path = SQL_DIR) -> None:
    for path in sorted(Path(sql_dir).glob("*.sql")):
        run_sql_file(con, path)
