from __future__ import annotations

import numpy as np
import pandas as pd

from volatility_platform.backtesting.forecast_metrics import qlike


def simple_average_ensemble(forecasts: pd.DataFrame, model_names: list[str]) -> pd.DataFrame:
    subset = forecasts[forecasts["model"].isin(model_names)]
    pivot = subset.pivot_table(
        index=["asset", "forecast_date", "target_date", "period"],
        columns="model",
        values="forecast_vol",
    )
    pivot = pivot.dropna()
    if pivot.empty:
        return pd.DataFrame()
    out = pivot.mean(axis=1).rename("forecast_vol").reset_index()
    out["model"] = "simple_average_ensemble"
    out["horizon"] = 1
    out["forecast_vol"] = out["forecast_vol"].clip(lower=1e-4)
    out["forecast_var"] = out["forecast_vol"] ** 2
    out["training_window"] = "equal_weight_available_models"
    out["distribution"] = "ensemble"
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


def validation_weighted_ensemble(
    forecasts: pd.DataFrame,
    realised: pd.DataFrame,
    model_names: list[str],
) -> pd.DataFrame:
    subset = forecasts[forecasts["model"].isin(model_names)].copy()
    merged = subset.merge(realised, on=["asset", "target_date"], how="inner")
    rows = []
    for asset, group in merged.groupby("asset", sort=False):
        valid = group[group["period"] == "validation"]
        weights = {}
        for model in model_names:
            model_valid = valid[valid["model"] == model]
            if len(model_valid) > 20:
                score = qlike(model_valid["realised_vol"], model_valid["forecast_vol"])
                weights[model] = 1.0 / max(score - valid["realised_vol"].pow(2).mean(), 1e-6)
        if not weights:
            weights = {model: 1.0 for model in model_names}
        total = sum(weights.values())
        weights = {model: weight / total for model, weight in weights.items()}
        asset_subset = subset[subset["asset"] == asset]
        pivot = asset_subset.pivot_table(
            index=["asset", "forecast_date", "target_date", "period"],
            columns="model",
            values="forecast_vol",
        ).dropna()
        if pivot.empty:
            continue
        used_models = [model for model in model_names if model in pivot.columns]
        weight_vector = np.array([weights.get(model, 0.0) for model in used_models])
        if weight_vector.sum() == 0:
            weight_vector = np.ones(len(used_models)) / len(used_models)
        else:
            weight_vector = weight_vector / weight_vector.sum()
        ens = pivot[used_models].to_numpy() @ weight_vector
        frame = pivot.reset_index()[["asset", "forecast_date", "target_date", "period"]]
        frame["forecast_vol"] = ens
        frame["model"] = "validation_weighted_ensemble"
        rows.append(frame)
    if not rows:
        return pd.DataFrame()
    out = pd.concat(rows, ignore_index=True)
    out["horizon"] = 1
    out["forecast_vol"] = out["forecast_vol"].clip(lower=1e-4)
    out["forecast_var"] = out["forecast_vol"] ** 2
    out["training_window"] = "validation_inverse_qlike"
    out["distribution"] = "ensemble"
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
