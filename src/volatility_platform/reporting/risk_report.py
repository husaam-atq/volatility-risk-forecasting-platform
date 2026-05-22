from __future__ import annotations

import pandas as pd


def risk_summary(var_results: pd.DataFrame) -> pd.DataFrame:
    if var_results.empty:
        return pd.DataFrame()
    return (
        var_results.groupby(["model", "confidence_level"])
        .agg(
            avg_breach_rate=("breach_rate", "mean"),
            kupiec_not_rejected=("kupiec_p_value", lambda s: (s > 0.05).mean()),
            christoffersen_not_rejected=("christoffersen_p_value", lambda s: (s > 0.05).mean()),
            avg_es_tail_loss_ratio=("es_tail_loss_ratio", "mean"),
            avg_max_cluster=("max_cluster_length", "mean"),
        )
        .reset_index()
    )
