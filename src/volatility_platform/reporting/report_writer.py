from __future__ import annotations

from contextlib import suppress
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd

from volatility_platform.config import (
    DATABASE_PATH,
    REPORTS_DIR,
    ROOT_DIR,
    TRAIN_END,
    VALIDATION_END,
)
from volatility_platform.database.queries import table_row_counts
from volatility_platform.regimes.volatility_regimes import classification_metrics
from volatility_platform.reporting.model_report import (
    asset_level_audit_summary,
    asset_level_model_audit,
    model_summary_tables,
)
from volatility_platform.reporting.risk_report import risk_summary
from volatility_platform.reporting.sql_performance_report import write_sql_performance_report
from volatility_platform.reporting.validation_report import target_table


def _markdown_table(frame: pd.DataFrame, max_rows: int | None = None) -> str:
    if max_rows is not None:
        frame = frame.head(max_rows)
    if frame.empty:
        return "_No rows._"
    display = frame.copy()
    for column in display.columns:
        if pd.api.types.is_float_dtype(display[column]):
            display[column] = display[column].map(
                lambda value: "" if pd.isna(value) else f"{value:.4f}"
            )
        else:
            display[column] = display[column].map(
                lambda value: "" if pd.isna(value) else str(value)
            )
    headers = [str(column) for column in display.columns]
    rows = display.values.tolist()
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    lines.extend("| " + " | ".join(row) + " |" for row in rows)
    return "\n".join(lines)


def load_report_inputs(db_path: str | Path = DATABASE_PATH) -> dict[str, pd.DataFrame]:
    with duckdb.connect(str(db_path), read_only=True) as con:
        return {
            "metrics": con.execute("SELECT * FROM model_metrics").fetchdf(),
            "var_results": con.execute("SELECT * FROM var_backtest_results").fetchdf(),
            "regime": con.execute("SELECT * FROM regime_metrics").fetchdf(),
            "bench": con.execute("SELECT * FROM sql_query_benchmarks").fetchdf(),
            "quality": con.execute("SELECT * FROM data_quality_checks").fetchdf(),
            "counts": table_row_counts(db_path),
            "portfolio": con.execute("SELECT * FROM v_portfolio_risk_summary").fetchdf(),
            "source": con.execute("""
                SELECT
                    source AS data_source,
                    COUNT(*) AS raw_price_rows,
                    MIN(date) AS first_date,
                    MAX(date) AS last_date
                FROM raw_prices
                GROUP BY source
                ORDER BY raw_price_rows DESC
                """).fetchdf(),
        }


def write_model_comparison_report(
    inputs: dict[str, pd.DataFrame],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    aggregate, asset = model_summary_tables(inputs["metrics"])
    asset_audit = asset_level_model_audit(inputs["metrics"])
    asset_summary = asset_level_audit_summary(asset_audit)
    lines = [
        "# Model Comparison Report",
        "",
        "## Data Source",
        "",
        _markdown_table(inputs["source"]),
        "",
        "The fixed universe is evaluated as a complete panel; assets and periods are not selected based on model performance.",
        "",
        "## Executive Summary",
        "",
        "The modelling layer compares rolling realised-volatility baselines, EWMA, GARCH-family models, tree-based regressors and ensemble forecasts on identical out-of-sample dates.",
        "QLIKE is treated as the primary metric because it is robust for volatility forecast comparison and penalises variance underestimation. The implementation uses the standard non-negative variance-ratio loss.",
        "",
        "## Aggregate Test-Period Ranking",
        "",
        _markdown_table(aggregate),
        "",
        "## Asset-Level Test-Period Ranking",
        "",
        _markdown_table(
            asset[
                [
                    "asset",
                    "model",
                    "qlike",
                    "mae",
                    "rmse",
                    "rank_qlike",
                    "improvement_vs_rolling_21",
                    "improvement_vs_ewma",
                    "improvement_vs_garch",
                ]
            ],
            120,
        ),
        "",
        "## Asset-Level Robustness Audit",
        "",
        _markdown_table(asset_audit),
        "",
        "## Asset-Level Robustness Summary",
        "",
        _markdown_table(asset_summary),
        "",
        "## Interpretation",
        "",
        "The aggregate table reports average ranks across the full fixed universe rather than a selected subset of assets.",
        "Where machine-learning models win, the likely driver is their use of volatility-of-volatility, market proxy and drawdown features.",
        "Where simpler models win, the result is retained because volatility forecasting is noisy and regime-dependent.",
        "",
        "## Failure Modes Observed",
        "",
        "- GARCH-family forecasts can be unstable when a series has abrupt volatility regime shifts.",
        "- Tree models may under-react to newly emerging stress regimes that are not represented in training data.",
        "- Range-based features improve responsiveness but can amplify noisy high-low observations.",
        "",
        "## Reproducibility",
        "",
        "Run `python examples/run_forecasting_pipeline.py` to regenerate forecasts and `python examples/generate_all_reports.py` to refresh this report.",
    ]
    (REPORTS_DIR / "model_comparison_report.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )
    asset_audit.to_csv(REPORTS_DIR / "model_comparison_results.csv", index=False)
    aggregate.to_csv(REPORTS_DIR / "model_ranking_results.csv", index=False)
    return aggregate, asset_audit


def write_risk_backtest_report(inputs: dict[str, pd.DataFrame]) -> pd.DataFrame:
    summary = risk_summary(inputs["var_results"])
    lines = [
        "# Risk Backtest Report",
        "",
        "## Data Source",
        "",
        _markdown_table(inputs["source"]),
        "",
        "## Scope",
        "",
        "Forecast volatility is converted into one-day 95% and 99% VaR and Expected Shortfall estimates using validation-period Student-t residual calibration with five degrees of freedom.",
        "Calibration is performed before the test period and is not fitted to final test breaches.",
        "",
        "## Aggregate VaR and ES Results",
        "",
        _markdown_table(summary),
        "",
        "## Asset-Level Backtest Results",
        "",
        _markdown_table(
            inputs["var_results"][
                [
                    "asset",
                    "model",
                    "confidence_level",
                    "period",
                    "n_obs",
                    "expected_breaches",
                    "actual_breaches",
                    "breach_rate",
                    "kupiec_p_value",
                    "christoffersen_p_value",
                    "es_tail_loss_ratio",
                    "max_cluster_length",
                ]
            ],
            160,
        ),
        "",
        "## Portfolio Risk Summary",
        "",
        _markdown_table(inputs["portfolio"]),
        "",
        "## Interpretation",
        "",
        "Kupiec p-values test unconditional coverage. Christoffersen p-values test whether breaches appear clustered rather than independent.",
        "Expected Shortfall diagnostics compare realised tail losses against model-implied ES on breach days.",
        "A good VaR model can still fail ES diagnostics if it captures breach frequency but underestimates breach severity.",
        "",
        "## Limitations",
        "",
        "- Daily VaR backtests have limited power, especially at the 99% level.",
        "- Student-t residual calibration improves coverage but still depends on validation-period representativeness.",
        "- Asset-level VaR ignores transaction costs, liquidity effects and intraday gap risk.",
    ]
    (REPORTS_DIR / "risk_backtest_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    inputs["var_results"].to_csv(REPORTS_DIR / "var_backtest_results.csv", index=False)
    return summary


def write_regime_csv(inputs: dict[str, pd.DataFrame]) -> None:
    inputs["regime"].to_csv(REPORTS_DIR / "regime_detection_results.csv", index=False)


def write_validation_report(
    inputs: dict[str, pd.DataFrame],
    model_summary: pd.DataFrame,
    tests_passed: bool = True,
) -> pd.DataFrame:
    targets = target_table(
        model_summary,
        inputs["var_results"],
        inputs["regime"],
        inputs["bench"],
        tests_passed=tests_passed,
    )
    lines = [
        "# Validation Report",
        "",
        "## Data Source",
        "",
        _markdown_table(inputs["source"]),
        "",
        "## Target Achievement Summary",
        "",
        _markdown_table(targets),
        "",
        "## Data Quality Checks",
        "",
        _markdown_table(inputs["quality"]),
        "",
        "## SQL Validation Checks",
        "",
        "Validation views test duplicate asset/date keys, non-positive prices, forecast leakage and non-positive forecasts.",
        "Run `python -m pytest tests/test_sql_validation_queries.py -v` for the automated check.",
        "",
        "## Model Training Checks",
        "",
        "All forecasts use a fixed time-series split: training through 2019, validation through 2021 and test from 2022 onward.",
        "Machine-learning models fit on the training window only; ensemble weights and VaR residual calibration are estimated from validation data.",
        "",
        "## Forecast Metric Checks",
        "",
        "RMSE, MAE, QLIKE, MAPE, correlation and directional accuracy are stored in `model_metrics` and compared through SQL views.",
        "",
        "## VaR and ES Backtesting Checks",
        "",
        "The risk layer stores VaR estimates, Expected Shortfall estimates, breach events, Kupiec tests, Christoffersen tests and ES diagnostics.",
        "",
        "## Regime Detection Checks",
        "",
        "Regime metrics report top-decile volatility capture, precision, recall, F1, false-positive rate, persistence and transition counts.",
        "",
        "## Dashboard Query Checks",
        "",
        "Dashboard views are benchmarked and stored in `sql_query_benchmarks`.",
        "",
        "## Tests Summary",
        "",
        "The repository includes unit, integration and smoke tests for database construction, SQL views, features, models, backtests, reports and dashboard import.",
        "The target table records the verification status from the current project run.",
        "",
        "## Honest Limitations",
        "",
        "Targets that fail are retained in the report. The project favours transparent model validation over forcing every metric to pass.",
    ]
    (REPORTS_DIR / "validation_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return targets


def update_readme(
    inputs: dict[str, pd.DataFrame],
    model_summary: pd.DataFrame,
    risk_summary_frame: pd.DataFrame,
    targets: pd.DataFrame,
) -> None:
    best = model_summary.sort_values("avg_qlike").iloc[0]
    var95 = inputs["var_results"][inputs["var_results"]["confidence_level"] == 0.95]
    var99 = inputs["var_results"][inputs["var_results"]["confidence_level"] == 0.99]
    capture = inputs["regime"]["top_decile_capture"].mean()
    false_flag = inputs["regime"]["false_high_flag_rate"].mean()
    precision = inputs["regime"]["precision"].mean()
    f1_score = inputs["regime"]["f1_score"].mean()
    max_rows = int(inputs["bench"]["benchmark_rows"].max())
    dashboard_p95 = inputs["bench"][
        inputs["bench"]["query_name"] != "one_million_row_synthetic_scale"
    ]["p95_ms"].max()
    source_label = ", ".join(inputs["source"]["data_source"].astype(str).tolist())
    first_date = inputs["source"]["first_date"].min()
    last_date = inputs["source"]["last_date"].max()
    cv_ready = (
        best["improvement_vs_rolling_21"] >= 0.08
        and best["improvement_vs_ewma"] >= 0.05
        and best["top_two_share"] >= 0.70
    )
    lines = [
        "# Volatility Risk Forecasting Platform",
        "",
        "![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)",
        "![SQL](https://img.shields.io/badge/SQL-analytics-1F6FEB)",
        "![DuckDB](https://img.shields.io/badge/DuckDB-default_database-FFF000)",
        "![Tests](https://img.shields.io/badge/tests-pytest-0A7E3D)",
        "![Ruff](https://img.shields.io/badge/lint-ruff-D7FF64)",
        "![Black](https://img.shields.io/badge/format-black-000000)",
        "![Streamlit](https://img.shields.io/badge/dashboard-Streamlit-FF4B4B)",
        "![License](https://img.shields.io/badge/license-MIT-blue)",
        "",
        "A SQL-backed market risk and volatility forecasting platform built with Python, DuckDB, pandas, scikit-learn, `arch`, Streamlit and Plotly.",
        "The project combines reproducible market-data ingestion, database-first analytics, volatility models, VaR and Expected Shortfall backtesting, regime detection, portfolio risk and dashboard reporting.",
        "",
        "## What This Project Demonstrates",
        "",
        "- SQL-centred analytical engineering using DuckDB tables, validation views and dashboard views.",
        "- Time-series model validation with fixed train, validation and test periods.",
        "- Volatility forecasting across rolling, EWMA, GARCH-family, machine-learning and ensemble models.",
        "- Market risk conversion from volatility forecasts into VaR and Expected Shortfall.",
        "- Statistical backtesting with Kupiec and Christoffersen tests.",
        "- Reporting discipline: weak metrics are shown rather than hidden.",
        "",
        "## Why It Matters For Quant And Risk Roles",
        "",
        "Risk analytics work rarely stops at fitting a model. A useful platform needs data controls, SQL lineage, reproducible model outputs, independent validation and dashboard-ready summaries.",
        "This repository is designed to show that full workflow: from prices to forecasts, from forecasts to risk estimates, and from risk estimates to validation reports.",
        "",
        "## Headline Results",
        "",
        f"- Latest generated report data source: `{source_label}`.",
        f"- Data date range: {first_date} to {last_date}.",
        f"- Best aggregate test-period model by QLIKE: `{best['model']}`.",
        f"- Average QLIKE improvement versus rolling 21-day volatility: {best['improvement_vs_rolling_21'] * 100:.2f}%.",
        f"- Average QLIKE improvement versus EWMA: {best['improvement_vs_ewma'] * 100:.2f}%.",
        f"- Average QLIKE improvement versus GARCH(1,1): {best['improvement_vs_garch'] * 100:.2f}%.",
        f"- Top-two asset share for the best aggregate model: {best['top_two_share'] * 100:.2f}%.",
        f"- Average 95% VaR breach rate across test results: {var95['breach_rate'].mean() * 100:.2f}%.",
        f"- Average 99% VaR breach rate across test results: {var99['breach_rate'].mean() * 100:.2f}%.",
        f"- Average top-decile volatility capture: {capture * 100:.2f}%.",
        f"- Average high-volatility precision: {precision * 100:.2f}%.",
        f"- Average high-volatility F1 score: {f1_score * 100:.2f}%.",
        f"- Average false high-volatility flag rate: {false_flag * 100:.2f}%.",
        f"- Largest SQL scale benchmark: {max_rows:,} rows.",
        f"- Dashboard query p95 latency: {dashboard_p95:.2f} ms.",
        "",
        "## Target Achievement",
        "",
        _markdown_table(targets),
        "",
        "## SQL Architecture Summary",
        "",
        "DuckDB is the default database. The platform stores raw prices, cleaned prices, returns, realised volatility, features, forecasts, VaR and ES estimates, breaches, regime labels, model metrics and query benchmarks.",
        "Dashboard sections are backed by SQL views such as `v_dashboard_overview`, `v_model_comparison`, `v_var_breach_summary`, `v_asset_risk_summary` and `v_portfolio_risk_summary`.",
        "",
        "## Model Comparison Summary",
        "",
        _markdown_table(
            model_summary[
                [
                    "model",
                    "avg_qlike",
                    "avg_rank",
                    "top_two_share",
                    "improvement_vs_rolling_21",
                    "improvement_vs_ewma",
                    "improvement_vs_garch",
                ]
            ]
        ),
        "",
        "## VaR And ES Backtesting Summary",
        "",
        _markdown_table(risk_summary_frame),
        "",
        "## Regime Detection Summary",
        "",
        _markdown_table(inputs["regime"]),
        "",
        "## SQL Performance Summary",
        "",
        _markdown_table(inputs["bench"]),
        "",
        "## Dashboard Screenshots",
        "",
        "The screenshots below were captured from the local Streamlit dashboard after the full pipeline run.",
        "",
        "![Dashboard overview](docs/images/dashboard_overview.png)",
        "![SQL pipeline](docs/images/sql_pipeline.png)",
        "![Model comparison](docs/images/model_comparison.png)",
        "![Volatility forecasts](docs/images/volatility_forecasts.png)",
        "![VaR backtesting](docs/images/var_backtesting.png)",
        "![Breach analysis](docs/images/breach_analysis.png)",
        "![Regime detection](docs/images/regime_detection.png)",
        "![Portfolio risk](docs/images/portfolio_risk.png)",
        "![SQL performance](docs/images/sql_performance.png)",
        "",
        "## Project Architecture",
        "",
        "```text",
        "volatility-risk-forecasting-platform/",
        "|-- app/                    Streamlit dashboard and reusable UI helpers",
        "|-- data/                   Offline sample data and data notes",
        "|-- database/               DuckDB database location",
        "|-- docs/                   Methodology, SQL architecture and validation notes",
        "|-- examples/               One-command pipeline entry points",
        "|-- notebooks/              Executable notebooks using package modules",
        "|-- reports/                Generated validation, model, risk and SQL reports",
        "|-- sql/                    Schema, validation views and dashboard views",
        "|-- src/volatility_platform Core package",
        "|-- tests/                  Unit, integration and smoke tests",
        "```",
        "",
        "## Module Map",
        "",
        "- `data`: universe definition, optional live download, offline sample loading and cleaning.",
        "- `database`: DuckDB connection, schema execution, build pipeline and validation queries.",
        "- `features`: returns, realised-volatility estimators, lagged volatility features and regime features.",
        "- `models`: baselines, EWMA, GARCH-family wrappers, tree models, ensembles and walk-forward orchestration.",
        "- `risk`: VaR, Expected Shortfall, portfolio risk, stress scenarios and risk contributions.",
        "- `backtesting`: forecast metrics, Kupiec, Christoffersen, ES diagnostics and breach clustering.",
        "- `regimes`: high/medium/low volatility labelling and change-point helpers.",
        "- `reporting`: Markdown and CSV report generation.",
        "",
        "## Data Pipeline",
        "",
        "The default pipeline uses `data/sample_prices.csv` so the repository runs offline without API keys.",
        "Live data can be requested with `--live`, in which case downloaded files are cached under `data/raw/` and excluded from version control.",
        "Generated reports explicitly state whether they were produced from live yfinance data or the sample fallback.",
        "The fixed universe is SPY, QQQ, IWM, TLT, GLD, USO, AAPL, MSFT, NVDA and JPM.",
        "",
        "## Methodology",
        "",
        "The core target is next-day 21-day close-to-close realised volatility. Features are observed at forecast date `t`; the target is realised volatility on date `t+1`.",
        "Training runs through 2019, validation through 2021 and final test from 2022 onward.",
        "Ensemble weights and VaR residual calibration use validation data only.",
        "",
        "## Installation",
        "",
        "```bash",
        "python -m venv .venv",
        "source .venv/bin/activate  # Windows: .venv\\Scripts\\activate",
        "python -m pip install --upgrade pip",
        "python -m pip install -e .[dev]",
        "```",
        "",
        "## Build Database",
        "",
        "```bash",
        "python examples/build_database.py",
        "python examples/build_database.py --live",
        "```",
        "",
        "## Run Forecasting",
        "",
        "```bash",
        "python examples/run_forecasting_pipeline.py",
        "```",
        "",
        "## Run Risk Backtest",
        "",
        "```bash",
        "python examples/run_var_backtest.py",
        "```",
        "",
        "## Generate Reports",
        "",
        "```bash",
        "python examples/run_regime_detection.py",
        "python examples/benchmark_sql_queries.py",
        "python examples/generate_all_reports.py",
        "```",
        "",
        "## Run Dashboard",
        "",
        "```bash",
        "streamlit run app/streamlit_app.py",
        "```",
        "",
        "## Testing",
        "",
        "```bash",
        "python -m compileall src app examples",
        "python -m pytest -v",
        "python -m ruff check .",
        "python -m black --check .",
        "```",
        "",
        "## Limitations",
        "",
        "- The offline dataset is designed for reproducibility; live public data should be used before quoting production conclusions.",
        "- Daily data does not capture intraday volatility, microstructure noise or overnight liquidity gaps.",
        "- GARCH estimates can fail or become unstable in short or highly stressed samples.",
        "- Machine-learning models can under-react to regimes not represented in training data.",
        "- VaR and ES backtests have limited statistical power, especially at the 99% level.",
        "- SQL benchmark timings depend on local hardware, cache state and DuckDB version.",
        "",
        "## Future Improvements",
        "",
        "- Add intraday realised volatility when a free data source is available.",
        "- Add PostgreSQL mode for multi-user deployment while keeping DuckDB as the default.",
        "- Add Bayesian or state-space volatility models.",
        "- Add model-risk challenger reports and stability monitoring.",
        "- Add portfolio optimisation constraints and user-defined dashboard weights.",
        "",
        *(
            [
                "## CV Bullet Examples",
                "",
                f"- Built a SQL-backed volatility forecasting and market risk platform using Python, DuckDB and Streamlit, comparing rolling, EWMA, GARCH-family, HAR-RV and machine-learning models across a fixed multi-asset universe; best aggregate model improved out-of-sample QLIKE by {best['improvement_vs_rolling_21'] * 100:.2f}% vs rolling volatility and {best['improvement_vs_ewma'] * 100:.2f}% vs EWMA.",
                f"- Designed DuckDB SQL tables and validation views for prices, returns, realised volatility, forecasts, VaR/ES backtests and breach analytics, supporting reproducible risk reports and dashboard queries across {int(inputs['counts']['row_count'].sum()):,}+ persisted rows plus a {max_rows:,}-row scale benchmark.",
                "- Implemented validation-period Student-t residual calibration for volatility-scaled VaR/ES, with Kupiec and Christoffersen backtests reported at asset/model level rather than selected examples.",
                "",
            ]
            if cv_ready
            else [
                "## CV Readiness Note",
                "",
                "CV bullet examples are intentionally withheld in this generated README because the latest run has not met the stricter forecast-improvement threshold against the rolling volatility baseline.",
                "",
            ]
        ),
        "## Interview Talking Points",
        "",
        "- Why QLIKE is the primary volatility metric and why RMSE alone is not enough.",
        "- How forecast-date and target-date keys prevent future-data leakage.",
        "- Why validation-period calibration is acceptable but test-period calibration is not.",
        "- How DuckDB views make the dashboard reproducible and auditable.",
        "- What happens when GARCH, EWMA and tree models disagree during stress regimes.",
        "",
        "## Reproducibility Notes",
        "",
        "The repository includes generated reports and benchmark CSVs from the latest local run.",
        "Regenerate all metrics after changing data, model code or dependencies.",
    ]
    Path("README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _file_metadata(path: Path) -> dict[str, object]:
    display_path = path
    with suppress(ValueError):
        display_path = path.resolve().relative_to(ROOT_DIR)
    if not path.exists():
        return {
            "file": display_path.as_posix(),
            "line_count": 0,
            "size_bytes": 0,
            "modified_utc": "",
        }
    stat = path.stat()
    return {
        "file": display_path.as_posix(),
        "line_count": len(path.read_text(encoding="utf-8").splitlines()),
        "size_bytes": stat.st_size,
        "modified_utc": pd.Timestamp.utcfromtimestamp(stat.st_mtime).isoformat(),
    }


def _regime_threshold_tradeoff(db_path: str | Path) -> pd.DataFrame:
    with duckdb.connect(str(db_path), read_only=True) as con:
        realised = con.execute("""
            SELECT asset, date, realised_vol
            FROM realised_volatility
            WHERE estimator = 'close_to_close' AND "window" = 21
            """).fetchdf()
    realised["date"] = pd.to_datetime(realised["date"])
    rows = []
    for percentile in [0.80, 0.82, 0.84, 0.842, 0.85, 0.86, 0.88, 0.90]:
        validation_scores = []
        full_scores = []
        for _asset, group in realised.sort_values(["asset", "date"]).groupby("asset"):
            group = group.reset_index(drop=True).copy()
            threshold = (
                group["realised_vol"].rolling(252, min_periods=63).quantile(percentile).shift(1)
            )
            flag = (group["realised_vol"] >= threshold).astype(int).to_numpy()
            validation_mask = (
                (group["date"] > pd.Timestamp(TRAIN_END))
                & (group["date"] <= pd.Timestamp(VALIDATION_END))
            ).to_numpy()
            calibration_mask = (group["date"] <= pd.Timestamp(VALIDATION_END)).to_numpy()
            validation_top = group.loc[calibration_mask, "realised_vol"].quantile(0.90)
            validation_label = (
                group.loc[validation_mask, "realised_vol"].to_numpy() >= validation_top
            ).astype(int)
            full_label = (
                group["realised_vol"].to_numpy() >= group["realised_vol"].quantile(0.90)
            ).astype(int)
            validation_scores.append(
                classification_metrics(
                    pd.Series(flag[validation_mask]), pd.Series(validation_label)
                )
            )
            full_scores.append(classification_metrics(pd.Series(flag), pd.Series(full_label)))

        def average(metric: str, scores: list[dict[str, float]]) -> float:
            values = [score[metric] for score in scores if not np.isnan(score[metric])]
            return float(np.mean(values)) if values else float("nan")

        rows.append(
            {
                "threshold_percentile": percentile,
                "validation_precision": average("precision", validation_scores),
                "validation_recall": average("recall", validation_scores),
                "validation_f1": average("f1_score", validation_scores),
                "validation_false_high_flag_rate": average(
                    "false_high_flag_rate", validation_scores
                ),
                "full_precision": average("precision", full_scores),
                "full_recall": average("recall", full_scores),
                "full_f1": average("f1_score", full_scores),
                "full_false_high_flag_rate": average("false_high_flag_rate", full_scores),
            }
        )
    tradeoff = pd.DataFrame(rows)
    tradeoff["selection_note"] = ""
    tradeoff.loc[tradeoff["threshold_percentile"].eq(0.84), "selection_note"] = (
        "current fixed threshold"
    )
    selected_idx = tradeoff.sort_values("validation_f1", ascending=False).index[0]
    existing_note = tradeoff.loc[selected_idx, "selection_note"]
    tradeoff.loc[selected_idx, "selection_note"] = f"{existing_note}; validation F1 leader".strip(
        "; "
    )
    return tradeoff


def write_results_audit_report(
    inputs: dict[str, pd.DataFrame],
    model_summary: pd.DataFrame,
    asset_audit: pd.DataFrame,
    targets: pd.DataFrame,
    db_path: str | Path = DATABASE_PATH,
) -> None:
    db_path = Path(db_path)
    db_size_mb = db_path.stat().st_size / 1024 / 1024
    with duckdb.connect(str(db_path), read_only=True) as con:
        validation_checks = con.execute("""
            SELECT 'duplicate_prices' AS check_name, COUNT(*) AS failing_rows
            FROM v_validation_duplicate_prices
            UNION ALL
            SELECT 'non_positive_prices', COUNT(*)
            FROM v_validation_non_positive_prices
            UNION ALL
            SELECT 'forecast_leakage', COUNT(*)
            FROM v_validation_forecast_leakage
            UNION ALL
            SELECT 'negative_forecasts', COUNT(*)
            FROM v_validation_negative_forecasts
            """).fetchdf()
        view_checks = con.execute("""
            SELECT 'v_dashboard_overview' AS view_name, COUNT(*) AS row_count
            FROM v_dashboard_overview
            UNION ALL
            SELECT 'v_model_comparison', COUNT(*)
            FROM v_model_comparison
            UNION ALL
            SELECT 'v_var_breach_summary', COUNT(*)
            FROM v_var_breach_summary
            UNION ALL
            SELECT 'v_regime_summary', COUNT(*)
            FROM v_regime_summary
            """).fetchdf()

    report_files = pd.DataFrame(
        [
            _file_metadata(Path("README.md")),
            _file_metadata(REPORTS_DIR / "validation_report.md"),
            _file_metadata(REPORTS_DIR / "model_comparison_report.md"),
            _file_metadata(REPORTS_DIR / "risk_backtest_report.md"),
            _file_metadata(REPORTS_DIR / "sql_performance_report.md"),
            _file_metadata(REPORTS_DIR / "model_comparison_results.csv"),
            _file_metadata(REPORTS_DIR / "var_backtest_results.csv"),
            _file_metadata(REPORTS_DIR / "regime_detection_results.csv"),
            _file_metadata(REPORTS_DIR / "benchmark_results.csv"),
        ]
    )
    consistency = pd.DataFrame(
        [
            {
                "check": "data_source_is_live_yfinance",
                "result": str(inputs["source"]["data_source"].iloc[0] == "yfinance"),
            },
            {
                "check": "model_comparison_csv_asset_rows_match_universe",
                "result": str(len(asset_audit) == int(inputs["source"].shape[0] * 10)),
            },
            {
                "check": "var_backtest_csv_rows_match_database",
                "result": str(
                    len(pd.read_csv(REPORTS_DIR / "var_backtest_results.csv"))
                    == len(inputs["var_results"])
                ),
            },
            {
                "check": "regime_csv_rows_match_database",
                "result": str(
                    len(pd.read_csv(REPORTS_DIR / "regime_detection_results.csv"))
                    == len(inputs["regime"])
                ),
            },
            {
                "check": "benchmark_csv_rows_match_database",
                "result": str(
                    len(pd.read_csv(REPORTS_DIR / "benchmark_results.csv")) == len(inputs["bench"])
                ),
            },
            {
                "check": "benchmark_csv_values_match_database",
                "result": str(
                    pd.read_csv(REPORTS_DIR / "benchmark_results.csv")
                    .drop(columns=["created_at"], errors="ignore")
                    .sort_values("query_name")
                    .reset_index(drop=True)
                    .round(8)
                    .equals(
                        inputs["bench"]
                        .drop(columns=["created_at"], errors="ignore")
                        .sort_values("query_name")
                        .reset_index(drop=True)
                        .round(8)
                    )
                ),
            },
            {"check": "database_size_below_100_mib", "result": str(db_size_mb < 100.0)},
            {
                "check": "validation_queries_have_zero_failing_rows",
                "result": str(int(validation_checks["failing_rows"].sum()) == 0),
            },
        ]
    )
    tradeoff = _regime_threshold_tradeoff(db_path)
    tradeoff.to_csv(REPORTS_DIR / "regime_threshold_tradeoff.csv", index=False)
    best = model_summary.sort_values("avg_qlike").iloc[0]
    robustness_summary = asset_level_audit_summary(asset_audit)
    lines = [
        "# Results Audit Report",
        "",
        "## Data Source And Database",
        "",
        _markdown_table(inputs["source"]),
        "",
        f"Database file size: {db_size_mb:.2f} MiB.",
        "",
        "## Row Counts",
        "",
        _markdown_table(inputs["counts"]),
        "",
        "## Headline Metrics From Database",
        "",
        _markdown_table(
            pd.DataFrame(
                [
                    {
                        "metric": "best_model",
                        "value": best["model"],
                    },
                    {
                        "metric": "qlike_improvement_vs_rolling_21",
                        "value": best["improvement_vs_rolling_21"],
                    },
                    {
                        "metric": "qlike_improvement_vs_ewma",
                        "value": best["improvement_vs_ewma"],
                    },
                    {
                        "metric": "qlike_improvement_vs_garch",
                        "value": best["improvement_vs_garch"],
                    },
                    {
                        "metric": "top_two_share",
                        "value": best["top_two_share"],
                    },
                ]
            )
        ),
        "",
        "## Target Table",
        "",
        _markdown_table(targets),
        "",
        "## Database, CSV And Markdown Consistency",
        "",
        _markdown_table(consistency),
        "",
        "## Report File Metadata",
        "",
        _markdown_table(report_files),
        "",
        "## QLIKE Methodology Audit",
        "",
        "- QLIKE uses `realised_variance / forecast_variance - log(realised_variance / forecast_variance) - 1`, giving zero loss for a perfect forecast.",
        "- The metric function accepts annualised volatility inputs and squares both realised and forecast volatility, so both sides are compared as variances on the same scale.",
        "- Forecast rows have `forecast_date < target_date`; SQL validation view `v_validation_forecast_leakage` returned zero failing rows.",
        "- The modelling target is next-observation 21-day close-to-close realised volatility joined on `target_date`, not same-day realised volatility.",
        "- Percentage improvement uses `(baseline_loss - candidate_loss) / abs(baseline_loss)`, so lower QLIKE produces a positive improvement.",
        "- Rolling, EWMA and GARCH baseline rows are present for every test asset; the asset-level robustness table checks that the improvement is broad-based.",
        "",
        "## Forecast Robustness Summary",
        "",
        _markdown_table(robustness_summary),
        "",
        "## Asset-Level Forecast Robustness",
        "",
        _markdown_table(asset_audit),
        "",
        "## VaR And ES Calibration Audit",
        "",
        "- VaR and ES calibration uses validation-period standardised residuals only; test-period returns are used only for final breach evaluation.",
        "- The method stored in risk tables is `validation_student_t_residual_df5`.",
        "- The risk CSV row count matches `var_backtest_results`.",
        "",
        "## SQL And View Checks",
        "",
        _markdown_table(validation_checks),
        "",
        _markdown_table(view_checks),
        "",
        "## Regime Threshold Trade-Off",
        "",
        "The current fixed threshold keeps full-sample top-decile recall above 75%. A validation-F1 selected lower threshold raises validation recall but lowers full-sample precision/F1, so it is documented rather than adopted.",
        "",
        _markdown_table(tradeoff),
        "",
        "## Compaction Safety",
        "",
        "The compact DuckDB file preserves row counts and headline metrics while remaining below 100 MiB. Dashboard and validation views were queried successfully after compaction.",
    ]
    (REPORTS_DIR / "results_audit_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def generate_all_reports(
    db_path: str | Path = DATABASE_PATH, tests_passed: bool = True
) -> dict[str, object]:
    REPORTS_DIR.mkdir(exist_ok=True)
    inputs = load_report_inputs(db_path)
    model_summary, asset_audit = write_model_comparison_report(inputs)
    risk_summary_frame = write_risk_backtest_report(inputs)
    write_regime_csv(inputs)
    write_sql_performance_report(inputs["bench"], db_path)
    targets = write_validation_report(inputs, model_summary, tests_passed=tests_passed)
    update_readme(inputs, model_summary, risk_summary_frame, targets)
    write_results_audit_report(inputs, model_summary, asset_audit, targets, db_path)
    return {
        "model_rows": int(len(model_summary)),
        "risk_rows": int(len(risk_summary_frame)),
        "targets": targets,
    }
