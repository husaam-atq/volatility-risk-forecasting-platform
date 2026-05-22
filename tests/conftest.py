from __future__ import annotations

import pytest

from volatility_platform.database.build_database import build_database
from volatility_platform.models.walk_forward import run_forecasting_pipeline
from volatility_platform.regimes.volatility_regimes import run_regime_detection
from volatility_platform.risk.portfolio_risk import build_portfolio_risk
from volatility_platform.risk.var import run_var_backtest
from volatility_platform.utils.performance import run_sql_benchmarks


@pytest.fixture(scope="session")
def sample_db(tmp_path_factory):
    db_path = tmp_path_factory.mktemp("db") / "market_risk.duckdb"
    build_database(db_path=db_path, use_live=False)
    return db_path


@pytest.fixture(scope="session")
def full_db(sample_db):
    run_forecasting_pipeline(sample_db)
    run_var_backtest(sample_db)
    build_portfolio_risk(sample_db)
    run_regime_detection(sample_db)
    run_sql_benchmarks(sample_db)
    return sample_db
