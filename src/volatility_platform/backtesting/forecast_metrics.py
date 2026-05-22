from __future__ import annotations

import numpy as np
import pandas as pd

EPS = 1e-10


def rmse(y_true, y_pred) -> float:
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    return float(np.sqrt(np.mean((y_true - y_pred) ** 2)))


def mae(y_true, y_pred) -> float:
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    return float(np.mean(np.abs(y_true - y_pred)))


def qlike(y_true_vol, y_pred_vol) -> float:
    realised_var = np.maximum(np.asarray(y_true_vol, dtype=float) ** 2, EPS)
    forecast_var = np.maximum(np.asarray(y_pred_vol, dtype=float) ** 2, EPS)
    return float(np.mean(realised_var / forecast_var + np.log(forecast_var)))


def mape(y_true, y_pred) -> float:
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    denom = np.maximum(np.abs(y_true), EPS)
    return float(np.mean(np.abs((y_true - y_pred) / denom)))


def correlation(y_true, y_pred) -> float:
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    if len(y_true) < 3 or np.std(y_true) == 0 or np.std(y_pred) == 0:
        return float("nan")
    return float(np.corrcoef(y_true, y_pred)[0, 1])


def directional_accuracy(y_true, y_pred) -> float:
    y_true = pd.Series(y_true)
    y_pred = pd.Series(y_pred)
    realised_direction = np.sign(y_true.diff().dropna())
    forecast_direction = np.sign(y_pred.diff().dropna())
    if len(realised_direction) == 0:
        return float("nan")
    return float((realised_direction.values == forecast_direction.values).mean())


def improvement(base_metric: float, candidate_metric: float) -> float:
    if base_metric == 0 or np.isnan(base_metric) or np.isnan(candidate_metric):
        return float("nan")
    return float((base_metric - candidate_metric) / abs(base_metric))


def metric_row(asset: str, model: str, period: str, y_true, y_pred) -> dict[str, object]:
    return {
        "asset": asset,
        "model": model,
        "period": period,
        "n_obs": len(y_true),
        "rmse": rmse(y_true, y_pred),
        "mae": mae(y_true, y_pred),
        "qlike": qlike(y_true, y_pred),
        "mape": mape(y_true, y_pred),
        "correlation": correlation(y_true, y_pred),
        "directional_accuracy": directional_accuracy(y_true, y_pred),
    }
