import pytest

from volatility_platform.backtesting.forecast_metrics import (
    directional_accuracy,
    improvement,
    mae,
    mape,
    qlike,
    rmse,
)


def test_forecast_metrics_positive():
    y = [0.1, 0.2, 0.3]
    p = [0.11, 0.19, 0.28]
    assert rmse(y, p) > 0
    assert mae(y, p) > 0
    assert qlike(y, p) < 1


@pytest.mark.parametrize(
    ("base", "candidate", "expected"),
    [(10.0, 8.0, 0.2), (10.0, 12.0, -0.2), (-10.0, -9.0, -0.1)],
)
def test_improvement_percentage_known_cases(base, candidate, expected):
    assert improvement(base, candidate) == pytest.approx(expected)


def test_qlike_prefers_accurate_volatility_forecast():
    realised = [0.10, 0.15, 0.20]
    assert qlike(realised, realised) == pytest.approx(0.0)
    assert qlike(realised, realised) < qlike(realised, [0.30, 0.30, 0.30])


def test_qlike_is_scale_consistent_for_volatility_inputs():
    realised = [0.10, 0.20]
    forecast = [0.20, 0.10]
    assert qlike(realised, forecast) == qlike(
        [x * 10 for x in realised], [x * 10 for x in forecast]
    )


def test_mape_handles_nonzero_volatility():
    assert mape([0.1, 0.2], [0.11, 0.18]) == pytest.approx(0.1)


def test_directional_accuracy_detects_matching_changes():
    assert directional_accuracy([0.1, 0.2, 0.15], [0.09, 0.22, 0.10]) == 1.0
