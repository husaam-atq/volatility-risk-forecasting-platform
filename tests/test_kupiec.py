from volatility_platform.backtesting.kupiec import kupiec_test


def test_kupiec_returns_pvalue():
    lr, p = kupiec_test([0] * 95 + [1] * 5, 0.05)
    assert lr >= 0
    assert 0 <= p <= 1
