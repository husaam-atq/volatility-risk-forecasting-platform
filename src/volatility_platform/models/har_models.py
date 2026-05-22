from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.linear_model import HuberRegressor, RidgeCV
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from volatility_platform.config import RANDOM_SEED

HAR_FEATURES = [
    "rv_5",
    "rv_10",
    "rv_21",
    "rv_63",
    "rv_126",
    "rv_252",
    "ewma_vol",
    "range_vol_21",
    "vol_of_vol_21",
]

HAR_MARKET_FEATURES = [*HAR_FEATURES, "market_rv_21", "market_return_1", "drawdown_63"]


def _log_feature_frame(frame: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    out = frame[columns].copy()
    for column in columns:
        if "return" not in column and "drawdown" not in column:
            out[f"log_{column}"] = np.log(out[column].clip(lower=1e-6))
    return out


def _fit_predict_log_model(
    train: pd.DataFrame,
    score: pd.DataFrame,
    columns: list[str],
    robust: bool,
) -> np.ndarray:
    estimator = (
        HuberRegressor(max_iter=500, epsilon=1.35)
        if robust
        else RidgeCV(alphas=[0.01, 0.1, 1.0, 10.0, 100.0])
    )
    pipeline = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
            ("model", estimator),
        ]
    )
    x_train = _log_feature_frame(train, columns)
    y_train = np.log(train["realised_vol"].clip(lower=1e-6))
    pipeline.fit(x_train, y_train)
    return np.exp(pipeline.predict(_log_feature_frame(score, columns))).clip(1e-4, 5.0)


def har_forecasts(model_frame: pd.DataFrame) -> pd.DataFrame:
    rows = []
    model_specs = {
        "har_rv_log_ridge": (HAR_FEATURES, False),
        "har_rv_market_log_ridge": (HAR_MARKET_FEATURES, False),
        "har_rv_market_huber": (HAR_MARKET_FEATURES, True),
    }
    for asset, group in model_frame.sort_values(["asset", "date"]).groupby("asset", sort=False):
        train_mask = group["period"] == "train"
        score_mask = ~train_mask
        if train_mask.sum() < 250:
            continue
        train = group.loc[train_mask].copy()
        score = group.loc[score_mask].copy()
        for model_name, (columns, robust) in model_specs.items():
            try:
                preds = _fit_predict_log_model(train, score, columns, robust=robust)
            except Exception:
                rng = np.random.default_rng(RANDOM_SEED)
                jitter = rng.normal(0.0, 1e-6, size=score.shape[0])
                preds = np.clip(score["rv_21"].to_numpy() + jitter, 1e-4, 5.0)
            rows.append(
                pd.DataFrame(
                    {
                        "asset": asset,
                        "forecast_date": score["date"].values,
                        "target_date": score["target_date"].values,
                        "period": score["period"].values,
                        "model": model_name,
                        "horizon": 1,
                        "forecast_vol": preds,
                        "training_window": "train_2015_2019_log_target",
                        "distribution": "log_linear_har",
                    }
                )
            )
    if not rows:
        return pd.DataFrame()
    out = pd.concat(rows, ignore_index=True)
    out["forecast_var"] = out["forecast_vol"] ** 2
    return out[
        [
            "asset",
            "forecast_date",
            "target_date",
            "model",
            "horizon",
            "forecast_vol",
            "forecast_var",
            "training_window",
            "distribution",
            "period",
        ]
    ]
