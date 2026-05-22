# SQL Performance Report

## Summary

- Full database rebuild time: 1.253651 seconds.
- Database file size: 57.01 MB.
- Total persisted analytical rows: 2,873,762.
- Largest benchmarked scale: 2,873,756 rows.

## Row Counts

| Table | Rows |
|---|---:|
| asset_universe | 10 |
| raw_prices | 28,620 |
| clean_prices | 28,620 |
| daily_returns | 28,610 |
| realised_volatility | 567,570 |
| volatility_features | 27,360 |
| volatility_forecasts | 304,760 |
| model_metrics | 380 |
| var_estimates | 609,520 |
| expected_shortfall_estimates | 609,520 |
| breach_events | 609,520 |
| var_backtest_results | 380 |
| regime_labels | 28,410 |
| portfolio_risk | 30,476 |
| sql_query_benchmarks | 6 |

## Query Benchmarks

| Query | Mean ms | p50 ms | p95 ms | Rows returned | Benchmark rows |
|---|---:|---:|---:|---:|---:|
| dashboard_overview | 8.048 | 7.954 | 8.677 | 1 | 2,873,756 |
| model_comparison | 2.979 | 2.827 | 4.019 | 19 | 2,873,756 |
| var_breach_summary | 0.665 | 0.635 | 0.837 | 380 | 2,873,756 |
| asset_risk_summary | 14.002 | 13.339 | 17.672 | 10 | 2,873,756 |
| portfolio_risk_summary | 2.354 | 2.262 | 2.972 | 19 | 2,873,756 |
| one_million_row_synthetic_scale | 6.202 | 6.005 | 6.983 | 10 | 1,144,800 |

## Interpretation

DuckDB is used as the analytical layer for joins, validation views, dashboard summaries and benchmark queries.
The synthetic scale query expands the clean price table to confirm that the SQL layer remains responsive above one million rows.
Reported timings are hardware dependent and should be regenerated on any target machine before quoting exact numbers.

## Limitations

Benchmarks are local single-user timings and do not represent concurrent production traffic.
The scale test stresses relational scans and aggregations; it is not a full simulation of every downstream model table.
Memory usage is not forced or pinned, so operating-system cache effects can improve repeated query timings.
