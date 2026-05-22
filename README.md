# Volatility Risk Forecasting Platform

![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)
![SQL](https://img.shields.io/badge/SQL-analytics-1F6FEB)
![DuckDB](https://img.shields.io/badge/DuckDB-default_database-FFF000)
![Tests](https://img.shields.io/badge/tests-pytest-0A7E3D)
![Ruff](https://img.shields.io/badge/lint-ruff-D7FF64)
![Black](https://img.shields.io/badge/format-black-000000)
![Streamlit](https://img.shields.io/badge/dashboard-Streamlit-FF4B4B)
![License](https://img.shields.io/badge/license-MIT-blue)

A SQL-backed market risk and volatility forecasting platform built with Python, DuckDB, pandas, scikit-learn, `arch`, Streamlit and Plotly.
The project combines reproducible market-data ingestion, database-first analytics, volatility models, VaR and Expected Shortfall backtesting, regime detection, portfolio risk and dashboard reporting.

## What This Project Demonstrates

- SQL-centred analytical engineering using DuckDB tables, validation views and dashboard views.
- Time-series model validation with fixed train, validation and test periods.
- Volatility forecasting across rolling, EWMA, GARCH-family, machine-learning and ensemble models.
- Market risk conversion from volatility forecasts into VaR and Expected Shortfall.
- Statistical backtesting with Kupiec and Christoffersen tests.
- Reporting discipline: weak metrics are shown rather than hidden.

## Why It Matters For Quant And Risk Roles

Risk analytics work rarely stops at fitting a model. A useful platform needs data controls, SQL lineage, reproducible model outputs, independent validation and dashboard-ready summaries.
This repository is designed to show that full workflow: from prices to forecasts, from forecasts to risk estimates, and from risk estimates to validation reports.

## Headline Results

- Best aggregate test-period model by QLIKE: `har_rolling_update`.
- Average QLIKE improvement versus rolling 21-day volatility: 0.63%.
- Average QLIKE improvement versus EWMA: 4.76%.
- Average QLIKE improvement versus GARCH(1,1): 8.31%.
- Top-two asset share for the best aggregate model: 80.00%.
- Average 95% VaR breach rate across test results: 4.38%.
- Average 99% VaR breach rate across test results: 0.98%.
- Average top-decile volatility capture: 83.39%.
- Average false high-volatility flag rate: 63.97%.
- Largest SQL scale benchmark: 2,512,785 rows.
- Dashboard query p95 latency: 15.65 ms.

## Target Achievement

| Target | Result | Status |
| --- | --- | --- |
| QLIKE improvement vs rolling vol >= 12% | 0.63% | fail |
| QLIKE improvement vs EWMA >= 5% | 4.76% | fail |
| Best/top-2 model across >= 70% assets | 80.00% | pass |
| 95% VaR breach rate 4.7%-5.3% | 4.38% | fail |
| 99% VaR breach rate 0.8%-1.2% | 0.98% | pass |
| Kupiec not rejected for most assets | 72.67% | pass |
| Christoffersen not rejected for most assets | 92.00% | pass |
| ES tail-loss ratio 0.9-1.1 | 1.028 | pass |
| Top-decile vol capture >= 75% | 83.39% | pass |
| SQL handles 1m+ rows | 2,512,785 | pass |
| Dashboard queries < 1 sec | 15.65 ms p95 | pass |
| Tests pass | passed | pass |

## SQL Architecture Summary

DuckDB is the default database. The platform stores raw prices, cleaned prices, returns, realised volatility, features, forecasts, VaR and ES estimates, breaches, regime labels, model metrics and query benchmarks.
Dashboard sections are backed by SQL views such as `v_dashboard_overview`, `v_model_comparison`, `v_var_breach_summary`, `v_asset_risk_summary` and `v_portfolio_risk_summary`.

## Model Comparison Summary

| model | avg_qlike | avg_rank | top_two_share | improvement_vs_rolling_21 | improvement_vs_ewma | improvement_vs_garch |
| --- | --- | --- | --- | --- | --- | --- |
| har_rolling_update | 0.1813 | 1.5000 | 0.8000 | 0.0063 | 0.0476 | 0.0831 |
| gjr_rolling_update | 0.1814 | 2.1000 | 0.7000 | 0.0062 | 0.0475 | 0.0830 |
| garch_rolling_update | 0.1814 | 2.6000 | 0.4000 | 0.0061 | 0.0474 | 0.0830 |
| ewma_rolling_update | 0.1814 | 3.8000 | 0.1000 | 0.0061 | 0.0474 | 0.0829 |
| rolling_21 | 0.1842 | 5.4000 | 0.0000 | 0.0000 | 0.0416 | 0.0774 |
| previous_day_rv | 0.1842 | 5.4000 | 0.0000 | 0.0000 | 0.0416 | 0.0774 |
| simple_average_ensemble | 0.1849 | 6.8000 | 0.0000 | -0.0017 | 0.0400 | 0.0759 |
| validation_weighted_ensemble | 0.1849 | 6.8000 | 0.0000 | -0.0017 | 0.0400 | 0.0759 |
| random_forest | 0.1907 | 9.2000 | 0.0000 | -0.0174 | 0.0251 | 0.0615 |
| hist_gradient_boosting | 0.1924 | 10.2000 | 0.0000 | -0.0215 | 0.0212 | 0.0578 |
| ewma_tuned | 0.1991 | 10.8000 | 0.0000 | -0.0326 | 0.0104 | 0.0476 |
| ewma_094 | 0.2047 | 11.8000 | 0.0000 | -0.0435 | 0.0000 | 0.0375 |
| gjr_garch | 0.2183 | 13.1000 | 0.0000 | -0.0732 | -0.0286 | 0.0106 |
| garch_11 | 0.2227 | 13.5000 | 0.0000 | -0.0853 | -0.0398 | 0.0000 |
| rolling_63 | 0.2760 | 15.0000 | 0.0000 | -0.1943 | -0.1443 | -0.1008 |

## VaR And ES Backtesting Summary

| model | confidence_level | avg_breach_rate | kupiec_not_rejected | christoffersen_not_rejected | avg_es_tail_loss_ratio | avg_max_cluster |
| --- | --- | --- | --- | --- | --- | --- |
| ewma_094 | 0.9500 | 0.0432 | 0.6000 | 0.9000 | 0.9951 | 2.3000 |
| ewma_094 | 0.9900 | 0.0101 | 1.0000 | 0.9000 | 1.0324 | 1.4000 |
| ewma_rolling_update | 0.9500 | 0.0427 | 0.5000 | 1.0000 | 1.0046 | 2.3000 |
| ewma_rolling_update | 0.9900 | 0.0094 | 0.8000 | 0.9000 | 1.0622 | 1.4000 |
| ewma_tuned | 0.9500 | 0.0427 | 0.6000 | 1.0000 | 1.0002 | 2.3000 |
| ewma_tuned | 0.9900 | 0.0108 | 0.9000 | 0.8000 | 1.0408 | 1.5000 |
| garch_11 | 0.9500 | 0.0497 | 0.9000 | 0.9000 | 1.0005 | 2.4000 |
| garch_11 | 0.9900 | 0.0110 | 1.0000 | 0.9000 | 1.0633 | 1.4000 |
| garch_rolling_update | 0.9500 | 0.0436 | 0.6000 | 1.0000 | 1.0022 | 2.3000 |
| garch_rolling_update | 0.9900 | 0.0095 | 0.8000 | 0.9000 | 1.0622 | 1.4000 |
| gjr_garch | 0.9500 | 0.0488 | 0.9000 | 0.9000 | 1.0099 | 2.3000 |
| gjr_garch | 0.9900 | 0.0113 | 0.9000 | 1.0000 | 1.0527 | 1.3000 |
| gjr_rolling_update | 0.9500 | 0.0432 | 0.6000 | 1.0000 | 1.0048 | 2.3000 |
| gjr_rolling_update | 0.9900 | 0.0095 | 0.8000 | 0.9000 | 1.0620 | 1.4000 |
| har_rolling_update | 0.9500 | 0.0426 | 0.5000 | 1.0000 | 1.0035 | 2.3000 |
| har_rolling_update | 0.9900 | 0.0094 | 0.8000 | 0.9000 | 1.0582 | 1.4000 |
| hist_gradient_boosting | 0.9500 | 0.0433 | 0.6000 | 0.9000 | 1.0081 | 2.4000 |
| hist_gradient_boosting | 0.9900 | 0.0096 | 0.9000 | 0.9000 | 1.0478 | 1.4000 |
| previous_day_rv | 0.9500 | 0.0425 | 0.4000 | 1.0000 | 1.0005 | 2.4000 |
| previous_day_rv | 0.9900 | 0.0090 | 0.8000 | 0.9000 | 1.0577 | 1.4000 |
| random_forest | 0.9500 | 0.0435 | 0.6000 | 0.9000 | 1.0047 | 2.2000 |
| random_forest | 0.9900 | 0.0090 | 0.8000 | 0.9000 | 1.0605 | 1.4000 |
| rolling_21 | 0.9500 | 0.0425 | 0.4000 | 1.0000 | 1.0005 | 2.4000 |
| rolling_21 | 0.9900 | 0.0090 | 0.8000 | 0.9000 | 1.0577 | 1.4000 |
| rolling_63 | 0.9500 | 0.0404 | 0.5000 | 0.9000 | 0.9901 | 2.5000 |
| rolling_63 | 0.9900 | 0.0083 | 1.0000 | 0.8000 | 1.0406 | 1.5000 |
| simple_average_ensemble | 0.9500 | 0.0440 | 0.6000 | 1.0000 | 1.0052 | 2.3000 |
| simple_average_ensemble | 0.9900 | 0.0105 | 0.8000 | 0.8000 | 1.0469 | 1.4000 |
| validation_weighted_ensemble | 0.9500 | 0.0440 | 0.6000 | 1.0000 | 1.0052 | 2.3000 |
| validation_weighted_ensemble | 0.9900 | 0.0105 | 0.8000 | 0.8000 | 1.0469 | 1.4000 |

## Regime Detection Summary

| asset | top_decile_capture | false_high_flag_rate | high_regime_share | median_regime_days | transition_count |
| --- | --- | --- | --- | --- | --- |
| AAPL | 0.7797 | 0.6686 | 0.2353 | 5.0000 | 172 |
| GLD | 0.8780 | 0.5782 | 0.2082 | 5.0000 | 169 |
| IWM | 0.8441 | 0.6473 | 0.2394 | 6.0000 | 189 |
| JPM | 0.7966 | 0.6216 | 0.2106 | 5.0000 | 169 |
| MSFT | 0.7831 | 0.6495 | 0.2235 | 6.0000 | 202 |
| NVDA | 0.9695 | 0.6011 | 0.2431 | 5.0000 | 206 |
| QQQ | 0.7797 | 0.7096 | 0.2686 | 5.0000 | 168 |
| SPY | 0.7661 | 0.6908 | 0.2479 | 9.0000 | 128 |
| TLT | 0.8237 | 0.6478 | 0.2340 | 6.0000 | 201 |
| USO | 0.9186 | 0.5824 | 0.2201 | 5.0000 | 188 |

## SQL Performance Summary

| query_name | row_count | mean_ms | p50_ms | p95_ms | min_ms | max_ms | benchmark_rows | created_at |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| dashboard_overview | 1 | 7.8882 | 7.9175 | 8.2063 | 7.4985 | 8.2306 | 2512785 | 2026-05-22 11:51:04.770759 |
| model_comparison | 15 | 2.7925 | 2.8161 | 3.1454 | 2.3866 | 3.2598 | 2512785 | 2026-05-22 11:51:04.770759 |
| var_breach_summary | 300 | 0.5860 | 0.5644 | 0.7323 | 0.5070 | 0.8395 | 2512785 | 2026-05-22 11:51:04.770759 |
| asset_risk_summary | 10 | 14.0997 | 14.1487 | 15.6461 | 12.6717 | 15.8876 | 2512785 | 2026-05-22 11:51:04.770759 |
| portfolio_risk_summary | 15 | 1.9834 | 1.9680 | 2.2577 | 1.7558 | 2.3514 | 2512785 | 2026-05-22 11:51:04.770759 |
| one_million_row_synthetic_scale | 10 | 5.8740 | 5.7446 | 6.2218 | 5.6035 | 6.2558 | 1188000 | 2026-05-22 11:51:04.770759 |

## Dashboard Screenshots

The screenshots below were captured from the local Streamlit dashboard after the full pipeline run.

![Dashboard overview](docs/images/dashboard_overview.png)
![SQL pipeline](docs/images/sql_pipeline.png)
![Model comparison](docs/images/model_comparison.png)
![Volatility forecasts](docs/images/volatility_forecasts.png)
![VaR backtesting](docs/images/var_backtesting.png)
![Breach analysis](docs/images/breach_analysis.png)
![Regime detection](docs/images/regime_detection.png)
![Portfolio risk](docs/images/portfolio_risk.png)
![SQL performance](docs/images/sql_performance.png)

## Project Architecture

```text
volatility-risk-forecasting-platform/
|-- app/                    Streamlit dashboard and reusable UI helpers
|-- data/                   Offline sample data and data notes
|-- database/               DuckDB database location
|-- docs/                   Methodology, SQL architecture and validation notes
|-- examples/               One-command pipeline entry points
|-- notebooks/              Executable notebooks using package modules
|-- reports/                Generated validation, model, risk and SQL reports
|-- sql/                    Schema, validation views and dashboard views
|-- src/volatility_platform Core package
|-- tests/                  Unit, integration and smoke tests
```

## Module Map

- `data`: universe definition, optional live download, offline sample loading and cleaning.
- `database`: DuckDB connection, schema execution, build pipeline and validation queries.
- `features`: returns, realised-volatility estimators, lagged volatility features and regime features.
- `models`: baselines, EWMA, GARCH-family wrappers, tree models, ensembles and walk-forward orchestration.
- `risk`: VaR, Expected Shortfall, portfolio risk, stress scenarios and risk contributions.
- `backtesting`: forecast metrics, Kupiec, Christoffersen, ES diagnostics and breach clustering.
- `regimes`: high/medium/low volatility labelling and change-point helpers.
- `reporting`: Markdown and CSV report generation.

## Data Pipeline

The default pipeline uses `data/sample_prices.csv` so the repository runs offline without API keys.
Live data can be requested with `--live`, in which case downloaded files are cached under `data/raw/` and excluded from version control.
The fixed universe is SPY, QQQ, IWM, TLT, GLD, USO, AAPL, MSFT, NVDA and JPM.

## Methodology

The core target is next-day 21-day close-to-close realised volatility. Features are observed at forecast date `t`; the target is realised volatility on date `t+1`.
Training runs through 2019, validation through 2021 and final test from 2022 onward.
Ensemble weights and VaR residual calibration use validation data only.

## Installation

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -e .[dev]
```

## Build Database

```bash
python examples/build_database.py
python examples/build_database.py --live
```

## Run Forecasting

```bash
python examples/run_forecasting_pipeline.py
```

## Run Risk Backtest

```bash
python examples/run_var_backtest.py
```

## Generate Reports

```bash
python examples/run_regime_detection.py
python examples/benchmark_sql_queries.py
python examples/generate_all_reports.py
```

## Run Dashboard

```bash
streamlit run app/streamlit_app.py
```

## Testing

```bash
python -m compileall src app examples
python -m pytest -v
python -m ruff check .
python -m black --check .
```

## Limitations

- The offline dataset is designed for reproducibility; live public data should be used before quoting production conclusions.
- Daily data does not capture intraday volatility, microstructure noise or overnight liquidity gaps.
- GARCH estimates can fail or become unstable in short or highly stressed samples.
- Machine-learning models can under-react to regimes not represented in training data.
- VaR and ES backtests have limited statistical power, especially at the 99% level.
- SQL benchmark timings depend on local hardware, cache state and DuckDB version.

## Future Improvements

- Add intraday realised volatility when a free data source is available.
- Add PostgreSQL mode for multi-user deployment while keeping DuckDB as the default.
- Add Bayesian or state-space volatility models.
- Add model-risk challenger reports and stability monitoring.
- Add portfolio optimisation constraints and user-defined dashboard weights.

## CV Bullet Examples

- Built a SQL-backed volatility forecasting and market risk platform using Python, DuckDB and Streamlit, comparing rolling, EWMA, GARCH-family and machine-learning models across a multi-asset universe; best aggregate model improved out-of-sample QLIKE by 0.63% vs rolling volatility and 4.76% vs EWMA.
- Designed DuckDB SQL tables and validation views for prices, returns, realised volatility, forecasts, VaR/ES backtests and breach analytics, supporting reproducible risk reports and dashboard queries across 2,512,791+ persisted rows plus a 2,512,785-row scale benchmark.
- Implemented validation-period empirical residual calibration for volatility-scaled VaR/ES, with Kupiec and Christoffersen backtests reported at asset/model level rather than cherry-picked.

## Interview Talking Points

- Why QLIKE is the primary volatility metric and why RMSE alone is not enough.
- How forecast-date and target-date keys prevent future-data leakage.
- Why validation-period calibration is acceptable but test-period calibration is not.
- How DuckDB views make the dashboard reproducible and auditable.
- What happens when GARCH, EWMA and tree models disagree during stress regimes.

## Reproducibility Notes

The repository includes generated reports and benchmark CSVs from the latest local run.
Regenerate all metrics after changing data, model code or dependencies.
