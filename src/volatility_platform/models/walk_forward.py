from __future__ import annotations

from pathlib import Path

import duckdb
import numpy as np
import pandas as pd

from volatility_platform.backtesting.forecast_metrics import improvement, metric_row
from volatility_platform.config import DATABASE_PATH, SQL_DIR, TRAIN_END, VALIDATION_END
from volatility_platform.database.run_sql import run_sql_directory
from volatility_platform.models.baseline import baseline_forecasts
from volatility_platform.models.ensemble import (
    simple_average_ensemble,
    validation_weighted_ensemble,
)
from volatility_platform.models.ewma import ewma_forecasts
from volatility_platform.models.garch_models import garch_forecasts
from volatility_platform.models.har_models import har_forecasts
from volatility_platform.models.ml_models import ml_forecasts


def build_model_frame(features: pd.DataFrame, realised: pd.DataFrame) -> pd.DataFrame:
    rv = realised[(realised["estimator"] == "close_to_close") & (realised["window"] == 21)][
        ["asset", "date", "realised_vol"]
    ].rename(columns={"date": "target_date"})
    frames = []
    for _asset, group in features.sort_values(["asset", "date"]).groupby("asset", sort=False):
        group = group.copy()
        group["target_date"] = group["date"].shift(-1)
        frames.append(group)
    model_frame = pd.concat(frames, ignore_index=True).dropna(subset=["target_date"])
    model_frame = model_frame.merge(rv, on=["asset", "target_date"], how="inner")
    model_frame["period"] = np.where(
        model_frame["target_date"] <= pd.Timestamp(TRAIN_END),
        "train",
        np.where(
            model_frame["target_date"] <= pd.Timestamp(VALIDATION_END),
            "validation",
            "test",
        ),
    )
    return model_frame


def compute_metrics(forecasts: pd.DataFrame, realised: pd.DataFrame) -> pd.DataFrame:
    merged = forecasts.merge(realised, on=["asset", "target_date"], how="inner")
    rows = []
    for (asset, model, period), group in merged.groupby(["asset", "model", "period"]):
        if period == "train" or len(group) < 10:
            continue
        rows.append(metric_row(asset, model, period, group["realised_vol"], group["forecast_vol"]))
    metrics = pd.DataFrame(rows)
    if metrics.empty:
        return metrics
    metrics["improvement_vs_rolling_21"] = np.nan
    metrics["improvement_vs_ewma"] = np.nan
    metrics["improvement_vs_garch"] = np.nan
    for (_asset, _period), group in metrics.groupby(["asset", "period"]):
        base_roll = group.loc[group["model"] == "rolling_21", "qlike"]
        base_ewma = group.loc[group["model"] == "ewma_094", "qlike"]
        base_garch = group.loc[group["model"] == "garch_11", "qlike"]
        for idx, row in group.iterrows():
            if not base_roll.empty:
                metrics.loc[idx, "improvement_vs_rolling_21"] = improvement(
                    base_roll.iloc[0], row["qlike"]
                )
            if not base_ewma.empty:
                metrics.loc[idx, "improvement_vs_ewma"] = improvement(
                    base_ewma.iloc[0], row["qlike"]
                )
            if not base_garch.empty:
                metrics.loc[idx, "improvement_vs_garch"] = improvement(
                    base_garch.iloc[0], row["qlike"]
                )
        metrics.loc[group.index, "rank_qlike"] = group["qlike"].rank(method="min").astype(int)
    metrics["rank_qlike"] = metrics["rank_qlike"].astype(int)
    return metrics


def run_forecasting_pipeline(db_path: str | Path = DATABASE_PATH) -> dict[str, object]:
    db_path = Path(db_path)
    with duckdb.connect(str(db_path)) as con:
        features = con.execute("SELECT * FROM volatility_features").fetchdf()
        returns = con.execute("SELECT * FROM daily_returns").fetchdf()
        realised = con.execute("SELECT * FROM realised_volatility").fetchdf()
    for frame in [features, returns, realised]:
        for column in ["date", "target_date", "forecast_date"]:
            if column in frame.columns:
                frame[column] = pd.to_datetime(frame[column])
    model_frame = build_model_frame(features, realised)
    realised_target = model_frame[["asset", "target_date", "realised_vol"]].drop_duplicates()

    forecast_parts = [
        baseline_forecasts(model_frame),
        ewma_forecasts(model_frame, returns),
        garch_forecasts(model_frame, returns),
        har_forecasts(model_frame),
    ]
    ml = ml_forecasts(model_frame)
    if not ml.empty:
        forecast_parts.append(ml)
    base_forecasts = pd.concat(forecast_parts, ignore_index=True)
    ensemble_models = [
        model
        for model in [
            "rolling_21",
            "har_rolling_update",
            "ewma_rolling_update",
            "garch_rolling_update",
            "gjr_rolling_update",
            "har_rv_log_ridge",
            "har_rv_market_log_ridge",
            "har_rv_market_huber",
            "ewma_tuned",
            "garch_11",
            "gjr_garch",
            "random_forest",
            "hist_gradient_boosting",
        ]
        if model in set(base_forecasts["model"])
    ]
    simple = simple_average_ensemble(base_forecasts, ensemble_models)
    weighted = validation_weighted_ensemble(base_forecasts, realised_target, ensemble_models)
    all_forecasts = pd.concat(
        [base_forecasts, simple, weighted],
        ignore_index=True,
    )
    all_forecasts = all_forecasts[all_forecasts["period"].isin(["validation", "test"])].copy()
    all_forecasts["forecast_date"] = pd.to_datetime(all_forecasts["forecast_date"]).dt.normalize()
    all_forecasts["target_date"] = pd.to_datetime(all_forecasts["target_date"]).dt.normalize()
    all_forecasts["forecast_vol"] = all_forecasts["forecast_vol"].clip(lower=1e-4, upper=5.0)
    all_forecasts["forecast_var"] = all_forecasts["forecast_vol"] ** 2
    all_forecasts = all_forecasts.drop_duplicates(["asset", "target_date", "model", "horizon"])
    metrics = compute_metrics(all_forecasts, realised_target)

    with duckdb.connect(str(db_path)) as con:
        con.execute("DELETE FROM volatility_forecasts")
        con.register("_forecasts", all_forecasts)
        con.execute("INSERT INTO volatility_forecasts BY NAME SELECT * FROM _forecasts")
        con.unregister("_forecasts")
        con.execute("DELETE FROM model_metrics")
        con.register("_metrics", metrics)
        con.execute(
            "INSERT INTO model_metrics (asset, model, period, n_obs, rmse, mae, qlike, mape, correlation, directional_accuracy, improvement_vs_rolling_21, improvement_vs_ewma, improvement_vs_garch, rank_qlike) SELECT asset, model, period, n_obs, rmse, mae, qlike, mape, correlation, directional_accuracy, improvement_vs_rolling_21, improvement_vs_ewma, improvement_vs_garch, rank_qlike FROM _metrics"
        )
        con.unregister("_metrics")
        run_sql_directory(con, SQL_DIR)

    best = metrics[metrics["period"] == "test"].sort_values("qlike").head(1)
    return {
        "forecast_rows": int(len(all_forecasts)),
        "metric_rows": int(len(metrics)),
        "best_model": None if best.empty else str(best.iloc[0]["model"]),
    }
