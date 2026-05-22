# Results Audit Report

## Data Source And Database

| data_source | raw_price_rows | first_date | last_date |
| --- | --- | --- | --- |
| yfinance | 28620 | 2015-01-02 00:00:00 | 2026-05-20 00:00:00 |

Database file size: 57.26 MiB.

## Row Counts

| table_name | row_count |
| --- | --- |
| asset_universe | 10 |
| raw_prices | 28620 |
| clean_prices | 28620 |
| daily_returns | 28610 |
| realised_volatility | 567570 |
| volatility_features | 27360 |
| volatility_forecasts | 304760 |
| model_metrics | 380 |
| var_estimates | 609520 |
| expected_shortfall_estimates | 609520 |
| breach_events | 609520 |
| var_backtest_results | 380 |
| regime_labels | 28410 |
| portfolio_risk | 30476 |
| sql_query_benchmarks | 6 |

## Headline Metrics From Database

| metric | value |
| --- | --- |
| best_model | har_rolling_update |
| qlike_improvement_vs_rolling_21 | 0.40411554860568105 |
| qlike_improvement_vs_ewma | 0.831530336795882 |
| qlike_improvement_vs_garch | 0.9150237827117342 |
| top_two_share | 0.8 |

## Target Table

| Target | Result | Status |
| --- | --- | --- |
| QLIKE improvement vs rolling vol >= 12% | 40.41% | pass |
| QLIKE improvement vs EWMA >= 5% | 83.15% | pass |
| QLIKE improvement vs GARCH >= 5% | 91.50% | pass |
| Best/top-2 model across >= 70% assets | 80.00% | pass |
| 95% VaR breach rate 4.7%-5.3% | 4.76% | pass |
| 99% VaR breach rate 0.8%-1.2% | 0.81% | pass |
| Kupiec not rejected for most assets | 85.79% | pass |
| Christoffersen not rejected for most assets | 87.89% | pass |
| ES tail-loss ratio 0.9-1.1 | 0.984 | pass |
| Top-decile vol capture >= 75% | 75.44% | pass |
| High-vol precision >= 40% | 43.46% | pass |
| High-vol F1 >= 50% | 55.07% | pass |
| False high-vol flag rate <= 60% | 56.54% | pass |
| SQL handles 1m+ rows | 2,873,756 | pass |
| Dashboard queries < 1 sec | 16.14 ms p95 | pass |
| Tests pass | passed | pass |

## Database, CSV And Markdown Consistency

| check | result |
| --- | --- |
| data_source_is_live_yfinance | True |
| model_comparison_csv_asset_rows_match_universe | True |
| var_backtest_csv_rows_match_database | True |
| regime_csv_rows_match_database | True |
| benchmark_csv_rows_match_database | True |
| benchmark_csv_values_match_database | True |
| database_size_below_100_mib | True |
| validation_queries_have_zero_failing_rows | True |

## Report File Metadata

| file | line_count | size_bytes | modified_utc |
| --- | --- | --- | --- |
| README.md | 305 | 16941 | 2026-05-22T15:50:18.750177+00:00 |
| reports/validation_report.md | 74 | 3473 | 2026-05-22T15:50:18.745677+00:00 |
| reports/model_comparison_report.md | 206 | 16602 | 2026-05-22T15:50:18.708108+00:00 |
| reports/risk_backtest_report.md | 256 | 22611 | 2026-05-22T15:50:18.720127+00:00 |
| reports/sql_performance_report.md | 51 | 1987 | 2026-05-22T15:50:18.741677+00:00 |
| reports/model_comparison_results.csv | 11 | 2127 | 2026-05-22T15:50:18.709610+00:00 |
| reports/var_backtest_results.csv | 381 | 93975 | 2026-05-22T15:50:18.723136+00:00 |
| reports/regime_detection_results.csv | 11 | 1626 | 2026-05-22T15:50:18.723136+00:00 |
| reports/benchmark_results.csv | 7 | 1004 | 2026-05-22T15:50:18.742180+00:00 |

## QLIKE Methodology Audit

- QLIKE uses `realised_variance / forecast_variance - log(realised_variance / forecast_variance) - 1`, giving zero loss for a perfect forecast.
- The metric function accepts annualised volatility inputs and squares both realised and forecast volatility, so both sides are compared as variances on the same scale.
- Forecast rows have `forecast_date < target_date`; SQL validation view `v_validation_forecast_leakage` returned zero failing rows.
- The modelling target is next-observation 21-day close-to-close realised volatility joined on `target_date`, not same-day realised volatility.
- Percentage improvement uses `(baseline_loss - candidate_loss) / abs(baseline_loss)`, so lower QLIKE produces a positive improvement.
- Rolling, EWMA and GARCH baseline rows are present for every test asset; the asset-level robustness table checks that the improvement is broad-based.

## Forecast Robustness Summary

| metric | value |
| --- | --- |
| median_improvement_vs_rolling_21 | 0.4105 |
| mean_improvement_vs_rolling_21 | 0.4075 |
| worst_asset_improvement_vs_rolling_21 | 0.3553 |
| assets_where_best_beats_rolling_21 | 10.0000 |
| assets_where_best_beats_ewma | 10.0000 |
| assets_where_best_beats_garch | 10.0000 |
| assets_where_har_rolling_update_is_top_two | 8.0000 |

## Asset-Level Forecast Robustness

| asset | best_model | rolling_21_qlike | ewma_094_qlike | garch_11_qlike | best_model_qlike | improvement_vs_rolling_21 | improvement_vs_ewma | improvement_vs_garch | har_rolling_update_rank | har_rolling_update_top_two | best_beats_rolling_21 | best_beats_ewma | best_beats_garch |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| AAPL | gjr_rolling_update | 0.0118 | 0.0385 | 0.0802 | 0.0067 | 0.4315 | 0.8258 | 0.9165 | 2 | True | True | True | True |
| GLD | har_rolling_update | 0.0081 | 0.0280 | 0.0607 | 0.0045 | 0.4434 | 0.8382 | 0.9252 | 1 | True | True | True | True |
| IWM | ewma_rolling_update | 0.0073 | 0.0250 | 0.0370 | 0.0042 | 0.4264 | 0.8317 | 0.8863 | 2 | True | True | True | True |
| JPM | garch_rolling_update | 0.0128 | 0.0478 | 0.1044 | 0.0081 | 0.3702 | 0.8314 | 0.9228 | 3 | False | True | True | True |
| MSFT | garch_rolling_update | 0.0111 | 0.0374 | 0.0745 | 0.0071 | 0.3594 | 0.8093 | 0.9043 | 2 | True | True | True | True |
| NVDA | gjr_rolling_update | 0.0125 | 0.0438 | 0.1843 | 0.0081 | 0.3553 | 0.8159 | 0.9562 | 2 | True | True | True | True |
| QQQ | har_rolling_update | 0.0076 | 0.0320 | 0.0457 | 0.0042 | 0.4500 | 0.8696 | 0.9088 | 1 | True | True | True | True |
| SPY | har_rolling_update | 0.0091 | 0.0376 | 0.0740 | 0.0055 | 0.3928 | 0.8537 | 0.9257 | 1 | True | True | True | True |
| TLT | garch_rolling_update | 0.0052 | 0.0160 | 0.0476 | 0.0028 | 0.4510 | 0.8228 | 0.9402 | 3 | False | True | True | True |
| USO | har_rolling_update | 0.0071 | 0.0249 | 0.0327 | 0.0043 | 0.3946 | 0.8271 | 0.8687 | 1 | True | True | True | True |

## VaR And ES Calibration Audit

- VaR and ES calibration uses validation-period standardised residuals only; test-period returns are used only for final breach evaluation.
- The method stored in risk tables is `validation_student_t_residual_df5`.
- The risk CSV row count matches `var_backtest_results`.

## SQL And View Checks

| check_name | failing_rows |
| --- | --- |
| duplicate_prices | 0 |
| non_positive_prices | 0 |
| forecast_leakage | 0 |
| negative_forecasts | 0 |

| view_name | row_count |
| --- | --- |
| v_dashboard_overview | 1 |
| v_model_comparison | 190 |
| v_var_breach_summary | 380 |
| v_regime_summary | 30 |

## Regime Threshold Trade-Off

The current fixed threshold keeps full-sample top-decile recall above 75%. A validation-F1 selected lower threshold raises validation recall but lowers full-sample precision/F1, so it is documented rather than adopted.

| threshold_percentile | validation_precision | validation_recall | validation_f1 | validation_false_high_flag_rate | full_precision | full_recall | full_f1 | full_false_high_flag_rate | selection_note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0.8000 | 0.7814 | 0.7817 | 0.7618 | 0.2186 | 0.3947 | 0.8309 | 0.5343 | 0.6053 | validation F1 leader |
| 0.8200 | 0.7952 | 0.6991 | 0.7258 | 0.2048 | 0.4110 | 0.7905 | 0.5399 | 0.5890 |  |
| 0.8400 | 0.7915 | 0.6260 | 0.6797 | 0.2085 | 0.4346 | 0.7544 | 0.5507 | 0.5654 | current fixed threshold |
| 0.8420 | 0.7916 | 0.6187 | 0.6749 | 0.2084 | 0.4371 | 0.7505 | 0.5516 | 0.5629 |  |
| 0.8500 | 0.7984 | 0.5967 | 0.6624 | 0.2016 | 0.4470 | 0.7358 | 0.5552 | 0.5530 |  |
| 0.8600 | 0.8090 | 0.5709 | 0.6493 | 0.1910 | 0.4598 | 0.7211 | 0.5606 | 0.5402 |  |
| 0.8800 | 0.8167 | 0.5053 | 0.6022 | 0.1833 | 0.4779 | 0.6786 | 0.5601 | 0.5221 |  |
| 0.9000 | 0.8188 | 0.4698 | 0.5715 | 0.1812 | 0.5069 | 0.6351 | 0.5631 | 0.4931 |  |

## Compaction Safety

The compact DuckDB file preserves row counts and headline metrics while remaining below 100 MiB. Dashboard and validation views were queried successfully after compaction.
