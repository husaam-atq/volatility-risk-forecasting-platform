# SQL Architecture

## Database Design

DuckDB is the default database because it is portable, fast and requires no server for local portfolio projects. The database file is stored at `database/market_risk.duckdb`.

## Core Tables

- `asset_universe`: fixed asset metadata.
- `raw_prices`: ingested market data.
- `clean_prices`: de-duplicated, validated price data.
- `daily_returns`: simple, log, absolute and squared returns.
- `realised_volatility`: close-to-close and range-based realised-volatility estimators.
- `volatility_features`: lagged features for forecasting.
- `volatility_forecasts`: model outputs keyed by forecast date and target date.
- `model_metrics`: forecast validation metrics.
- `var_estimates` and `expected_shortfall_estimates`: risk estimates.
- `breach_events`: realised return versus VaR outcomes.
- `var_backtest_results`: Kupiec, Christoffersen and ES diagnostics.
- `regime_labels`: high/medium/low volatility states.
- `sql_query_benchmarks`: dashboard and scale-test timings.

## Views

Dashboard and validation views include:

- `v_asset_coverage`
- `v_daily_returns`
- `v_realised_volatility`
- `v_forecast_vs_realised`
- `v_model_comparison`
- `v_var_breach_summary`
- `v_expected_shortfall_summary`
- `v_breach_clustering`
- `v_regime_summary`
- `v_dashboard_overview`
- `v_asset_risk_summary`
- `v_portfolio_risk_summary`

## Pipeline Flow

Prices are loaded into DuckDB, transformed into returns and realised volatility, converted into features, forecast by Python models, written back to SQL, converted into risk estimates and finally exposed through SQL views.

## Dashboard Query Flow

Streamlit connects to DuckDB in read-only mode where practical. Charts and cards are built from SQL queries, keeping the dashboard aligned with persisted validation results.
