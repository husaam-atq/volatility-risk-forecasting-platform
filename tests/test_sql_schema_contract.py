import duckdb
import pytest

TABLES = [
    "asset_universe",
    "raw_prices",
    "clean_prices",
    "data_quality_checks",
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
    "regime_metrics",
    "portfolio_risk",
    "sql_query_benchmarks",
]

VIEWS = [
    "v_asset_coverage",
    "v_daily_returns",
    "v_realised_volatility",
    "v_forecast_vs_realised",
    "v_var_breach_summary",
    "v_expected_shortfall_summary",
    "v_breach_clustering",
    "v_model_comparison",
    "v_regime_summary",
    "v_dashboard_overview",
    "v_asset_risk_summary",
    "v_portfolio_risk_summary",
    "v_validation_forecast_leakage",
]


@pytest.mark.parametrize("table", TABLES)
def test_expected_tables_exist(sample_db, table):
    with duckdb.connect(str(sample_db), read_only=True) as con:
        exists = con.execute(
            """
            SELECT COUNT(*)
            FROM information_schema.tables
            WHERE table_schema = 'main' AND table_name = ?
            """,
            [table],
        ).fetchone()[0]
    assert exists == 1


@pytest.mark.parametrize("view", VIEWS)
def test_expected_views_exist(sample_db, view):
    with duckdb.connect(str(sample_db), read_only=True) as con:
        exists = con.execute(
            """
            SELECT COUNT(*)
            FROM information_schema.tables
            WHERE table_schema = 'main' AND table_name = ?
            """,
            [view],
        ).fetchone()[0]
    assert exists == 1


@pytest.mark.parametrize(
    ("view", "columns"),
    [
        ("v_model_rank_summary", {"model", "avg_qlike", "avg_rank"}),
        ("v_var_breach_summary", {"model", "confidence_level", "breach_rate"}),
        ("v_expected_shortfall_summary", {"model", "confidence_level", "tail_loss_ratio"}),
        ("v_regime_summary", {"asset", "regime", "precision", "f1_score"}),
        ("v_dashboard_overview", {"asset_count", "first_date", "forecast_rows"}),
    ],
)
def test_core_views_return_expected_columns(full_db, view, columns):
    with duckdb.connect(str(full_db), read_only=True) as con:
        names = {row[1] for row in con.execute(f"PRAGMA table_info('{view}')").fetchall()}
    assert columns.issubset(names)
