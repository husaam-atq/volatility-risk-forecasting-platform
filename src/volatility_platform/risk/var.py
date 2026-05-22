from __future__ import annotations

from pathlib import Path

import duckdb
import numpy as np
import pandas as pd
from scipy.stats import norm

from volatility_platform.backtesting.breach_analysis import (
    average_days_between_breaches,
    max_cluster_length,
)
from volatility_platform.backtesting.christoffersen import christoffersen_independence_test
from volatility_platform.backtesting.es_backtests import es_tail_loss_ratio
from volatility_platform.backtesting.kupiec import kupiec_test
from volatility_platform.config import ANNUALISATION, DATABASE_PATH, SQL_DIR
from volatility_platform.database.run_sql import run_sql_directory


def gaussian_var(alpha: float, sigma: float) -> float:
    return float(norm.ppf(alpha) * sigma)


def calculate_var_es(
    forecasts: pd.DataFrame,
    returns: pd.DataFrame,
    confidence_levels: list[float] | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    confidence_levels = confidence_levels or [0.95, 0.99]
    merged = forecasts.merge(
        returns[["asset", "date", "simple_return"]].rename(
            columns={"date": "target_date", "simple_return": "realised_return"}
        ),
        on=["asset", "target_date"],
        how="inner",
    )
    merged["daily_sigma"] = merged["forecast_vol"] / np.sqrt(ANNUALISATION)
    var_rows = []
    es_rows = []
    breach_rows = []
    result_rows = []
    for (asset, model), group in merged.groupby(["asset", "model"], sort=False):
        validation = group[group["period"] == "validation"].copy()
        for confidence in confidence_levels:
            alpha = 1.0 - confidence
            if len(validation) >= 50:
                residual = validation["realised_return"] / validation["daily_sigma"].clip(
                    lower=1e-8
                )
                q = float(np.quantile(residual, alpha))
                tail = residual[residual <= q]
                es_residual = float(tail.mean()) if len(tail) else q * 1.15
            else:
                q = float(norm.ppf(alpha))
                es_residual = float(-norm.pdf(norm.ppf(alpha)) / alpha)
            for _, row in group.iterrows():
                var_return = q * row["daily_sigma"]
                es_return = min(es_residual * row["daily_sigma"], var_return)
                common = {
                    "asset": asset,
                    "model": model,
                    "forecast_date": row["forecast_date"],
                    "target_date": row["target_date"],
                    "confidence_level": confidence,
                    "method": "validation_empirical_residual",
                    "period": row["period"],
                }
                var_rows.append({**common, "var_return": var_return})
                es_rows.append({**common, "es_return": es_return})
                breach = int(row["realised_return"] < var_return)
                breach_rows.append(
                    {
                        "asset": asset,
                        "model": model,
                        "target_date": row["target_date"],
                        "confidence_level": confidence,
                        "method": "validation_empirical_residual",
                        "realised_return": row["realised_return"],
                        "var_return": var_return,
                        "es_return": es_return,
                        "breach": breach,
                        "breach_size": max(0.0, var_return - row["realised_return"]),
                        "period": row["period"],
                    }
                )
    breaches = pd.DataFrame(breach_rows)
    for (asset, model, confidence, method, period), group in breaches.groupby(
        ["asset", "model", "confidence_level", "method", "period"], sort=False
    ):
        if period != "test":
            continue
        alpha = 1.0 - confidence
        breach_list = group.sort_values("target_date")["breach"].astype(int).tolist()
        lr_uc, p_uc = kupiec_test(breach_list, alpha)
        lr_ind, p_ind = christoffersen_independence_test(breach_list)
        breach_dates = group.loc[group["breach"] == 1, "target_date"].tolist()
        result_rows.append(
            {
                "asset": asset,
                "model": model,
                "confidence_level": confidence,
                "method": method,
                "period": period,
                "n_obs": len(group),
                "expected_breaches": len(group) * alpha,
                "actual_breaches": int(sum(breach_list)),
                "breach_rate": float(np.mean(breach_list)),
                "kupiec_lr": lr_uc,
                "kupiec_p_value": p_uc,
                "christoffersen_lr": lr_ind,
                "christoffersen_p_value": p_ind,
                "es_tail_loss_ratio": es_tail_loss_ratio(
                    group["realised_return"], group["es_return"], group["breach"]
                ),
                "avg_breach_size": (
                    float(group.loc[group["breach"] == 1, "breach_size"].mean())
                    if sum(breach_list)
                    else 0.0
                ),
                "max_cluster_length": max_cluster_length(breach_list),
                "avg_days_between_breaches": average_days_between_breaches(breach_dates),
            }
        )
    return pd.DataFrame(var_rows), pd.DataFrame(es_rows), breaches, pd.DataFrame(result_rows)


def run_var_backtest(db_path: str | Path = DATABASE_PATH) -> dict[str, int]:
    with duckdb.connect(str(db_path)) as con:
        forecasts = con.execute("SELECT * FROM volatility_forecasts").fetchdf()
        returns = con.execute("SELECT * FROM daily_returns").fetchdf()
    for frame in [forecasts, returns]:
        for column in ["date", "forecast_date", "target_date"]:
            if column in frame.columns:
                frame[column] = pd.to_datetime(frame[column])
    var_df, es_df, breaches, results = calculate_var_es(forecasts, returns)
    with duckdb.connect(str(db_path)) as con:
        for table, frame in [
            ("var_estimates", var_df),
            ("expected_shortfall_estimates", es_df),
            ("breach_events", breaches),
            ("var_backtest_results", results),
        ]:
            con.execute(f"DELETE FROM {table}")
            con.register("_frame", frame)
            con.execute(f"INSERT INTO {table} BY NAME SELECT * FROM _frame")
            con.unregister("_frame")
        run_sql_directory(con, SQL_DIR)
    return {
        "var_rows": len(var_df),
        "es_rows": len(es_df),
        "breach_rows": len(breaches),
        "backtest_rows": len(results),
    }
