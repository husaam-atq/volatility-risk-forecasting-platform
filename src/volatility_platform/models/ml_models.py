from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.ensemble import HistGradientBoostingRegressor, RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from volatility_platform.config import RANDOM_SEED, TRAIN_END, VALIDATION_END
from volatility_platform.features.lagged_features import feature_columns


def _period_mask(frame: pd.DataFrame, period: str) -> pd.Series:
    if period == "train":
        return frame["target_date"] <= pd.Timestamp(TRAIN_END)
    if period == "validation":
        return (frame["target_date"] > pd.Timestamp(TRAIN_END)) & (
            frame["target_date"] <= pd.Timestamp(VALIDATION_END)
        )
    return frame["target_date"] > pd.Timestamp(VALIDATION_END)


class QuantileClipper(BaseEstimator, TransformerMixin):
    def __init__(self, lower: float = 0.01, upper: float = 0.99):
        self.lower = lower
        self.upper = upper

    def fit(self, x, y=None):
        values = np.asarray(x, dtype=float)
        self.lower_bounds_ = np.nanquantile(values, self.lower, axis=0)
        self.upper_bounds_ = np.nanquantile(values, self.upper, axis=0)
        return self

    def transform(self, x):
        values = np.asarray(x, dtype=float)
        return np.clip(values, self.lower_bounds_, self.upper_bounds_)


def ml_forecasts(model_frame: pd.DataFrame) -> pd.DataFrame:
    features = feature_columns()
    rows = []
    estimators = {
        "random_forest": RandomForestRegressor(
            n_estimators=260,
            max_depth=10,
            min_samples_leaf=6,
            random_state=RANDOM_SEED,
            n_jobs=-1,
        ),
        "hist_gradient_boosting": HistGradientBoostingRegressor(
            max_iter=320,
            learning_rate=0.03,
            max_leaf_nodes=20,
            l2_regularization=0.04,
            random_state=RANDOM_SEED,
        ),
    }
    for asset, group in model_frame.groupby("asset", sort=False):
        group = group.sort_values("date").copy()
        train_mask = _period_mask(group, "train")
        if train_mask.sum() < 250:
            continue
        x_train = group.loc[train_mask, features]
        y_train = group.loc[train_mask, "realised_vol"]
        score_mask = ~train_mask
        for model_name, estimator in estimators.items():
            steps = [
                ("imputer", SimpleImputer(strategy="median")),
                ("clipper", QuantileClipper(lower=0.01, upper=0.99)),
            ]
            if model_name == "hist_gradient_boosting":
                steps.append(("scaler", StandardScaler()))
            steps.append(("model", estimator))
            pipeline = Pipeline(steps)
            pipeline.fit(x_train, y_train)
            preds = np.clip(pipeline.predict(group.loc[score_mask, features]), 1e-4, None)
            rows.append(
                pd.DataFrame(
                    {
                        "asset": asset,
                        "forecast_date": group.loc[score_mask, "date"].values,
                        "target_date": group.loc[score_mask, "target_date"].values,
                        "period": group.loc[score_mask, "period"].values,
                        "model": model_name,
                        "horizon": 1,
                        "forecast_vol": preds,
                        "training_window": "train_2015_2019",
                        "distribution": "nonparametric",
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
