# Data

`sample_prices.csv` is an offline reproducibility dataset covering the fixed default universe from 2015-01-02 to 2026-05-21.

Live data can be downloaded with `examples/build_database.py --live` when `yfinance` is available. Downloaded files are cached under `data/raw/` and are excluded from version control to keep the repository light.

Cleaning rules:

- Use adjusted close for return calculations.
- Remove duplicate `(asset, date)` rows.
- Drop rows with non-positive OHLC prices.
- Align assets on common business dates for portfolio-level analytics.
- Report missing values, duplicate keys, non-positive prices and extreme returns.
