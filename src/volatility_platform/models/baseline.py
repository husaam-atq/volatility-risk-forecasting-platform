from __future__ import annotations

import pandas as pd


def baseline_forecasts(model_frame: pd.DataFrame) -> pd.DataFrame:
    rows = []
    model_map = {
        "previous_day_rv": "rv_21",
        "rolling_21": "rv_21",
        "rolling_63": "rv_63",
    }
    for model, column in model_map.items():
        frame = model_frame[["asset", "date", "target_date", "period", column]].rename(
            columns={column: "forecast_vol", "date": "forecast_date"}
        )
        frame["model"] = model
        rows.append(frame)
    out = pd.concat(rows, ignore_index=True)
    out["horizon"] = 1
    out["forecast_vol"] = out["forecast_vol"].clip(lower=1e-4)
    out["forecast_var"] = out["forecast_vol"] ** 2
    out["training_window"] = "rolling_feature"
    out["distribution"] = "volatility_proxy"
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
