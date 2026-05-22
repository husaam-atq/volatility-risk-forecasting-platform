from __future__ import annotations

import pandas as pd


def default_stress_scenarios() -> pd.DataFrame:
    return pd.DataFrame(
        [
            ("equity_shock", -0.08, 0.01, 0.00, 1.25),
            ("rates_shock_proxy", -0.02, -0.06, 0.00, 1.15),
            ("commodity_shock_proxy", -0.03, 0.00, -0.10, 1.20),
            ("volatility_shock", -0.04, -0.01, -0.03, 1.60),
            ("correlation_shock", -0.05, -0.02, -0.02, 1.40),
        ],
        columns=["scenario", "equity_return", "rates_return", "commodity_return", "vol_multiplier"],
    )
