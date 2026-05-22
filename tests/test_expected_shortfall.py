from volatility_platform.risk.expected_shortfall import gaussian_es
from volatility_platform.risk.var import gaussian_var


def test_es_more_conservative_than_var():
    assert gaussian_es(0.05, 0.02) < gaussian_var(0.05, 0.02)
