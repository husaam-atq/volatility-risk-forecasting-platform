from __future__ import annotations

from pathlib import Path

import pandas as pd

from volatility_platform.config import DEFAULT_END_DATE, DEFAULT_START_DATE, RAW_DATA_DIR
from volatility_platform.data.loaders import ensure_sample_prices
from volatility_platform.data.universe import default_universe


def download_yfinance_prices(
    tickers: list[str] | None = None,
    start: str = DEFAULT_START_DATE,
    end: str = DEFAULT_END_DATE,
    cache_path: Path | None = None,
) -> pd.DataFrame:
    tickers = tickers or default_universe()["asset"].tolist()
    cache_path = cache_path or RAW_DATA_DIR / "yfinance_prices.csv"
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        import yfinance as yf

        data = yf.download(
            tickers=tickers,
            start=start,
            end=end,
            auto_adjust=False,
            actions=False,
            group_by="ticker",
            progress=False,
            threads=True,
        )
        rows = []
        for ticker in tickers:
            frame = data[ticker].copy() if isinstance(data.columns, pd.MultiIndex) else data.copy()
            frame = frame.rename(
                columns={
                    "Open": "open",
                    "High": "high",
                    "Low": "low",
                    "Close": "close",
                    "Adj Close": "adj_close",
                    "Volume": "volume",
                }
            )
            frame["asset"] = ticker
            frame["date"] = frame.index
            rows.append(
                frame[["date", "asset", "open", "high", "low", "close", "adj_close", "volume"]]
            )
        prices = pd.concat(rows, ignore_index=True).dropna(subset=["adj_close"])
        prices["source"] = "yfinance"
        if prices.empty:
            raise ValueError("download returned no usable rows")
        prices.to_csv(cache_path, index=False)
        return prices
    except Exception:
        return ensure_sample_prices()
