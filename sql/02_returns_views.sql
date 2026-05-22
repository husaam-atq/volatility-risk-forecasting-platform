CREATE OR REPLACE VIEW v_daily_returns AS
SELECT
    asset,
    date,
    simple_return,
    log_return,
    abs_return,
    squared_return
FROM daily_returns;

CREATE OR REPLACE VIEW v_asset_coverage AS
SELECT
    p.asset,
    MIN(p.date) AS first_date,
    MAX(p.date) AS last_date,
    COUNT(*) AS price_rows,
    COUNT(r.simple_return) AS return_rows,
    SUM(CASE WHEN p.adj_close <= 0 THEN 1 ELSE 0 END) AS non_positive_prices
FROM clean_prices p
LEFT JOIN daily_returns r
  ON p.asset = r.asset AND p.date = r.date
GROUP BY p.asset
ORDER BY p.asset;

CREATE OR REPLACE VIEW v_sql_window_returns AS
SELECT
    asset,
    date,
    adj_close / LAG(adj_close) OVER (PARTITION BY asset ORDER BY date) - 1.0 AS simple_return,
    LN(adj_close / LAG(adj_close) OVER (PARTITION BY asset ORDER BY date)) AS log_return
FROM clean_prices;
