CREATE OR REPLACE VIEW v_regime_summary AS
SELECT
    l.asset,
    l.regime,
    COUNT(*) AS days,
    AVG(l.realised_vol) AS avg_realised_vol,
            AVG(l.high_vol_flag) AS high_vol_share,
            MAX(m.top_decile_capture) AS top_decile_capture,
            MAX(m.false_high_flag_rate) AS false_high_flag_rate,
            MAX(m.precision) AS precision,
            MAX(m.recall) AS recall,
            MAX(m.f1_score) AS f1_score,
            MAX(m.false_positive_rate) AS false_positive_rate
        FROM regime_labels l
LEFT JOIN regime_metrics m
  ON l.asset = m.asset
GROUP BY l.asset, l.regime;

CREATE OR REPLACE VIEW v_dashboard_overview AS
SELECT
    (SELECT COUNT(DISTINCT asset) FROM clean_prices) AS asset_count,
    (SELECT MIN(date) FROM clean_prices) AS first_date,
    (SELECT MAX(date) FROM clean_prices) AS last_date,
    (SELECT COUNT(*) FROM clean_prices) AS clean_price_rows,
    (SELECT COUNT(*) FROM daily_returns) AS return_rows,
    (SELECT COUNT(*) FROM realised_volatility) AS realised_vol_rows,
    (SELECT COUNT(*) FROM volatility_forecasts) AS forecast_rows,
    (SELECT COUNT(*) FROM breach_events) AS breach_rows;

CREATE OR REPLACE VIEW v_asset_risk_summary AS
SELECT
    r.asset,
    AVG(r.simple_return) * 252.0 AS annualised_return,
    STDDEV_SAMP(r.simple_return) * SQRT(252.0) AS annualised_volatility,
    MIN(r.simple_return) AS worst_daily_return,
    MAX(rv.realised_vol) AS max_realised_vol,
    AVG(CASE WHEN b.confidence_level = 0.95 AND b.period = 'test' THEN b.breach ELSE NULL END) AS test_var95_breach_rate
FROM daily_returns r
        LEFT JOIN realised_volatility rv
          ON r.asset = rv.asset AND r.date = rv.date
         AND rv.estimator = 'close_to_close' AND rv."window" = 21
LEFT JOIN breach_events b
  ON r.asset = b.asset AND r.date = b.target_date
GROUP BY r.asset;

CREATE OR REPLACE VIEW v_portfolio_risk_summary AS
SELECT
    model,
    COUNT(*) AS observations,
    AVG(portfolio_return) * 252.0 AS annualised_return,
    STDDEV_SAMP(portfolio_return) * SQRT(252.0) AS realised_volatility,
    AVG(forecast_vol) AS avg_forecast_vol,
    AVG(CASE WHEN portfolio_return < var_95 THEN 1 ELSE 0 END) AS var95_breach_rate,
    AVG(CASE WHEN portfolio_return < var_99 THEN 1 ELSE 0 END) AS var99_breach_rate
FROM portfolio_risk
GROUP BY model;
