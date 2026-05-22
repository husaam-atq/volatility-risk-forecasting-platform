import pandas as pd

from volatility_platform.models.garch_models import _recursive_garch_vol


def test_garch_recursion_positive():
    returns = pd.Series([0.01, -0.02, 0.005, 0.012] * 80)
    vol = _recursive_garch_vol(returns, (0.02, 0.07, 0.9, 0.0))
    assert (vol > 0).all()
