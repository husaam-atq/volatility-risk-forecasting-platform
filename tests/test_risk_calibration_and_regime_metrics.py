import numpy as np
import pandas as pd
import pytest

from volatility_platform.regimes.volatility_regimes import classification_metrics
from volatility_platform.risk.var import calculate_var_es, student_t_residual_quantile


def test_student_t_residual_quantile_is_left_tail_and_es_is_conservative():
    residuals = pd.Series(np.linspace(-2.5, 2.5, 200))
    quantile, es_residual = student_t_residual_quantile(0.05, residuals, df=5.0)
    assert quantile < 0
    assert es_residual <= quantile


def test_calculate_var_es_outputs_expected_period_backtests():
    dates = pd.bdate_range("2020-01-02", periods=140)
    forecasts = pd.DataFrame(
        {
            "asset": "SPY",
            "model": "unit_model",
            "forecast_date": dates,
            "target_date": dates + pd.offsets.BDay(1),
            "forecast_vol": 0.20,
            "period": ["validation"] * 80 + ["test"] * 60,
        }
    )
    returns = pd.DataFrame(
        {
            "asset": "SPY",
            "date": dates + pd.offsets.BDay(1),
            "simple_return": np.r_[np.linspace(-0.02, 0.02, 80), np.linspace(-0.03, 0.03, 60)],
        }
    )
    var_df, es_df, breaches, results = calculate_var_es(forecasts, returns)
    assert not var_df.empty
    assert not es_df.empty
    assert set(breaches["method"]) == {"validation_student_t_residual_df5"}
    assert set(results["period"]) == {"test"}


def test_var_breach_logic_marks_losses_beyond_var():
    dates = pd.bdate_range("2020-01-02", periods=90)
    forecasts = pd.DataFrame(
        {
            "asset": "SPY",
            "model": "unit_model",
            "forecast_date": dates,
            "target_date": dates + pd.offsets.BDay(1),
            "forecast_vol": 0.10,
            "period": ["validation"] * 60 + ["test"] * 30,
        }
    )
    returns = pd.DataFrame(
        {
            "asset": "SPY",
            "date": dates + pd.offsets.BDay(1),
            "simple_return": [-0.005] * 60 + [-0.20] + [0.001] * 29,
        }
    )
    _, _, breaches, _ = calculate_var_es(forecasts, returns, confidence_levels=[0.95])
    test_breaches = breaches[breaches["period"] == "test"]
    assert test_breaches["breach"].sum() >= 1


def test_regime_classification_metrics_known_case():
    scores = classification_metrics(
        pd.Series([1, 1, 0, 0, 1, 0]),
        pd.Series([1, 0, 1, 0, 1, 0]),
    )
    assert scores["precision"] == pytest.approx(2 / 3)
    assert scores["recall"] == pytest.approx(2 / 3)
    assert scores["f1_score"] == pytest.approx(2 / 3)
    assert scores["false_positive_rate"] == pytest.approx(1 / 3)
    assert scores["false_high_flag_rate"] == pytest.approx(1 / 3)
