import pandas as pd

from volatility_platform.features.realised_volatility import compute_realised_volatility


def test_realised_volatility_shapes():
    dates = pd.bdate_range("2020-01-01", periods=80)
    prices = pd.DataFrame(
        {
            "asset": "A",
            "date": dates,
            "open": 100.0,
            "high": 101.0,
            "low": 99.0,
            "close": [100.0 + i for i in range(80)],
            "adj_close": [100.0 + i for i in range(80)],
            "volume": 1000,
            "source": "test",
        }
    )
    out = compute_realised_volatility(prices, windows=[5, 21])
    assert {"close_to_close", "parkinson"}.issubset(set(out["estimator"]))
    assert (out["realised_vol"] >= 0).all()
