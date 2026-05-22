CREATE OR REPLACE VIEW v_realised_volatility AS
SELECT
    asset,
    date,
    estimator,
    "window",
    realised_vol,
    realised_var
FROM realised_volatility;

CREATE OR REPLACE VIEW v_sql_rolling_volatility AS
SELECT
    asset,
    date,
    SQRT(252.0 * AVG(squared_return) OVER (
        PARTITION BY asset
        ORDER BY date
        ROWS BETWEEN 20 PRECEDING AND CURRENT ROW
    )) AS sql_rv_21
FROM daily_returns;
