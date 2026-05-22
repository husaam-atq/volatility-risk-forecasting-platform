from __future__ import annotations

from pathlib import Path

from volatility_platform.config import DATABASE_PATH, REPORTS_DIR
from volatility_platform.database.queries import table_row_counts


def write_sql_performance_report(bench, db_path: str | Path = DATABASE_PATH) -> None:
    REPORTS_DIR.mkdir(exist_ok=True)
    counts = table_row_counts(db_path)
    build_time_path = REPORTS_DIR / "database_build_time.txt"
    build_time = (
        build_time_path.read_text(encoding="utf-8").strip()
        if build_time_path.exists()
        else "not recorded"
    )
    total_rows = int(counts["row_count"].sum())
    db_size_mb = Path(db_path).stat().st_size / (1024 * 1024) if Path(db_path).exists() else 0.0
    lines = [
        "# SQL Performance Report",
        "",
        "## Summary",
        "",
        f"- Full database rebuild time: {build_time} seconds.",
        f"- Database file size: {db_size_mb:.2f} MB.",
        f"- Total persisted analytical rows: {total_rows:,}.",
        f"- Largest benchmarked scale: {int(bench['benchmark_rows'].max()):,} rows.",
        "",
        "## Row Counts",
        "",
        "| Table | Rows |",
        "|---|---:|",
    ]
    lines.extend([f"| {r.table_name} | {int(r.row_count):,} |" for r in counts.itertuples()])
    lines.extend(
        [
            "",
            "## Query Benchmarks",
            "",
            "| Query | Mean ms | p50 ms | p95 ms | Rows returned | Benchmark rows |",
            "|---|---:|---:|---:|---:|---:|",
        ]
    )
    for r in bench.itertuples():
        lines.append(
            f"| {r.query_name} | {r.mean_ms:.3f} | {r.p50_ms:.3f} | {r.p95_ms:.3f} | {int(r.row_count):,} | {int(r.benchmark_rows):,} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "DuckDB is used as the analytical layer for joins, validation views, dashboard summaries and benchmark queries.",
            "The synthetic scale query expands the clean price table to confirm that the SQL layer remains responsive above one million rows.",
            "Reported timings are hardware dependent and should be regenerated on any target machine before quoting exact numbers.",
            "",
            "## Limitations",
            "",
            "Benchmarks are local single-user timings and do not represent concurrent production traffic.",
            "The scale test stresses relational scans and aggregations; it is not a full simulation of every downstream model table.",
            "Memory usage is not forced or pinned, so operating-system cache effects can improve repeated query timings.",
        ]
    )
    (REPORTS_DIR / "sql_performance_report.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )
    bench.to_csv(REPORTS_DIR / "benchmark_results.csv", index=False)
