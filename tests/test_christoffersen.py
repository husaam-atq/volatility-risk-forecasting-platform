from volatility_platform.backtesting.christoffersen import christoffersen_independence_test


def test_christoffersen_returns_pvalue():
    lr, p = christoffersen_independence_test([0, 1, 0, 0, 1, 0, 0, 0])
    assert lr >= 0
    assert 0 <= p <= 1
