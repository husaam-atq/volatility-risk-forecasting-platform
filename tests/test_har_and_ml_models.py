import numpy as np
import pandas as pd

from volatility_platform.config import TRAIN_END, VALIDATION_END
from volatility_platform.features.lagged_features import feature_columns
from volatility_platform.models.har_models import har_forecasts
from volatility_platform.models.ml_models import QuantileClipper, ml_forecasts


def _synthetic_model_frame(n_rows: int = 1200) -> pd.DataFrame:
    dates = pd.bdate_range("2018-01-02", periods=n_rows)
    trend = np.linspace(0.0, 1.0, n_rows)
    base_vol = 0.12 + 0.04 * np.sin(np.linspace(0.0, 18.0, n_rows)) + 0.03 * trend
    frame = pd.DataFrame(
        {
            "asset": "SPY",
            "date": dates,
            "target_date": dates + pd.offsets.BDay(1),
            "realised_vol": np.clip(
                base_vol + 0.01 * np.cos(np.linspace(0.0, 9.0, n_rows)), 0.02, 1.0
            ),
        }
    )
    for column in feature_columns():
        if column.startswith("return"):
            frame[column] = 0.002 * np.sin(np.linspace(0.0, 6.0, n_rows))
        elif column.startswith("abs_return"):
            frame[column] = 0.01 + 0.001 * np.cos(np.linspace(0.0, 5.0, n_rows))
        elif column == "drawdown_63":
            frame[column] = -0.08 * trend
        elif column in {"skew_63", "kurt_63"}:
            frame[column] = 0.1 * np.sin(np.linspace(0.0, 3.0, n_rows))
        else:
            frame[column] = np.clip(base_vol * (1.0 + 0.05 * np.sin(trend * 8.0)), 0.02, 1.0)
    frame["period"] = np.where(
        frame["target_date"] <= pd.Timestamp(TRAIN_END),
        "train",
        np.where(frame["target_date"] <= pd.Timestamp(VALIDATION_END), "validation", "test"),
    )
    return frame


def test_har_forecasts_emit_expected_models_and_positive_values():
    forecasts = har_forecasts(_synthetic_model_frame())
    assert set(forecasts["model"]) == {
        "har_rv_log_ridge",
        "har_rv_market_log_ridge",
        "har_rv_market_huber",
    }
    assert (forecasts["forecast_vol"] > 0).all()
    assert set(forecasts["period"]) == {"validation", "test"}


def test_quantile_clipper_uses_training_bounds():
    clipper = QuantileClipper(lower=0.25, upper=0.75)
    clipper.fit(np.array([[0.0, 10.0], [1.0, 11.0], [2.0, 12.0], [3.0, 13.0]]))
    transformed = clipper.transform(np.array([[-100.0, 100.0]]))
    assert transformed[0, 0] >= clipper.lower_bounds_[0]
    assert transformed[0, 1] <= clipper.upper_bounds_[1]


def test_ml_forecasts_are_positive_and_skip_training_output():
    forecasts = ml_forecasts(_synthetic_model_frame())
    assert {"random_forest", "hist_gradient_boosting"}.issubset(set(forecasts["model"]))
    assert (forecasts["forecast_vol"] > 0).all()
    assert "train" not in set(forecasts["period"])
