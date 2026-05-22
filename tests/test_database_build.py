import duckdb


def test_database_build_tables(sample_db):
    with duckdb.connect(str(sample_db), read_only=True) as con:
        tables = {row[0] for row in con.execute("SHOW TABLES").fetchall()}
        assert "clean_prices" in tables
        assert "daily_returns" in tables
        assert con.execute("SELECT COUNT(*) FROM clean_prices").fetchone()[0] > 0
