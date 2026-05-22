import duckdb
import pandas as pd

import volatility_platform.database.build_database as build_module
import volatility_platform.utils.performance as performance_module
from volatility_platform.database.build_database import build_database
from volatility_platform.reporting.model_report import (
    asset_level_audit_summary,
    asset_level_model_audit,
)
from volatility_platform.reporting.report_writer import _regime_threshold_tradeoff
from volatility_platform.utils.performance import run_sql_benchmarks


def test_asset_level_model_audit_has_one_row_per_asset(full_db):
    with duckdb.connect(str(full_db), read_only=True) as con:
        metrics = con.execute("SELECT * FROM model_metrics").fetchdf()
        asset_count = con.execute("SELECT COUNT(*) FROM asset_universe").fetchone()[0]
    audit = asset_level_model_audit(metrics)
    assert len(audit) == asset_count
    assert audit["best_model_qlike"].notna().all()
    assert audit["rolling_21_qlike"].notna().all()


def test_asset_level_audit_summary_counts_assets(full_db):
    with duckdb.connect(str(full_db), read_only=True) as con:
        metrics = con.execute("SELECT * FROM model_metrics").fetchdf()
    audit = asset_level_model_audit(metrics)
    summary = asset_level_audit_summary(audit)
    top_two = summary.loc[
        summary["metric"] == "assets_where_har_rolling_update_is_top_two", "value"
    ].iloc[0]
    assert 0 <= top_two <= len(audit)


def test_regime_threshold_tradeoff_includes_current_threshold(full_db):
    tradeoff = _regime_threshold_tradeoff(full_db)
    assert {"threshold_percentile", "validation_f1", "full_f1"}.issubset(tradeoff.columns)
    assert (tradeoff["threshold_percentile"] == 0.84).any()
    assert tradeoff["validation_f1"].notna().all()


def test_report_source_flag_matches_database(sample_db):
    with duckdb.connect(str(sample_db), read_only=True) as con:
        sources = pd.Series(
            [row[0] for row in con.execute("SELECT DISTINCT source FROM raw_prices").fetchall()]
        )
    assert set(sources).issubset({"sample", "yfinance"})
    assert not sources.empty


def test_temp_database_build_does_not_write_report_timestamp(tmp_path, monkeypatch):
    monkeypatch.setattr(build_module, "REPORTS_DIR", tmp_path)
    build_database(db_path=tmp_path / "temp.duckdb", use_live=False)
    assert not (tmp_path / "database_build_time.txt").exists()


def test_temp_sql_benchmark_does_not_write_report_csv(sample_db, tmp_path, monkeypatch):
    monkeypatch.setattr(performance_module, "REPORTS_DIR", tmp_path)
    run_sql_benchmarks(sample_db)
    assert not (tmp_path / "benchmark_results.csv").exists()
