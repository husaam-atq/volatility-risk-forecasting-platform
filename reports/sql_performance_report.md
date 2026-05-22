# SQL Performance Report

## Summary

- Full database rebuild time: 1.368148 seconds.
- Database file size: 57.26 MB.
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
| dashboard_overview | 8.153 | 8.072 | 8.910 | 1 | 2,873,756 |
| model_comparison | 3.239 | 3.137 | 3.832 | 19 | 2,873,756 |
| var_breach_summary | 0.717 | 0.687 | 0.887 | 380 | 2,873,756 |
| asset_risk_summary | 14.343 | 13.856 | 16.138 | 10 | 2,873,756 |
| portfolio_risk_summary | 2.474 | 2.345 | 3.131 | 19 | 2,873,756 |
| one_million_row_synthetic_scale | 6.264 | 6.231 | 6.534 | 10 | 1,144,800 |

## Interpretation

DuckDB is used as the analytical layer for joins, validation views, dashboard summaries and benchmark queries.
The synthetic scale query expands the clean price table to confirm that the SQL layer remains responsive above one million rows.
Reported timings are hardware dependent and should be regenerated on any target machine before quoting exact numbers.

## Limitations

Benchmarks are local single-user timings and do not represent concurrent production traffic.
The scale test stresses relational scans and aggregations; it is not a full simulation of every downstream model table.
Memory usage is not forced or pinned, so operating-system cache effects can improve repeated query timings.
