from volatility_platform.risk.var import gaussian_var


def test_var_negative_for_left_tail():
    assert gaussian_var(0.05, 0.02) < 0
