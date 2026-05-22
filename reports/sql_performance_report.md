# SQL Performance Report

## Summary

- Full database rebuild time: 1.334048 seconds.
- Database file size: 49.26 MB.
- Total persisted analytical rows: 2,512,791.
- Largest benchmarked scale: 2,512,785 rows.

## Row Counts

| Table | Rows |
|---|---:|
| asset_universe | 10 |
| raw_prices | 29,700 |
| clean_prices | 29,700 |
| daily_returns | 29,690 |
| realised_volatility | 589,170 |
| volatility_features | 29,070 |
| volatility_forecasts | 250,050 |
| model_metrics | 300 |
| var_estimates | 500,100 |
| expected_shortfall_estimates | 500,100 |
| breach_events | 500,100 |
| var_backtest_results | 300 |
| regime_labels | 29,490 |
| portfolio_risk | 25,005 |
| sql_query_benchmarks | 6 |

## Query Benchmarks

| Query | Mean ms | p50 ms | p95 ms | Rows returned | Benchmark rows |
|---|---:|---:|---:|---:|---:|
| dashboard_overview | 7.888 | 7.918 | 8.206 | 1 | 2,512,785 |
| model_comparison | 2.792 | 2.816 | 3.145 | 15 | 2,512,785 |
| var_breach_summary | 0.586 | 0.564 | 0.732 | 300 | 2,512,785 |
| asset_risk_summary | 14.100 | 14.149 | 15.646 | 10 | 2,512,785 |
| portfolio_risk_summary | 1.983 | 1.968 | 2.258 | 15 | 2,512,785 |
| one_million_row_synthetic_scale | 5.874 | 5.745 | 6.222 | 10 | 1,188,000 |

## Interpretation

DuckDB is used as the analytical layer for joins, validation views, dashboard summaries and benchmark queries.
The synthetic scale query expands the clean price table to confirm that the SQL layer remains responsive above one million rows.
Reported timings are hardware dependent and should be regenerated on any target machine before quoting exact numbers.

## Limitations

Benchmarks are local single-user timings and do not represent concurrent production traffic.
The scale test stresses relational scans and aggregations; it is not a full simulation of every downstream model table.
Memory usage is not forced or pinned, so operating-system cache effects can improve repeated query timings.
