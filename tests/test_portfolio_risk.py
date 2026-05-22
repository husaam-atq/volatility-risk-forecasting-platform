import duckdb
import numpy as np

from volatility_platform.risk.portfolio_risk import volatility_contributions


def test_portfolio_contributions_sum(sample_db):
    with duckdb.connect(str(sample_db), read_only=True) as con:
        returns = con.execute("SELECT * FROM daily_returns").fetchdf()
    contrib = volatility_contributions(returns)
    assert np.isclose(contrib["vol_contribution"].sum(), 1.0)
