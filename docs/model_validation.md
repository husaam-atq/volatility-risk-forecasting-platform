# Model Validation

## Forecast Metrics

The project reports RMSE, MAE, QLIKE, MAPE, correlation and directional accuracy. QLIKE is the primary ranking metric because volatility forecasts are variance forecasts and the realised volatility proxy is noisy.

QLIKE is calculated as `realised_variance / forecast_variance - log(realised_variance / forecast_variance) - 1`. A perfect forecast has zero loss, which makes percentage improvements against baselines interpretable.

## Model Ranking

Models are ranked within each asset on identical test-period target dates. Aggregate rankings use all assets in the fixed universe.

## VaR And ES Backtesting

VaR and ES estimates are created from volatility forecasts using validation-period Student-t residual calibration. The test period is reserved for final backtesting.

## Kupiec Test Interpretation

A Kupiec p-value above 0.05 means the test does not reject the expected breach rate. It does not prove the model is correct; it only means the observed count is not statistically inconsistent with the target alpha.

## Christoffersen Test Interpretation

A Christoffersen p-value above 0.05 means breach independence is not rejected. Clustering can still exist visually or economically even when the statistical test has low power.

## Limitations Of Statistical Backtests

Daily 99% VaR tests often have few breaches, so the tests are noisy. A model can pass coverage and still underestimate severity. ES diagnostics are included to reduce that blind spot.
