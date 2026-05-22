from __future__ import annotations

from math import sqrt

import numpy as np
import pandas as pd

from volatility_platform.config import DEFAULT_END_DATE, DEFAULT_START_DATE, SAMPLE_PRICES_PATH
from volatility_platform.data.universe import default_universe


def generate_sample_prices(
    start: str = DEFAULT_START_DATE,
    end: str = DEFAULT_END_DATE,
    seed: int = 20260522,
) -> pd.DataFrame:
    universe = default_universe()
    start_prices = {
        "SPY": 430.0,
        "QQQ": 360.0,
        "IWM": 190.0,
        "TLT": 95.0,
        "GLD": 185.0,
        "USO": 70.0,
        "AAPL": 175.0,
        "MSFT": 330.0,
        "NVDA": 450.0,
        "JPM": 160.0,
    }
    idio_base = {
        "SPY": 0.010,
        "QQQ": 0.012,
        "IWM": 0.0135,
        "TLT": 0.009,
        "GLD": 0.0105,
        "USO": 0.018,
        "AAPL": 0.015,
        "MSFT": 0.0135,
        "NVDA": 0.022,
        "JPM": 0.014,
    }
    beta = {
        "SPY": 0.78,
        "QQQ": 0.86,
        "IWM": 0.82,
        "TLT": -0.22,
        "GLD": 0.10,
        "USO": 0.35,
        "AAPL": 0.82,
        "MSFT": 0.80,
        "NVDA": 0.88,
        "JPM": 0.72,
    }
    dates = pd.bdate_range(start, end)
    rng = np.random.default_rng(seed)
    market_shock = rng.standard_t(df=7, size=len(dates))
    market_vol = np.zeros(len(dates))
    market_vol[0] = 0.010
    for i, date in enumerate(dates[1:], start=1):
        regime = 1.0
        if pd.Timestamp("2020-02-15") <= date <= pd.Timestamp("2020-06-30"):
            regime = 2.8
        elif pd.Timestamp("2022-01-01") <= date <= pd.Timestamp("2022-11-30"):
            regime = 1.65
        elif pd.Timestamp("2025-02-01") <= date <= pd.Timestamp("2025-05-31"):
            regime = 1.45
        market_vol[i] = (
            sqrt(
                0.000004
                + 0.09 * (market_shock[i - 1] * market_vol[i - 1]) ** 2
                + 0.88 * market_vol[i - 1] ** 2
            )
            * regime
        )
        market_vol[i] = float(np.clip(market_vol[i], 0.004, 0.080))
    market_return = 0.00018 + market_vol * market_shock

    rows: list[dict[str, object]] = []
    for asset in universe["asset"]:
        asset_seed = seed + sum(ord(char) for char in asset)
        asset_rng = np.random.default_rng(asset_seed)
        idio = asset_rng.standard_t(df=6, size=len(dates))
        idio_vol = np.zeros(len(dates))
        idio_vol[0] = idio_base[asset]
        price = start_prices[asset]
        meta = universe.set_index("asset").loc[asset]
        for i, date in enumerate(dates):
            if i > 0:
                idio_vol[i] = sqrt(
                    idio_base[asset] ** 2 * 0.08
                    + 0.08 * (idio[i - 1] * idio_vol[i - 1]) ** 2
                    + 0.87 * idio_vol[i - 1] ** 2
                )
                idio_vol[i] = float(
                    np.clip(idio_vol[i], idio_base[asset] * 0.45, idio_base[asset] * 4.0)
                )
            stress_bias = 0.0
            if pd.Timestamp("2020-02-15") <= date <= pd.Timestamp("2020-04-15"):
                stress_bias = -0.0019 * max(beta[asset], 0.05)
            if pd.Timestamp("2022-03-01") <= date <= pd.Timestamp("2022-06-30"):
                stress_bias += -0.00065 * max(beta[asset], 0.05)
            ret = beta[asset] * market_return[i] + idio_vol[i] * idio[i] + stress_bias
            ret = float(np.clip(ret, -0.18, 0.16))
            prev_close = price
            price = max(2.0, price * np.exp(ret))
            overnight = asset_rng.normal(0.0, idio_vol[i] * 0.22)
            open_price = max(1.0, prev_close * np.exp(overnight))
            span = abs(ret) + abs(asset_rng.normal(0, idio_vol[i] * 0.75)) + 0.001
            high = max(open_price, price) * (1.0 + span * 0.45)
            low = min(open_price, price) * max(0.2, 1.0 - span * 0.45)
            adj_factor = 1.0 + 0.00002 * np.sin(i / 120.0)
            volume = int(
                asset_rng.lognormal(mean=6.3, sigma=0.35)
                * 10000
                * (1.0 + min(market_vol[i] * 25, 2.5))
            )
            rows.append(
                {
                    "date": date.normalize(),
                    "asset": asset,
                    "open": round(open_price, 6),
                    "high": round(high, 6),
                    "low": round(low, 6),
                    "close": round(price, 6),
                    "adj_close": round(price * adj_factor, 6),
                    "volume": volume,
                    "source": "sample",
                    "asset_class": meta["asset_class"],
                    "description": meta["description"],
                }
            )
    return pd.DataFrame(rows)


def ensure_sample_prices(path=SAMPLE_PRICES_PATH) -> pd.DataFrame:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        return pd.read_csv(path, parse_dates=["date"])
    data = generate_sample_prices()
    data.to_csv(path, index=False)
    return data


def load_price_file(path=SAMPLE_PRICES_PATH) -> pd.DataFrame:
    return pd.read_csv(path, parse_dates=["date"])
