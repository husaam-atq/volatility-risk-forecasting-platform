-- Coverage by asset.
SELECT * FROM v_asset_coverage ORDER BY asset;

-- Best test-period model by QLIKE for each asset.
SELECT asset, model, qlike, rank_qlike
FROM v_model_comparison
WHERE rank_qlike = 1
ORDER BY asset;

-- Aggregate model leaderboard.
SELECT * FROM v_model_rank_summary ORDER BY avg_qlike;

-- 95% VaR backtest summary.
SELECT asset, model, breach_rate, kupiec_p_value, christoffersen_p_value
FROM v_var_breach_summary
WHERE confidence_level = 0.95 AND period = 'test'
ORDER BY model, asset;

-- Dashboard overview query.
SELECT * FROM v_dashboard_overview;
