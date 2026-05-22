from __future__ import annotations

import numpy as np
import pandas as pd


def compute_daily_returns(prices: pd.DataFrame) -> pd.DataFrame:
    data = prices.sort_values(["asset", "date"]).copy()
    data["simple_return"] = data.groupby("asset")["adj_close"].pct_change()
    data["log_return"] = np.log(data["adj_close"] / data.groupby("asset")["adj_close"].shift(1))
    data = data.dropna(subset=["simple_return", "log_return"])
    data["abs_return"] = data["simple_return"].abs()
    data["squared_return"] = data["simple_return"] ** 2
    return data[["asset", "date", "simple_return", "log_return", "abs_return", "squared_return"]]
