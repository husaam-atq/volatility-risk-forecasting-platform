from __future__ import annotations

import numpy as np


def max_cluster_length(breaches) -> int:
    max_len = current = 0
    for breach in breaches:
        if int(breach) == 1:
            current += 1
            max_len = max(max_len, current)
        else:
            current = 0
    return int(max_len)


def average_days_between_breaches(breach_dates) -> float:
    dates = np.array(breach_dates, dtype="datetime64[D]")
    if len(dates) < 2:
        return float("nan")
    return float(np.diff(dates).astype("timedelta64[D]").astype(int).mean())
