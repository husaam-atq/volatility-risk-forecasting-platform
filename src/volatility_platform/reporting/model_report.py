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
