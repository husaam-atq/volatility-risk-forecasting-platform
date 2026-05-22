from __future__ import annotations

import numpy as np
import pandas as pd

from volatility_platform.config import ANNUALISATION, VOL_WINDOWS
from volatility_platform.features.returns import compute_daily_returns


def close_to_close_volatility(returns: pd.Series, window: int) -> pd.Series:
    return np.sqrt(ANNUALISATION * returns.rolling(window, min_periods=window).mean())


def parkinson_variance(high: pd.Series, low: pd.Series) -> pd.Series:
    return (np.log(high / low) ** 2) / (4.0 * np.log(2.0))


def garman_klass_variance(
    open_: pd.Series, high: pd.Series, low: pd.Series, close: pd.Series
) -> pd.Series:
    log_hl = np.log(high / low)
    log_co = np.log(close / open_)
    return 0.5 * log_hl**2 - (2.0 * np.log(2.0) - 1.0) * log_co**2


def rogers_satchell_variance(
    open_: pd.Series, high: pd.Series, low: pd.Series, close: pd.Series
) -> pd.Series:
    return np.log(high / close) * np.log(high / open_) + np.log(low / close) * np.log(low / open_)


def yang_zhang_variance(
    open_: pd.Series, high: pd.Series, low: pd.Series, close: pd.Series
) -> pd.Series:
    prev_close = close.shift(1)
    overnight = np.log(open_ / prev_close)
    open_close = np.log(close / open_)
    rs = rogers_satchell_variance(open_, high, low, close)
    return 0.10 * overnight**2 + 0.10 * open_close**2 + 0.80 * rs


def compute_realised_volatility(
    prices: pd.DataFrame, windows: list[int] | None = None
) -> pd.DataFrame:
    windows = windows or VOL_WINDOWS
    returns = compute_daily_returns(prices)
    merged = prices.merge(returns, on=["asset", "date"], how="left")
    frames: list[pd.DataFrame] = []
    for asset, group in merged.sort_values(["asset", "date"]).groupby("asset", sort=False):
        group = group.copy()
        group["close_to_close_daily_var"] = group["simple_return"] ** 2
        group["parkinson_daily_var"] = parkinson_variance(group["high"], group["low"])
        group["garman_klass_daily_var"] = garman_klass_variance(
            group["open"], group["high"], group["low"], group["close"]
        ).clip(lower=0)
        group["rogers_satchell_daily_var"] = rogers_satchell_variance(
            group["open"], group["high"], group["low"], group["close"]
        ).clip(lower=0)
        group["yang_zhang_daily_var"] = yang_zhang_variance(
            group["open"], group["high"], group["low"], group["close"]
        ).clip(lower=0)
        for estimator in [
            "close_to_close",
            "parkinson",
            "garman_klass",
            "rogers_satchell",
            "yang_zhang",
        ]:
            daily_col = f"{estimator}_daily_var"
            for window in windows:
                realised_var = (
                    group[daily_col].rolling(window, min_periods=window).mean() * ANNUALISATION
                )
                frame = pd.DataFrame(
                    {
                        "asset": asset,
                        "date": group["date"],
                        "estimator": estimator,
                        "window": window,
                        "realised_vol": np.sqrt(realised_var),
                        "realised_var": realised_var,
                    }
                )
                frames.append(frame.dropna())
    out = pd.concat(frames, ignore_index=True)
    out = out.replace([np.inf, -np.inf], np.nan).dropna()
    return out
