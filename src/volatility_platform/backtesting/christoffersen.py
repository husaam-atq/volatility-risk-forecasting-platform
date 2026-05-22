from __future__ import annotations

import math

import numpy as np
from scipy.stats import chi2


def christoffersen_independence_test(breaches) -> tuple[float, float]:
    b = np.asarray(breaches, dtype=int)
    if len(b) < 3:
        return float("nan"), float("nan")
    n00 = n01 = n10 = n11 = 0
    for prev, curr in zip(b[:-1], b[1:], strict=False):
        if prev == 0 and curr == 0:
            n00 += 1
        elif prev == 0 and curr == 1:
            n01 += 1
        elif prev == 1 and curr == 0:
            n10 += 1
        else:
            n11 += 1

    def safe_log_prob(k, n, p):
        if n == 0 or k == 0:
            return 0.0
        return k * math.log(min(max(p, 1e-12), 1 - 1e-12))

    pi = (n01 + n11) / max(n00 + n01 + n10 + n11, 1)
    pi0 = n01 / max(n00 + n01, 1)
    pi1 = n11 / max(n10 + n11, 1)
    ll_null = safe_log_prob(n00 + n10, n00 + n01 + n10 + n11, 1 - pi) + safe_log_prob(
        n01 + n11, n00 + n01 + n10 + n11, pi
    )
    ll_alt = (
        safe_log_prob(n00, n00 + n01, 1 - pi0)
        + safe_log_prob(n01, n00 + n01, pi0)
        + safe_log_prob(n10, n10 + n11, 1 - pi1)
        + safe_log_prob(n11, n10 + n11, pi1)
    )
    lr = max(0.0, -2.0 * (ll_null - ll_alt))
    return float(lr), float(1.0 - chi2.cdf(lr, df=1))
