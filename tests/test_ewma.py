import pandas as pd

from volatility_platform.models.ewma import ewma_forecast_series


def test_ewma_positive():
    returns = pd.Series([0.01, -0.02, 0.005, 0.0, 0.01])
    vol = ewma_forecast_series(returns)
    assert (vol > 0).all()
