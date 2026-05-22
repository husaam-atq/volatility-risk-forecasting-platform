from __future__ import annotations

import pandas as pd

UNIVERSE_ROWS = [
    ("SPY", "SPDR S&P 500 ETF Trust", "ETF", "Equity", "US large-cap equity benchmark", "market"),
    ("QQQ", "Invesco QQQ Trust", "ETF", "Equity", "US growth equity benchmark", "growth"),
    (
        "IWM",
        "iShares Russell 2000 ETF",
        "ETF",
        "Equity",
        "US small-cap equity benchmark",
        "small_cap",
    ),
    (
        "TLT",
        "iShares 20+ Year Treasury Bond ETF",
        "ETF",
        "Rates",
        "Long-duration Treasury proxy",
        "rates",
    ),
    ("GLD", "SPDR Gold Shares", "ETF", "Commodity", "Gold proxy", "commodity"),
    ("USO", "United States Oil Fund", "ETF", "Commodity", "Crude oil proxy", "commodity"),
    ("AAPL", "Apple Inc.", "Equity", "Technology", "Large-cap technology equity", "single_name"),
    (
        "MSFT",
        "Microsoft Corporation",
        "Equity",
        "Technology",
        "Large-cap technology equity",
        "single_name",
    ),
    (
        "NVDA",
        "NVIDIA Corporation",
        "Equity",
        "Technology",
        "High-beta semiconductor equity",
        "single_name",
    ),
    ("JPM", "JPMorgan Chase & Co.", "Equity", "Financials", "Large-cap bank equity", "single_name"),
]


def default_universe() -> pd.DataFrame:
    return pd.DataFrame(
        UNIVERSE_ROWS,
        columns=[
            "asset",
            "asset_name",
            "asset_class",
            "sector",
            "description",
            "benchmark_role",
        ],
    )
