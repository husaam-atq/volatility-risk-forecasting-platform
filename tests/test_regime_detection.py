import duckdb


def test_regime_labels_valid(full_db):
    with duckdb.connect(str(full_db), read_only=True) as con:
        labels = (
            con.execute("SELECT DISTINCT regime FROM regime_labels").fetchdf()["regime"].tolist()
        )
        assert set(labels).issubset({"low", "medium", "high"})
        assert con.execute("SELECT AVG(top_decile_capture) FROM regime_metrics").fetchone()[0] >= 0
