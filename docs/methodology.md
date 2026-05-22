# Methodology

## Volatility Forecasting Problem

The platform forecasts one-day-ahead volatility for a fixed multi-asset universe. The operational target is next-day 21-day close-to-close realised volatility, which is a smoother proxy than a single squared return while still advancing one trading day at a time.

## Realised Volatility Estimators

Close-to-close volatility uses rolling squared daily returns. Parkinson volatility uses the high-low range. Garman-Klass adds open-close information. Rogers-Satchell is more robust to drift. Yang-Zhang combines overnight, open-close and range terms.

## QLIKE

QLIKE compares realised variance with forecast variance and is the primary model-selection metric. It is commonly used in volatility forecasting because it is less distorted by noisy volatility proxies than simple squared-error metrics.

## Walk-Forward Validation

The fixed split is:

- Training: 2015-2019.
- Validation: 2020-2021.
- Test: 2022 onward.

Forecasts are produced with `forecast_date < target_date`. Ensemble weights and VaR residual calibration use validation data only.

## No-Leakage Design

Feature rows are keyed by forecast date. The target is joined on the next trading date. SQL validation views check for `forecast_date >= target_date` and non-positive forecasts.

## VaR And Expected Shortfall

Annualised volatility forecasts are converted to daily sigma. Validation-period empirical residual quantiles generate 95% and 99% VaR. Expected Shortfall uses the average validation residual beyond the VaR quantile.

## Kupiec And Christoffersen Tests

The Kupiec test evaluates unconditional coverage: whether the observed breach frequency matches the target alpha. The Christoffersen test evaluates independence: whether breaches are clustered.

## Regime Detection

Regime labels use prior rolling volatility percentiles and z-scores. High-volatility labels are evaluated against full-sample top-decile realised-volatility days for diagnostic reporting.

## SQL-Backed Architecture

DuckDB stores all analytical tables and exposes dashboard-ready views. The dashboard queries SQL views rather than recomputing metrics in memory.

## Limitations

Daily public data cannot capture intraday risk, liquidity or execution effects. Statistical backtests have limited power. Machine-learning results depend on regime representativeness and careful validation.
