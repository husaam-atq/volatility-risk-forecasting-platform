import duckdb
import pytest


@pytest.mark.parametrize("table", ["raw_prices", "clean_prices"])
def test_price_tables_have_no_duplicate_asset_dates(sample_db, table):
    with duckdb.connect(str(sample_db), read_only=True) as con:
        duplicates = con.execute(f"""
            SELECT COUNT(*)
            FROM (
                SELECT asset, date, COUNT(*) AS row_count
                FROM {table}
                GROUP BY asset, date
                HAVING COUNT(*) > 1
            )
            """).fetchone()[0]
    assert duplicates == 0


@pytest.mark.parametrize("column", ["open", "high", "low", "close", "adj_close"])
def test_clean_prices_are_positive(sample_db, column):
    with duckdb.connect(str(sample_db), read_only=True) as con:
        invalid = con.execute(f"SELECT COUNT(*) FROM clean_prices WHERE {column} <= 0").fetchone()[
            0
        ]
    assert invalid == 0


def test_fixed_universe_has_expected_assets(sample_db):
    expected = {"SPY", "QQQ", "IWM", "TLT", "GLD", "USO", "AAPL", "MSFT", "NVDA", "JPM"}
    with duckdb.connect(str(sample_db), read_only=True) as con:
        assets = {row[0] for row in con.execute("SELECT asset FROM asset_universe").fetchall()}
    assert assets == expected


def test_raw_price_source_is_recorded(sample_db):
    with duckdb.connect(str(sample_db), read_only=True) as con:
        sources = {
            row[0] for row in con.execute("SELECT DISTINCT source FROM raw_prices").fetchall()
        }
    assert sources
    assert all(source for source in sources)


def test_data_quality_checks_all_pass(sample_db):
    with duckdb.connect(str(sample_db), read_only=True) as con:
        failures = con.execute(
            "SELECT COUNT(*) FROM data_quality_checks WHERE status <> 'pass'"
        ).fetchone()[0]
    assert failures == 0
