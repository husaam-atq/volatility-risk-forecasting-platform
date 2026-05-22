CREATE OR REPLACE VIEW v_forecast_vs_realised AS
SELECT
    f.asset,
    f.model,
    f.forecast_date,
    f.target_date,
    f.period,
    f.forecast_vol,
    rv.realised_vol,
    f.forecast_vol - rv.realised_vol AS forecast_error,
    POWER(f.forecast_vol - rv.realised_vol, 2) AS squared_error,
    ABS(f.forecast_vol - rv.realised_vol) AS absolute_error
FROM volatility_forecasts f
JOIN realised_volatility rv
  ON f.asset = rv.asset
     AND f.target_date = rv.date
     AND rv.estimator = 'close_to_close'
     AND rv."window" = 21;
