import pandas as pd

from volatility_platform.features.returns import compute_daily_returns


def test_return_calculation():
    prices = pd.DataFrame(
        {
            "asset": ["A", "A", "A"],
            "date": pd.date_range("2020-01-01", periods=3),
            "adj_close": [100.0, 110.0, 99.0],
        }
    )
    out = compute_daily_returns(prices)
    assert round(out.iloc[0]["simple_return"], 6) == 0.1
    assert round(out.iloc[1]["simple_return"], 6) == -0.1
