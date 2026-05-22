-- Validation queries should return zero failing rows where possible.

CREATE OR REPLACE VIEW v_validation_duplicate_prices AS
SELECT asset, date, COUNT(*) AS row_count
FROM clean_prices
GROUP BY asset, date
HAVING COUNT(*) > 1;

CREATE OR REPLACE VIEW v_validation_non_positive_prices AS
SELECT *
FROM clean_prices
WHERE open <= 0 OR high <= 0 OR low <= 0 OR close <= 0 OR adj_close <= 0;

CREATE OR REPLACE VIEW v_validation_forecast_leakage AS
SELECT *
FROM volatility_forecasts
WHERE forecast_date >= target_date;

CREATE OR REPLACE VIEW v_validation_negative_forecasts AS
SELECT *
FROM volatility_forecasts
WHERE forecast_vol <= 0 OR forecast_var <= 0;

CREATE OR REPLACE VIEW v_validation_dashboard_queries AS
SELECT 'v_dashboard_overview' AS view_name, COUNT(*) AS rows FROM v_dashboard_overview
UNION ALL
SELECT 'v_model_comparison' AS view_name, COUNT(*) AS rows FROM v_model_comparison
UNION ALL
SELECT 'v_var_breach_summary' AS view_name, COUNT(*) AS rows FROM v_var_breach_summary
UNION ALL
SELECT 'v_asset_risk_summary' AS view_name, COUNT(*) AS rows FROM v_asset_risk_summary;
