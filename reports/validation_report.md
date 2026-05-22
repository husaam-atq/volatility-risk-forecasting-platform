# Validation Report

## Target Achievement Summary

| Target | Result | Status |
| --- | --- | --- |
| QLIKE improvement vs rolling vol >= 12% | 0.63% | fail |
| QLIKE improvement vs EWMA >= 5% | 4.76% | fail |
| Best/top-2 model across >= 70% assets | 80.00% | pass |
| 95% VaR breach rate 4.7%-5.3% | 4.38% | fail |
| 99% VaR breach rate 0.8%-1.2% | 0.98% | pass |
| Kupiec not rejected for most assets | 72.67% | pass |
| Christoffersen not rejected for most assets | 92.00% | pass |
| ES tail-loss ratio 0.9-1.1 | 1.028 | pass |
| Top-decile vol capture >= 75% | 83.39% | pass |
| SQL handles 1m+ rows | 2,512,785 | pass |
| Dashboard queries < 1 sec | 15.65 ms p95 | pass |
| Tests pass | passed | pass |

## Data Quality Checks

| check_name | result_value | status | details | checked_at |
| --- | --- | --- | --- | --- |
| missing_price_values | 0.0000 | pass | Null OHLC or adjusted-close values in raw data. | 2026-05-22 11:50:14.164045 |
| duplicate_asset_date_keys | 0.0000 | pass | Duplicate raw asset/date records before de-duplication. | 2026-05-22 11:50:14.164045 |
| non_positive_prices | 0.0000 | pass | Non-positive OHLC or adjusted-close values. | 2026-05-22 11:50:14.164045 |
| minimum_asset_coverage_days | 2970.0000 | pass | Minimum number of observations across assets. | 2026-05-22 11:50:14.164045 |
| extreme_absolute_returns_gt_20pct | 0.0000 | pass | Daily absolute returns above 20%. | 2026-05-22 11:50:14.164045 |
| clean_price_rows | 29700.0000 | pass | Rows after cleaning. | 2026-05-22 11:50:14.164045 |

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

Regime metrics report top-decile volatility capture, false high-volatility flag rate, persistence and transition counts.

## Dashboard Query Checks

Dashboard views are benchmarked and stored in `sql_query_benchmarks`.

## Tests Summary

The repository includes unit, integration and smoke tests for database construction, SQL views, features, models, backtests, reports and dashboard import.
The target table records the verification status from the current project run.

## Honest Limitations

Targets that fail are retained in the report. The project favours transparent model validation over forcing every metric to pass.
