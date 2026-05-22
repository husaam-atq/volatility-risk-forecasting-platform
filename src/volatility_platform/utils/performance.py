from __future__ import annotations

import time
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd

from volatility_platform.config import DATABASE_PATH, REPORTS_DIR, SQL_DIR
from volatility_platform.database.queries import table_row_counts

DASHBOARD_QUERIES = {
    "dashboard_overview": "SELECT * FROM v_dashboard_overview",
    "model_comparison": "SELECT * FROM v_model_rank_summary",
    "var_breach_summary": "SELECT * FROM v_var_breach_summary",
    "asset_risk_summary": "SELECT * FROM v_asset_risk_summary",
    "portfolio_risk_summary": "SELECT * FROM v_portfolio_risk_summary",
}


def benchmark_query(
    con: duckdb.DuckDBPyConnection, sql: str, repeats: int = 10
) -> dict[str, float]:
    timings = []
    row_count = 0
    for _ in range(repeats):
        start = time.perf_counter()
        result = con.execute(sql).fetchall()
        timings.append((time.perf_counter() - start) * 1000.0)
        row_count = len(result)
    values = np.array(timings)
    return {
        "row_count": float(row_count),
        "mean_ms": float(values.mean()),
        "p50_ms": float(np.percentile(values, 50)),
        "p95_ms": float(np.percentile(values, 95)),
        "min_ms": float(values.min()),
        "max_ms": float(values.max()),
    }


def run_sql_benchmarks(db_path: str | Path = DATABASE_PATH) -> pd.DataFrame:
    rows = []
    total_rows = int(table_row_counts(db_path)["row_count"].sum())
    with duckdb.connect(str(db_path)) as con:
        for name, sql in DASHBOARD_QUERIES.items():
            metrics = benchmark_query(con, sql)
            rows.append({"query_name": name, **metrics, "benchmark_rows": total_rows})

        scale_sql = """
        WITH expanded AS (
            SELECT
                p.asset,
                p.date + (i * INTERVAL 1 DAY) AS synthetic_date,
                p.adj_close,
                i AS scale_bucket
            FROM clean_prices p
            CROSS JOIN range(0, 40) AS t(i)
        )
        SELECT asset, COUNT(*) AS rows, AVG(adj_close) AS avg_price
        FROM expanded
        GROUP BY asset
        """
        metrics = benchmark_query(con, scale_sql, repeats=5)
        benchmark_rows = con.execute("SELECT COUNT(*) * 40 FROM clean_prices").fetchone()[0]
        rows.append(
            {
                "query_name": "one_million_row_synthetic_scale",
                **metrics,
                "benchmark_rows": benchmark_rows,
            }
        )
        bench = pd.DataFrame(rows)
        con.execute("DELETE FROM sql_query_benchmarks")
        con.register("_bench", bench)
        con.execute("INSERT INTO sql_query_benchmarks BY NAME SELECT * FROM _bench")
        con.unregister("_bench")
        from volatility_platform.database.run_sql import run_sql_directory

        run_sql_directory(con, SQL_DIR)
    REPORTS_DIR.mkdir(exist_ok=True)
    bench.to_csv(REPORTS_DIR / "benchmark_results.csv", index=False)
    return bench
