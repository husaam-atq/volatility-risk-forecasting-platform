import duckdb


def test_core_views_exist(full_db):
    with duckdb.connect(str(full_db), read_only=True) as con:
        assert con.execute("SELECT COUNT(*) FROM v_dashboard_overview").fetchone()[0] == 1
        assert con.execute("SELECT COUNT(*) FROM v_model_comparison").fetchone()[0] > 0
