# Validation Report

## Data Source

| data_source | raw_price_rows | first_date | last_date |
| --- | --- | --- | --- |
| yfinance | 28620 | 2015-01-02 00:00:00 | 2026-05-20 00:00:00 |

## Target Achievement Summary

| Target | Result | Status |
| --- | --- | --- |
| QLIKE improvement vs rolling vol >= 12% | 40.41% | pass |
| QLIKE improvement vs EWMA >= 5% | 83.15% | pass |
| QLIKE improvement vs GARCH >= 5% | 91.50% | pass |
| Best/top-2 model across >= 70% assets | 80.00% | pass |
| 95% VaR breach rate 4.7%-5.3% | 4.76% | pass |
| 99% VaR breach rate 0.8%-1.2% | 0.81% | pass |
| Kupiec not rejected for most assets | 85.79% | pass |
| Christoffersen not rejected for most assets | 87.89% | pass |
| ES tail-loss ratio 0.9-1.1 | 0.984 | pass |
| Top-decile vol capture >= 75% | 75.44% | pass |
| High-vol precision >= 40% | 43.46% | pass |
| High-vol F1 >= 50% | 55.07% | pass |
| False high-vol flag rate <= 60% | 56.54% | pass |
| SQL handles 1m+ rows | 2,873,756 | pass |
| Dashboard queries < 1 sec | 16.14 ms p95 | pass |
| Tests pass | passed | pass |

## Data Quality Checks

| check_name | result_value | status | details | checked_at |
| --- | --- | --- | --- | --- |
| missing_price_values | 0.0000 | pass | Null OHLC or adjusted-close values in raw data. | 2026-05-22 16:41:05.657263 |
| duplicate_asset_date_keys | 0.0000 | pass | Duplicate raw asset/date records before de-duplication. | 2026-05-22 16:41:05.657263 |
| non_positive_prices | 0.0000 | pass | Non-positive OHLC or adjusted-close values. | 2026-05-22 16:41:05.657263 |
| minimum_asset_coverage_days | 2862.0000 | pass | Minimum number of observations across assets. | 2026-05-22 16:41:05.657263 |
| extreme_absolute_returns_gt_20pct | 4.0000 | pass | Daily absolute returns above 20%. | 2026-05-22 16:41:05.657263 |
| clean_price_rows | 28620.0000 | pass | Rows after cleaning. | 2026-05-22 16:41:05.657263 |

## SQL Validation Checks

Validation views test duplicate asset/date keys, non-positive prices, forecast leakage and non-positive forecasts.
Run `python -m pytest tests/test_sql_validation_queries.py -v` for the automated check.

## Model Training Checks

All forecasts use a fixed time-series split: training through 2019, validation through 2021 and test from 2022 onward.
Machine-learning models fit on the training window only; ensemble weights and VaR residual calibration are estimated from validation data.

## Forecast Metric Checks

RMSE, MAE, QLIKE, MAPE, correlation and directional accuracy are stored in `model_metrics` and compared through SQL views.

## VaR and ES Backtesting Checks

The risk layer stores VaR estimates, Expected Shortfall estimates, breach events, Kupiec tests, Christoffersen tests and ES diagnostics.

## Regime Detection Checks

Regime metrics report top-decile volatility capture, precision, recall, F1, false-positive rate, persistence and transition counts.

## Dashboard Query Checks

Dashboard views are benchmarked and stored in `sql_query_benchmarks`.

## Tests Summary

The repository includes unit, integration and smoke tests for database construction, SQL views, features, models, backtests, reports and dashboard import.
The target table records the verification status from the current project run.

## Honest Limitations

Targets that fail are retained in the report. The project favours transparent model validation over forcing every metric to pass.
