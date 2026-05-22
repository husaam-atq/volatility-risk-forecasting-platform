from __future__ import annotations

import pandas as pd


def add_regime_feature_flags(features: pd.DataFrame) -> pd.DataFrame:
    data = features.copy()
    data["high_recent_vol"] = (
        data["rv_21"] > data.groupby("asset")["rv_21"].transform("median")
    ).astype(int)
    return data
