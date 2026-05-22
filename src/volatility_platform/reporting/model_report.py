from __future__ import annotations

import pandas as pd


def model_summary_tables(metrics: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    test = metrics[metrics["period"] == "test"].copy()
    aggregate = (
        test.groupby("model")
        .agg(
            asset_count=("asset", "nunique"),
            avg_qlike=("qlike", "mean"),
            avg_mae=("mae", "mean"),
            avg_rmse=("rmse", "mean"),
            avg_rank=("rank_qlike", "mean"),
            top_two_share=("rank_qlike", lambda s: (s <= 2).mean()),
            improvement_vs_rolling_21=("improvement_vs_rolling_21", "mean"),
            improvement_vs_ewma=("improvement_vs_ewma", "mean"),
            improvement_vs_garch=("improvement_vs_garch", "mean"),
        )
        .reset_index()
        .sort_values("avg_qlike")
    )
    asset = test.sort_values(["asset", "rank_qlike"])
    return aggregate, asset


def asset_level_model_audit(metrics: pd.DataFrame) -> pd.DataFrame:
    test = metrics[metrics["period"] == "test"].copy()
    rows = []
    for asset, group in test.groupby("asset", sort=True):
        by_model = group.set_index("model")
        best = group.sort_values("qlike").iloc[0]
        har_rank = (
            int(by_model.loc["har_rolling_update", "rank_qlike"])
            if "har_rolling_update" in by_model.index
            else pd.NA
        )
        rows.append(
            {
                "asset": asset,
                "best_model": best["model"],
                "rolling_21_qlike": by_model.loc["rolling_21", "qlike"],
                "ewma_094_qlike": by_model.loc["ewma_094", "qlike"],
                "garch_11_qlike": by_model.loc["garch_11", "qlike"],
                "best_model_qlike": best["qlike"],
                "improvement_vs_rolling_21": best["improvement_vs_rolling_21"],
                "improvement_vs_ewma": best["improvement_vs_ewma"],
                "improvement_vs_garch": best["improvement_vs_garch"],
                "har_rolling_update_rank": har_rank,
                "har_rolling_update_top_two": bool(har_rank <= 2) if pd.notna(har_rank) else False,
                "best_beats_rolling_21": bool(best["improvement_vs_rolling_21"] > 0),
                "best_beats_ewma": bool(best["improvement_vs_ewma"] > 0),
                "best_beats_garch": bool(best["improvement_vs_garch"] > 0),
            }
        )
    return pd.DataFrame(rows)


def asset_level_audit_summary(asset_audit: pd.DataFrame) -> pd.DataFrame:
    if asset_audit.empty:
        return pd.DataFrame()
    return pd.DataFrame(
        [
            {
                "metric": "median_improvement_vs_rolling_21",
                "value": asset_audit["improvement_vs_rolling_21"].median(),
            },
            {
                "metric": "mean_improvement_vs_rolling_21",
                "value": asset_audit["improvement_vs_rolling_21"].mean(),
            },
            {
                "metric": "worst_asset_improvement_vs_rolling_21",
                "value": asset_audit["improvement_vs_rolling_21"].min(),
            },
            {
                "metric": "assets_where_best_beats_rolling_21",
                "value": int(asset_audit["best_beats_rolling_21"].sum()),
            },
            {
                "metric": "assets_where_best_beats_ewma",
                "value": int(asset_audit["best_beats_ewma"].sum()),
            },
            {
                "metric": "assets_where_best_beats_garch",
                "value": int(asset_audit["best_beats_garch"].sum()),
            },
            {
                "metric": "assets_where_har_rolling_update_is_top_two",
                "value": int(asset_audit["har_rolling_update_top_two"].sum()),
            },
        ]
    )
