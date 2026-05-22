from __future__ import annotations

from scipy.stats import norm, t


def gaussian_es(alpha: float, sigma: float) -> float:
    return float(-sigma * norm.pdf(norm.ppf(alpha)) / alpha)


def student_t_es(alpha: float, sigma: float, df: float = 7.0) -> float:
    q = t.ppf(alpha, df)
    scale = (df + q**2) / (df - 1)
    return float(-sigma * scale * t.pdf(q, df) / alpha)
