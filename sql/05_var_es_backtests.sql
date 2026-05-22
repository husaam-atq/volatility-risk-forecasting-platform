CREATE OR REPLACE VIEW v_var_breach_summary AS
SELECT
    asset,
    model,
    confidence_level,
    method,
    period,
    n_obs,
    expected_breaches,
    actual_breaches,
    breach_rate,
    kupiec_p_value,
    christoffersen_p_value,
    es_tail_loss_ratio,
    max_cluster_length
FROM var_backtest_results;

CREATE OR REPLACE VIEW v_expected_shortfall_summary AS
SELECT
    asset,
    model,
    confidence_level,
    method,
    period,
    AVG(CASE WHEN breach = 1 THEN -realised_return ELSE NULL END) AS avg_realised_tail_loss,
    AVG(CASE WHEN breach = 1 THEN -es_return ELSE NULL END) AS avg_expected_shortfall,
    AVG(CASE WHEN breach = 1 THEN -realised_return ELSE NULL END)
        / NULLIF(AVG(CASE WHEN breach = 1 THEN -es_return ELSE NULL END), 0) AS tail_loss_ratio
FROM breach_events
GROUP BY asset, model, confidence_level, method, period;
