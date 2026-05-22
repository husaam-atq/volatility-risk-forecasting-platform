from __future__ import annotations

import pandas as pd


def simple_change_points(series: pd.Series, z_threshold: float = 2.5) -> pd.Series:
    z = (series - series.rolling(126, min_periods=30).mean()) / series.rolling(
        126, min_periods=30
    ).std()
    return (z.abs() >= z_threshold).fillna(False)
