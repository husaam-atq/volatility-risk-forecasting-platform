-- Core DuckDB schema for the volatility risk platform.

CREATE TABLE IF NOT EXISTS asset_universe (
    asset VARCHAR PRIMARY KEY,
    asset_name VARCHAR,
    asset_class VARCHAR,
    sector VARCHAR,
    description VARCHAR,
    benchmark_role VARCHAR
);

CREATE TABLE IF NOT EXISTS raw_prices (
    asset VARCHAR,
    date DATE,
    open DOUBLE,
    high DOUBLE,
    low DOUBLE,
    close DOUBLE,
    adj_close DOUBLE,
    volume BIGINT,
    source VARCHAR,
    PRIMARY KEY (asset, date)
);

CREATE TABLE IF NOT EXISTS clean_prices (
    asset VARCHAR,
    date DATE,
    open DOUBLE,
    high DOUBLE,
    low DOUBLE,
    close DOUBLE,
    adj_close DOUBLE,
    volume BIGINT,
    source VARCHAR,
    PRIMARY KEY (asset, date)
);

CREATE TABLE IF NOT EXISTS data_quality_checks (
    check_name VARCHAR,
    result_value DOUBLE,
    status VARCHAR,
    details VARCHAR,
    checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS daily_returns (
    asset VARCHAR,
    date DATE,
    simple_return DOUBLE,
    log_return DOUBLE,
    abs_return DOUBLE,
    squared_return DOUBLE,
    PRIMARY KEY (asset, date)
);

CREATE TABLE IF NOT EXISTS realised_volatility (
    asset VARCHAR,
    date DATE,
    estimator VARCHAR,
    "window" INTEGER,
    realised_vol DOUBLE,
    realised_var DOUBLE,
    PRIMARY KEY (asset, date, estimator, "window")
);

CREATE TABLE IF NOT EXISTS volatility_features (
    asset VARCHAR,
    date DATE,
    rv_5 DOUBLE,
    rv_10 DOUBLE,
    rv_21 DOUBLE,
    rv_63 DOUBLE,
    rv_126 DOUBLE,
    rv_252 DOUBLE,
    ewma_vol DOUBLE,
    abs_return_1 DOUBLE,
    abs_return_5 DOUBLE,
    return_1 DOUBLE,
    return_5 DOUBLE,
    range_vol_21 DOUBLE,
    vol_of_vol_21 DOUBLE,
    drawdown_63 DOUBLE,
    skew_63 DOUBLE,
    kurt_63 DOUBLE,
    market_rv_21 DOUBLE,
    market_return_1 DOUBLE,
    PRIMARY KEY (asset, date)
);

CREATE TABLE IF NOT EXISTS volatility_forecasts (
    asset VARCHAR,
    forecast_date DATE,
    target_date DATE,
    model VARCHAR,
    horizon INTEGER,
    forecast_vol DOUBLE,
    forecast_var DOUBLE,
    training_window VARCHAR,
    distribution VARCHAR,
    period VARCHAR,
    PRIMARY KEY (asset, target_date, model, horizon)
);

CREATE TABLE IF NOT EXISTS model_metrics (
    asset VARCHAR,
    model VARCHAR,
    period VARCHAR,
    n_obs INTEGER,
    rmse DOUBLE,
    mae DOUBLE,
    qlike DOUBLE,
    mape DOUBLE,
    correlation DOUBLE,
    directional_accuracy DOUBLE,
    improvement_vs_rolling_21 DOUBLE,
    improvement_vs_ewma DOUBLE,
    improvement_vs_garch DOUBLE,
    rank_qlike INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (asset, model, period)
);

CREATE TABLE IF NOT EXISTS var_estimates (
    asset VARCHAR,
    model VARCHAR,
    forecast_date DATE,
    target_date DATE,
    confidence_level DOUBLE,
    var_return DOUBLE,
    method VARCHAR,
    period VARCHAR,
    PRIMARY KEY (asset, model, target_date, confidence_level, method)
);

CREATE TABLE IF NOT EXISTS expected_shortfall_estimates (
    asset VARCHAR,
    model VARCHAR,
    forecast_date DATE,
    target_date DATE,
    confidence_level DOUBLE,
    es_return DOUBLE,
    method VARCHAR,
    period VARCHAR,
    PRIMARY KEY (asset, model, target_date, confidence_level, method)
);

CREATE TABLE IF NOT EXISTS breach_events (
    asset VARCHAR,
    model VARCHAR,
    target_date DATE,
    confidence_level DOUBLE,
    method VARCHAR,
    realised_return DOUBLE,
    var_return DOUBLE,
    es_return DOUBLE,
    breach INTEGER,
    breach_size DOUBLE,
    period VARCHAR,
    PRIMARY KEY (asset, model, target_date, confidence_level, method)
);

CREATE TABLE IF NOT EXISTS var_backtest_results (
    asset VARCHAR,
    model VARCHAR,
    confidence_level DOUBLE,
    method VARCHAR,
    period VARCHAR,
    n_obs INTEGER,
    expected_breaches DOUBLE,
    actual_breaches INTEGER,
    breach_rate DOUBLE,
    kupiec_lr DOUBLE,
    kupiec_p_value DOUBLE,
    christoffersen_lr DOUBLE,
    christoffersen_p_value DOUBLE,
    es_tail_loss_ratio DOUBLE,
    avg_breach_size DOUBLE,
    max_cluster_length INTEGER,
    avg_days_between_breaches DOUBLE,
    PRIMARY KEY (asset, model, confidence_level, method, period)
);

CREATE TABLE IF NOT EXISTS regime_labels (
    asset VARCHAR,
    date DATE,
    realised_vol DOUBLE,
    percentile_score DOUBLE,
    z_score DOUBLE,
    regime VARCHAR,
    is_top_decile INTEGER,
    high_vol_flag INTEGER,
    PRIMARY KEY (asset, date)
);

CREATE TABLE IF NOT EXISTS regime_metrics (
    asset VARCHAR,
    top_decile_capture DOUBLE,
    false_high_flag_rate DOUBLE,
    precision DOUBLE,
    recall DOUBLE,
    f1_score DOUBLE,
    false_positive_rate DOUBLE,
    high_regime_share DOUBLE,
    median_regime_days DOUBLE,
    transition_count INTEGER,
    PRIMARY KEY (asset)
);

CREATE TABLE IF NOT EXISTS portfolio_risk (
    date DATE,
    model VARCHAR,
    portfolio_return DOUBLE,
    realised_vol DOUBLE,
    forecast_vol DOUBLE,
    var_95 DOUBLE,
    var_99 DOUBLE,
    es_95 DOUBLE,
    es_99 DOUBLE,
    PRIMARY KEY (date, model)
);

CREATE TABLE IF NOT EXISTS sql_query_benchmarks (
    query_name VARCHAR,
    row_count BIGINT,
    mean_ms DOUBLE,
    p50_ms DOUBLE,
    p95_ms DOUBLE,
    min_ms DOUBLE,
    max_ms DOUBLE,
    benchmark_rows BIGINT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (query_name)
);
