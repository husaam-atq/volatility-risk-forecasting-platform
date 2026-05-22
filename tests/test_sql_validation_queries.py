from volatility_platform.database.validation import run_validation_queries


def test_sql_validation_queries_pass(full_db):
    result = run_validation_queries(full_db)
    assert (result["status"] == "pass").all()
