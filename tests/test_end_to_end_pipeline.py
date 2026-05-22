import importlib.util

import duckdb


def test_end_to_end_pipeline_outputs(full_db):
    with duckdb.connect(str(full_db), read_only=True) as con:
        assert con.execute("SELECT COUNT(*) FROM model_metrics").fetchone()[0] > 0
        assert con.execute("SELECT COUNT(*) FROM var_backtest_results").fetchone()[0] > 0
        assert con.execute("SELECT COUNT(*) FROM sql_query_benchmarks").fetchone()[0] > 0
    assert importlib.util.find_spec("app.streamlit_app") is not None
