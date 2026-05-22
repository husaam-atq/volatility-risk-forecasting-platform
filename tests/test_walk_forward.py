import duckdb


def test_walk_forward_forecasts_no_leakage(full_db):
    with duckdb.connect(str(full_db), read_only=True) as con:
        bad = con.execute(
            "SELECT COUNT(*) FROM volatility_forecasts WHERE forecast_date >= target_date"
        ).fetchone()[0]
        assert bad == 0
        assert (
            con.execute(
                "SELECT COUNT(*) FROM volatility_forecasts WHERE forecast_vol <= 0"
            ).fetchone()[0]
            == 0
        )
