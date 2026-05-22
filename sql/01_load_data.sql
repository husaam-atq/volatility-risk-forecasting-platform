-- Data is loaded through Python using registered pandas DataFrames so that
-- duplicate keys, non-positive prices and coverage checks can be validated
-- before insertion. The schema keeps raw and cleaned prices separate.

SELECT 'raw_prices and clean_prices are populated by src/volatility_platform/database/build_database.py' AS note;
