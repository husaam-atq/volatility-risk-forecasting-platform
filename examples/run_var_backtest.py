from __future__ import annotations

from volatility_platform.risk.portfolio_risk import build_portfolio_risk
from volatility_platform.risk.var import run_var_backtest

if __name__ == "__main__":
    print(run_var_backtest())
    portfolio = build_portfolio_risk()
    print({"portfolio_rows": len(portfolio)})
