from __future__ import annotations

import warnings

import numpy as np
import pandas as pd

from volatility_platform.config import ANNUALISATION, TRAIN_END, VALIDATION_END


def _fit_arch_params(train_returns: pd.Series, kind: str) -> tuple[float, float, float, float]:
    try:
        from arch import arch_model

        scaled = train_returns.dropna() * 100.0
        if len(scaled) < 250:
            raise ValueError("too few returns for GARCH fit")
        p, o, q = (1, 0, 1) if kind == "garch_11" else (1, 1, 1)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            res = arch_model(
                scaled,
                mean="Constant",
                vol="GARCH",
                p=p,
                o=o,
                q=q,
                dist="t",
                rescale=False,
            ).fit(disp="off", options={"maxiter": 250})
        params = res.params
        omega = max(float(params.get("omega", 0.01)), 1e-8)
        alpha = max(float(params.get("alpha[1]", 0.05)), 0.0)
        beta = max(float(params.get("beta[1]", 0.90)), 0.0)
        gamma = max(float(params.get("gamma[1]", 0.0)), 0.0)
        if alpha + 0.5 * gamma + beta >= 0.995:
            scale = 0.995 / (alpha + 0.5 * gamma + beta)
            alpha *= scale
            gamma *= scale
            beta *= scale
        return omega, alpha, beta, gamma
    except Exception:
        return 0.02, 0.07, 0.90, 0.0


def _recursive_garch_vol(
    returns: pd.Series, params: tuple[float, float, float, float]
) -> pd.Series:
    omega, alpha, beta, gamma = params
    values = returns.fillna(0.0).to_numpy() * 100.0
    var = np.zeros(len(values))
    var[0] = max(np.nanvar(values[: min(252, len(values))]), 1e-6)
    for i in range(1, len(values)):
        shock = values[i - 1]
        leverage = gamma * shock**2 * float(shock < 0)
        var[i] = omega + alpha * shock**2 + leverage + beta * var[i - 1]
        var[i] = float(np.clip(var[i], 1e-8, 400.0))
    return pd.Series(np.sqrt(var) / 100.0 * np.sqrt(ANNUALISATION), index=returns.index)


def garch_forecasts(model_frame: pd.DataFrame, returns: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for asset, asset_returns in returns.sort_values(["asset", "date"]).groupby("asset"):
        series = asset_returns.set_index("date")["simple_return"]
        trailing_20_var_sum = series.pow(2).rolling(20, min_periods=20).sum()
        train = series[series.index <= pd.Timestamp(TRAIN_END)]
        train_valid = series[series.index <= pd.Timestamp(VALIDATION_END)]
        for model in ["garch_11", "gjr_garch", "garch_rolling_update", "gjr_rolling_update"]:
            fit_kind = "garch_11" if model in {"garch_11", "garch_rolling_update"} else "gjr_garch"
            params = _fit_arch_params(train if fit_kind == "garch_11" else train_valid, fit_kind)
            vol = _recursive_garch_vol(series, params)
            if model.endswith("rolling_update"):
                next_daily_var = (vol**2) / ANNUALISATION
                updated_var = (trailing_20_var_sum + next_daily_var) / 21.0
                vol = np.sqrt(np.maximum(updated_var, 1e-12) * ANNUALISATION)
            rows.append(
                pd.DataFrame(
                    {
                        "asset": asset,
                        "forecast_date": vol.index,
                        "forecast_vol": vol.values,
                        "model": model,
                        "training_window": (
                            "fixed_params_train_valid"
                            if fit_kind == "gjr_garch"
                            else "fixed_params_train"
                        ),
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
    out["distribution"] = "student_t_params"
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
