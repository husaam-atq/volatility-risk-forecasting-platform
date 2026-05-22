import duckdb
import pandas as pd

from volatility_platform.config import TRAIN_END, VALIDATION_END
from volatility_platform.models.walk_forward import build_model_frame


def test_forecast_dates_precede_targets(full_db):
    with duckdb.connect(str(full_db), read_only=True) as con:
        leaking_rows = con.execute(
            "SELECT COUNT(*) FROM volatility_forecasts WHERE forecast_date >= target_date"
        ).fetchone()[0]
    assert leaking_rows == 0


def test_forecasts_are_validation_or_test_only(full_db):
    with duckdb.connect(str(full_db), read_only=True) as con:
        periods = {
            row[0]
            for row in con.execute("SELECT DISTINCT period FROM volatility_forecasts").fetchall()
        }
    assert periods == {"validation", "test"}


def test_model_metrics_exclude_training_period(full_db):
    with duckdb.connect(str(full_db), read_only=True) as con:
        train_rows = con.execute(
            "SELECT COUNT(*) FROM model_metrics WHERE period = 'train'"
        ).fetchone()[0]
    assert train_rows == 0


def test_walk_forward_period_boundaries(sample_db):
    with duckdb.connect(str(sample_db), read_only=True) as con:
        features = con.execute("SELECT * FROM volatility_features").fetchdf()
        realised = con.execute("SELECT * FROM realised_volatility").fetchdf()
    features["date"] = pd.to_datetime(features["date"])
    realised["date"] = pd.to_datetime(realised["date"])
    frame = build_model_frame(features, realised)
    train_end = pd.Timestamp(TRAIN_END)
    validation_end = pd.Timestamp(VALIDATION_END)
    assert frame.loc[frame["period"] == "train", "target_date"].max() <= train_end
    assert frame.loc[frame["period"] == "validation", "target_date"].min() > train_end
    assert frame.loc[frame["period"] == "validation", "target_date"].max() <= validation_end
    assert frame.loc[frame["period"] == "test", "target_date"].min() > validation_end


def test_model_frame_target_is_next_observation(sample_db):
    with duckdb.connect(str(sample_db), read_only=True) as con:
        features = con.execute("SELECT * FROM volatility_features").fetchdf()
        realised = con.execute("SELECT * FROM realised_volatility").fetchdf()
    features["date"] = pd.to_datetime(features["date"])
    realised["date"] = pd.to_datetime(realised["date"])
    frame = build_model_frame(features, realised)
    assert (pd.to_datetime(frame["date"]) < pd.to_datetime(frame["target_date"])).all()


def test_no_duplicate_forecast_keys(full_db):
    with duckdb.connect(str(full_db), read_only=True) as con:
        duplicates = con.execute("""
            SELECT COUNT(*)
            FROM (
                SELECT asset, target_date, model, horizon, COUNT(*) AS row_count
                FROM volatility_forecasts
                GROUP BY asset, target_date, model, horizon
                HAVING COUNT(*) > 1
            )
            """).fetchone()[0]
    assert duplicates == 0
