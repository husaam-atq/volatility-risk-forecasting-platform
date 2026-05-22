from __future__ import annotations

import math

from scipy.stats import chi2


def kupiec_test(breaches, alpha: float) -> tuple[float, float]:
    x = int(sum(breaches))
    n = len(breaches)
    if n == 0:
        return float("nan"), float("nan")
    phat = min(max(x / n, 1e-12), 1 - 1e-12)
    alpha = min(max(alpha, 1e-12), 1 - 1e-12)
    ll_null = (n - x) * math.log(1 - alpha) + x * math.log(alpha)
    ll_alt = (n - x) * math.log(1 - phat) + x * math.log(phat)
    lr = max(0.0, -2.0 * (ll_null - ll_alt))
    return float(lr), float(1.0 - chi2.cdf(lr, df=1))
