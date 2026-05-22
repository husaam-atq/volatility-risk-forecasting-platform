from __future__ import annotations

import numpy as np
import pandas as pd

from volatility_platform.backtesting.forecast_metrics import qlike
from volatility_platform.config import ANNUALISATION


def ewma_forecast_series(returns: pd.Series, lam: float = 0.94) -> pd.Series:
    values = returns.fillna(0.0).to_numpy()
    var = np.zeros(len(values))
    var[0] = np.nanvar(values[: min(63, len(values))]) if len(values) > 3 else 1e-4
    for i in range(1, len(values)):
        var[i] = lam * var[i - 1] + (1.0 - lam) * values[i - 1] ** 2
    return pd.Series(np.sqrt(np.maximum(var, 1e-10) * ANNUALISATION), index=returns.index)


def tune_lambda(model_frame: pd.DataFrame, returns: pd.DataFrame, lambdas=None) -> dict[str, float]:
    lambdas = lambdas or [0.90, 0.92, 0.94, 0.96, 0.97, 0.98]
    merged = model_frame[["asset", "date", "target_date", "period", "realised_vol"]]
    best = {}
    for asset, asset_returns in returns.sort_values(["asset", "date"]).groupby("asset"):
        returns_asset = asset_returns.set_index("date")["simple_return"]
        asset_model = merged[merged["asset"] == asset]
        scores = []
        for lam in lambdas:
            vol = ewma_forecast_series(returns_asset, lam=lam).rename("forecast_vol").reset_index()
            vol["asset"] = asset
            candidate = asset_model.merge(
                vol.rename(columns={"date": "date"}), on=["asset", "date"], how="left"
            )
            valid = candidate[candidate["period"] == "validation"].dropna()
            if len(valid) > 10:
                scores.append((qlike(valid["realised_vol"], valid["forecast_vol"]), lam))
        best[asset] = min(scores)[1] if scores else 0.94
    return best


def ewma_forecasts(
    model_frame: pd.DataFrame, returns: pd.DataFrame, tuned: bool = True
) -> pd.DataFrame:
    lambdas = tune_lambda(model_frame, returns) if tuned else {}
    rows = []
    for asset, asset_returns in returns.sort_values(["asset", "date"]).groupby("asset"):
        returns_series = asset_returns.set_index("date")["simple_return"]
        trailing_20_var_sum = returns_series.pow(2).rolling(20, min_periods=20).sum()
        for model, lam in [
            ("ewma_094", 0.94),
            ("ewma_tuned", lambdas.get(asset, 0.94)),
            ("ewma_rolling_update", lambdas.get(asset, 0.94)),
        ]:
            vol = ewma_forecast_series(returns_series, lam=lam)
            if model == "ewma_rolling_update":
                next_daily_var = (vol**2) / ANNUALISATION
                updated_var = (trailing_20_var_sum + next_daily_var) / 21.0
                vol = np.sqrt(np.maximum(updated_var, 1e-12) * ANNUALISATION)
            frame = pd.DataFrame(
                {
                    "asset": asset,
                    "forecast_date": vol.index,
                    "forecast_vol": vol.values,
                    "model": model,
                    "training_window": f"lambda={lam:.2f}",
                }
            )
            rows.append(frame)
        asset_model = model_frame[model_frame["asset"] == asset].copy()
        if not asset_model.empty:
            asset_model = asset_model.merge(
                trailing_20_var_sum.rename("trailing_20_var_sum").reset_index(),
                left_on="date",
                right_on="date",
                how="left",
            )
            blend_daily_var = (
                0.35 * asset_model["rv_5"] ** 2
                + 0.25 * asset_model["ewma_vol"] ** 2
                + 0.25 * asset_model["range_vol_21"] ** 2
                + 0.15 * asset_model["market_rv_21"] ** 2
            ) / ANNUALISATION
            scale = 1.0
            valid = asset_model["period"] == "validation"
            if valid.sum() > 20:
                scores = []
                for candidate_scale in np.linspace(0.1, 4.0, 79):
                    pred = np.sqrt(
                        np.maximum(
                            (
                                asset_model.loc[valid, "trailing_20_var_sum"]
                                + candidate_scale * blend_daily_var.loc[valid]
                            )
                            / 21.0
                            * ANNUALISATION,
                            1e-12,
                        )
                    )
                    scores.append(
                        (qlike(asset_model.loc[valid, "realised_vol"], pred), candidate_scale)
                    )
                scale = min(scores)[1]
            har_vol = np.sqrt(
                np.maximum(
                    (asset_model["trailing_20_var_sum"] + scale * blend_daily_var)
                    / 21.0
                    * ANNUALISATION,
                    1e-12,
                )
            )
            rows.append(
                pd.DataFrame(
                    {
                        "asset": asset,
                        "forecast_date": asset_model["date"].values,
                        "forecast_vol": har_vol.values,
                        "model": "har_rolling_update",
                        "training_window": f"validation_scale={scale:.2f}",
                    }
                )
            )
    out = pd.concat(rows, ignore_index=True)
    out = model_frame[["asset", "date", "target_date", "period"]].merge(
        out, left_on=["asset", "date"], right_on=["asset", "forecast_date"], how="inner"
    )
    out["horizon"] = 1
    out["forecast_vol"] = out["forecast_vol"].clip(lower=1e-4)
    out["forecast_var"] = out["forecast_vol"] ** 2
    out["distribution"] = "gaussian"
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
