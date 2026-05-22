CREATE OR REPLACE VIEW v_model_comparison AS
SELECT
    asset,
    model,
    period,
    n_obs,
    rmse,
    mae,
    qlike,
    mape,
    correlation,
    directional_accuracy,
    improvement_vs_rolling_21,
    improvement_vs_ewma,
    improvement_vs_garch,
    rank_qlike
FROM model_metrics
WHERE period = 'test';

CREATE OR REPLACE VIEW v_model_rank_summary AS
SELECT
    model,
    COUNT(*) AS asset_count,
    AVG(qlike) AS avg_qlike,
    AVG(mae) AS avg_mae,
    AVG(rmse) AS avg_rmse,
    AVG(rank_qlike) AS avg_rank,
    SUM(CASE WHEN rank_qlike <= 2 THEN 1 ELSE 0 END) * 1.0 / COUNT(*) AS top_two_share,
    AVG(improvement_vs_rolling_21) AS avg_improvement_vs_rolling_21,
    AVG(improvement_vs_ewma) AS avg_improvement_vs_ewma,
    AVG(improvement_vs_garch) AS avg_improvement_vs_garch
FROM v_model_comparison
GROUP BY model
ORDER BY avg_qlike;
