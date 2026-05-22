from volatility_platform.backtesting.forecast_metrics import mae, qlike, rmse


def test_forecast_metrics_positive():
    y = [0.1, 0.2, 0.3]
    p = [0.11, 0.19, 0.28]
    assert rmse(y, p) > 0
    assert mae(y, p) > 0
    assert qlike(y, p) < 1
