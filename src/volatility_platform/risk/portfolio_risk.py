from __future__ import annotations

from pathlib import Path

import duckdb
import numpy as np
import pandas as pd

from volatility_platform.config import ANNUALISATION, DATABASE_PATH, SQL_DIR
from volatility_platform.database.run_sql import run_sql_directory


def equal_weight_portfolio_returns(returns: pd.DataFrame) -> pd.DataFrame:
    pivot = returns.pivot(index="date", columns="asset", values="simple_return").dropna()
    portfolio = pivot.mean(axis=1).rename("portfolio_return").reset_index()
    return portfolio


def portfolio_volatility(returns: pd.DataFrame, weights: np.ndarray | None = None) -> float:
    pivot = returns.pivot(index="date", columns="asset", values="simple_return").dropna()
    weights = weights if weights is not None else np.repeat(1.0 / pivot.shape[1], pivot.shape[1])
    cov = pivot.cov().to_numpy() * ANNUALISATION
    return float(np.sqrt(weights @ cov @ weights))


def volatility_contributions(
    returns: pd.DataFrame, weights: np.ndarray | None = None
) -> pd.DataFrame:
    pivot = returns.pivot(index="date", columns="asset", values="simple_return").dropna()
    weights = weights if weights is not None else np.repeat(1.0 / pivot.shape[1], pivot.shape[1])
    cov = pivot.cov().to_numpy() * ANNUALISATION
    port_vol = np.sqrt(weights @ cov @ weights)
    marginal = cov @ weights / max(port_vol, 1e-12)
    contrib = weights * marginal / max(port_vol, 1e-12)
    return pd.DataFrame({"asset": pivot.columns, "vol_contribution": contrib})


def build_portfolio_risk(db_path: str | Path = DATABASE_PATH) -> pd.DataFrame:
    with duckdb.connect(str(db_path)) as con:
        returns = con.execute("SELECT * FROM daily_returns").fetchdf()
        forecasts = con.execute("SELECT * FROM volatility_forecasts").fetchdf()
    returns["date"] = pd.to_datetime(returns["date"])
    forecasts["target_date"] = pd.to_datetime(forecasts["target_date"])
    portfolio = equal_weight_portfolio_returns(returns)
    forecast_pivot = forecasts.pivot_table(
        index=["target_date", "model"], columns="asset", values="forecast_vol"
    ).dropna()
    rows = []
    for (date, model), row in forecast_pivot.iterrows():
        sigma = float(np.sqrt(np.mean((row.values / np.sqrt(ANNUALISATION)) ** 2)))
        port_ret = portfolio.loc[portfolio["date"] == date, "portfolio_return"]
        if port_ret.empty:
            continue
        rows.append(
            {
                "date": date,
                "model": model,
                "portfolio_return": float(port_ret.iloc[0]),
                "realised_vol": np.nan,
                "forecast_vol": sigma * np.sqrt(ANNUALISATION),
                "var_95": -1.645 * sigma,
                "var_99": -2.326 * sigma,
                "es_95": -2.063 * sigma,
                "es_99": -2.665 * sigma,
            }
        )
    out = pd.DataFrame(rows)
    if not out.empty:
        out["realised_vol"] = (
            out.sort_values("date")
            .groupby("model")["portfolio_return"]
            .transform(lambda s: s.rolling(21, min_periods=10).std() * np.sqrt(ANNUALISATION))
        )
    with duckdb.connect(str(db_path)) as con:
        con.execute("DELETE FROM portfolio_risk")
        con.register("_portfolio", out)
        con.execute("INSERT INTO portfolio_risk BY NAME SELECT * FROM _portfolio")
        con.unregister("_portfolio")
        run_sql_directory(con, SQL_DIR)
    return out
