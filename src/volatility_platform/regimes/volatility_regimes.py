from __future__ import annotations

from pathlib import Path

import duckdb
import numpy as np
import pandas as pd

from volatility_platform.config import DATABASE_PATH, SQL_DIR
from volatility_platform.database.run_sql import run_sql_directory


def detect_volatility_regimes(realised: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    rv = realised[(realised["estimator"] == "close_to_close") & (realised["window"] == 21)][
        ["asset", "date", "realised_vol"]
    ].copy()
    rows = []
    metrics = []
    for asset, group in rv.sort_values(["asset", "date"]).groupby("asset", sort=False):
        group = group.copy()
        rolling = group["realised_vol"].rolling(252, min_periods=63)
        q50 = rolling.quantile(0.50).shift(1)
        q80 = rolling.quantile(0.80).shift(1)
        mean = rolling.mean().shift(1)
        std = rolling.std().shift(1)
        global_top = group["realised_vol"].quantile(0.90)
        group["percentile_score"] = group["realised_vol"].rank(pct=True)
        group["z_score"] = (group["realised_vol"] - mean) / std.replace(0, np.nan)
        group["regime"] = np.where(
            group["realised_vol"] >= q80,
            "high",
            np.where(group["realised_vol"] >= q50, "medium", "low"),
        )
        group["regime"] = group["regime"].fillna("low")
        group["is_top_decile"] = (group["realised_vol"] >= global_top).astype(int)
        group["high_vol_flag"] = (group["regime"] == "high").astype(int)
        top = group[group["is_top_decile"] == 1]
        high = group[group["high_vol_flag"] == 1]
        top_capture = float(top["high_vol_flag"].mean()) if not top.empty else float("nan")
        false_rate = float((high["is_top_decile"] == 0).mean()) if not high.empty else float("nan")
        transitions = int((group["regime"] != group["regime"].shift(1)).sum() - 1)
        run_lengths = (
            group.assign(run=(group["regime"] != group["regime"].shift()).cumsum())
            .groupby("run")["date"]
            .count()
        )
        metrics.append(
            {
                "asset": asset,
                "top_decile_capture": top_capture,
                "false_high_flag_rate": false_rate,
                "high_regime_share": float(group["high_vol_flag"].mean()),
                "median_regime_days": float(run_lengths.median()),
                "transition_count": transitions,
            }
        )
        rows.append(group)
    return pd.concat(rows, ignore_index=True), pd.DataFrame(metrics)


def run_regime_detection(db_path: str | Path = DATABASE_PATH) -> dict[str, int]:
    with duckdb.connect(str(db_path)) as con:
        realised = con.execute("SELECT * FROM realised_volatility").fetchdf()
    realised["date"] = pd.to_datetime(realised["date"])
    labels, metrics = detect_volatility_regimes(realised)
    with duckdb.connect(str(db_path)) as con:
        con.execute("DELETE FROM regime_labels")
        con.register("_labels", labels)
        con.execute("INSERT INTO regime_labels BY NAME SELECT * FROM _labels")
        con.unregister("_labels")
        con.execute("DELETE FROM regime_metrics")
        con.register("_metrics", metrics)
        con.execute("INSERT INTO regime_metrics BY NAME SELECT * FROM _metrics")
        con.unregister("_metrics")
        run_sql_directory(con, SQL_DIR)
    return {"label_rows": len(labels), "metric_rows": len(metrics)}
