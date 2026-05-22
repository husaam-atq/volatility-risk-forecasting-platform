from __future__ import annotations

import numpy as np
import pandas as pd

from volatility_platform.config import ANNUALISATION
from volatility_platform.features.returns import compute_daily_returns


def ewma_volatility(returns: pd.Series, lam: float = 0.94) -> pd.Series:
    values = returns.fillna(0.0).to_numpy()
    var = np.zeros(len(values))
    if len(values) == 0:
        return pd.Series(dtype=float, index=returns.index)
    var[0] = np.nanvar(values[: min(21, len(values))]) if len(values) > 2 else values[0] ** 2
    for i in range(1, len(values)):
        var[i] = lam * var[i - 1] + (1.0 - lam) * values[i - 1] ** 2
    return pd.Series(np.sqrt(var * ANNUALISATION), index=returns.index)


def build_volatility_features(prices: pd.DataFrame) -> pd.DataFrame:
    returns = compute_daily_returns(prices)
    base = prices.merge(returns, on=["asset", "date"], how="left").sort_values(["asset", "date"])
    frames: list[pd.DataFrame] = []
    spy_rv = None
    for asset, group in base.groupby("asset", sort=False):
        group = group.copy()
        ret = group["simple_return"]
        group["rv_5"] = np.sqrt(ret.pow(2).rolling(5, min_periods=5).mean() * ANNUALISATION)
        group["rv_10"] = np.sqrt(ret.pow(2).rolling(10, min_periods=10).mean() * ANNUALISATION)
        group["rv_21"] = np.sqrt(ret.pow(2).rolling(21, min_periods=21).mean() * ANNUALISATION)
        group["rv_63"] = np.sqrt(ret.pow(2).rolling(63, min_periods=63).mean() * ANNUALISATION)
        group["rv_126"] = np.sqrt(ret.pow(2).rolling(126, min_periods=63).mean() * ANNUALISATION)
        group["rv_252"] = np.sqrt(ret.pow(2).rolling(252, min_periods=126).mean() * ANNUALISATION)
        group["ewma_vol"] = ewma_volatility(ret)
        group["abs_return_1"] = ret.abs()
        group["abs_return_5"] = ret.abs().rolling(5, min_periods=5).mean()
        group["return_1"] = ret
        group["return_5"] = ret.rolling(5, min_periods=5).sum()
        range_var = (np.log(group["high"] / group["low"]) ** 2) / (4.0 * np.log(2.0))
        group["range_vol_21"] = np.sqrt(
            range_var.rolling(21, min_periods=21).mean() * ANNUALISATION
        )
        group["vol_of_vol_21"] = group["rv_21"].rolling(21, min_periods=10).std()
        cummax = group["adj_close"].rolling(63, min_periods=5).max()
        group["drawdown_63"] = group["adj_close"] / cummax - 1.0
        group["skew_63"] = ret.rolling(63, min_periods=20).skew()
        group["kurt_63"] = ret.rolling(63, min_periods=20).kurt()
        if asset == "SPY":
            spy_rv = group[["date", "rv_21", "return_1"]].rename(
                columns={"rv_21": "market_rv_21", "return_1": "market_return_1"}
            )
        frames.append(group)
    features = pd.concat(frames, ignore_index=True)
    if spy_rv is not None:
        features = features.merge(spy_rv, on="date", how="left")
    cols = [
        "asset",
        "date",
        "rv_5",
        "rv_10",
        "rv_21",
        "rv_63",
        "rv_126",
        "rv_252",
        "ewma_vol",
        "abs_return_1",
        "abs_return_5",
        "return_1",
        "return_5",
        "range_vol_21",
        "vol_of_vol_21",
        "drawdown_63",
        "skew_63",
        "kurt_63",
        "market_rv_21",
        "market_return_1",
    ]
    return features[cols].replace([np.inf, -np.inf], np.nan).dropna().reset_index(drop=True)


def feature_columns() -> list[str]:
    return [
        "rv_5",
        "rv_10",
        "rv_21",
        "rv_63",
        "rv_126",
        "rv_252",
        "ewma_vol",
        "abs_return_1",
        "abs_return_5",
        "return_1",
        "return_5",
        "range_vol_21",
        "vol_of_vol_21",
        "drawdown_63",
        "skew_63",
        "kurt_63",
        "market_rv_21",
        "market_return_1",
    ]
