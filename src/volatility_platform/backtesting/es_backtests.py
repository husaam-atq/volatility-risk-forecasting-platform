from __future__ import annotations

import numpy as np
import pandas as pd


def es_tail_loss_ratio(realised_returns, es_returns, breaches) -> float:
    data = pd.DataFrame(
        {
            "realised": realised_returns,
            "es": es_returns,
            "breach": breaches,
        }
    )
    tail = data[data["breach"] == 1]
    if tail.empty or (-tail["es"]).mean() == 0:
        return float("nan")
    return float((-tail["realised"]).mean() / (-tail["es"]).mean())


def es_exceedance_severity(realised_returns, es_returns, breaches) -> float:
    data = pd.DataFrame({"realised": realised_returns, "es": es_returns, "breach": breaches})
    tail = data[data["breach"] == 1]
    if tail.empty:
        return float("nan")
    return float(np.mean(np.maximum(0.0, tail["es"] - tail["realised"])))
