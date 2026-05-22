from __future__ import annotations

import pandas as pd


def to_timestamp(value) -> pd.Timestamp:
    return pd.to_datetime(value).normalize()
