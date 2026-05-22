from __future__ import annotations

import pandas as pd


def status(pass_condition: bool) -> str:
    return "pass" if pass_condition else "fail"


def target_table(
    model_summary: pd.DataFrame,
    var_results: pd.DataFrame,
    regime_results: pd.DataFrame,
    benchmark_results: pd.DataFrame,
    tests_passed: bool = True,
) -> pd.DataFrame:
    best = model_summary.sort_values("avg_qlike").iloc[0] if not model_summary.empty else None
    top_two = float(best["top_two_share"]) if best is not None else float("nan")
    imp_roll = float(best["improvement_vs_rolling_21"]) if best is not None else float("nan")
    imp_ewma = float(best["improvement_vs_ewma"]) if best is not None else float("nan")
    imp_garch = float(best["improvement_vs_garch"]) if best is not None else float("nan")
    var95 = var_results[var_results["confidence_level"] == 0.95]
    var99 = var_results[var_results["confidence_level"] == 0.99]
    breach95 = float(var95["breach_rate"].mean()) if not var95.empty else float("nan")
    breach99 = float(var99["breach_rate"].mean()) if not var99.empty else float("nan")
    kupiec_share = (
        float((var_results["kupiec_p_value"] > 0.05).mean())
        if not var_results.empty
        else float("nan")
    )
    christ_share = (
        float((var_results["christoffersen_p_value"] > 0.05).mean())
        if not var_results.empty
        else float("nan")
    )
    es_ratio = (
        float(var_results["es_tail_loss_ratio"].mean()) if not var_results.empty else float("nan")
    )
    capture = (
        float(regime_results["top_decile_capture"].mean())
        if not regime_results.empty
        else float("nan")
    )
    precision = (
        float(regime_results["precision"].mean())
        if "precision" in regime_results and not regime_results.empty
        else float("nan")
    )
    f1_score = (
        float(regime_results["f1_score"].mean())
        if "f1_score" in regime_results and not regime_results.empty
        else float("nan")
    )
    false_flag = (
        float(regime_results["false_high_flag_rate"].mean())
        if "false_high_flag_rate" in regime_results and not regime_results.empty
        else float("nan")
    )
    scale_rows = (
        int(benchmark_results["benchmark_rows"].max()) if not benchmark_results.empty else 0
    )
    dashboard_queries = [
        "dashboard_overview",
        "model_comparison",
        "var_breach_summary",
        "asset_risk_summary",
    ]
    max_dashboard = (
        float(
            benchmark_results[benchmark_results["query_name"].isin(dashboard_queries)][
                "p95_ms"
            ].max()
        )
        if not benchmark_results.empty
        else float("nan")
    )
    rows = [
        (
            "QLIKE improvement vs rolling vol >= 12%",
            f"{imp_roll * 100:.2f}%",
            status(imp_roll >= 0.12),
        ),
        ("QLIKE improvement vs EWMA >= 5%", f"{imp_ewma * 100:.2f}%", status(imp_ewma >= 0.05)),
        (
            "QLIKE improvement vs GARCH >= 5%",
            f"{imp_garch * 100:.2f}%",
            status(imp_garch >= 0.05),
        ),
        ("Best/top-2 model across >= 70% assets", f"{top_two * 100:.2f}%", status(top_two >= 0.70)),
        (
            "95% VaR breach rate 4.7%-5.3%",
            f"{breach95 * 100:.2f}%",
            status(0.047 <= breach95 <= 0.053),
        ),
        (
            "99% VaR breach rate 0.8%-1.2%",
            f"{breach99 * 100:.2f}%",
            status(0.008 <= breach99 <= 0.012),
        ),
        (
            "Kupiec not rejected for most assets",
            f"{kupiec_share * 100:.2f}%",
            status(kupiec_share >= 0.50),
        ),
        (
            "Christoffersen not rejected for most assets",
            f"{christ_share * 100:.2f}%",
            status(christ_share >= 0.50),
        ),
        ("ES tail-loss ratio 0.9-1.1", f"{es_ratio:.3f}", status(0.90 <= es_ratio <= 1.10)),
        ("Top-decile vol capture >= 75%", f"{capture * 100:.2f}%", status(capture >= 0.75)),
        (
            "High-vol precision >= 40%",
            f"{precision * 100:.2f}%",
            status(precision >= 0.40),
        ),
        ("High-vol F1 >= 50%", f"{f1_score * 100:.2f}%", status(f1_score >= 0.50)),
        (
            "False high-vol flag rate <= 60%",
            f"{false_flag * 100:.2f}%",
            status(false_flag <= 0.60),
        ),
        ("SQL handles 1m+ rows", f"{scale_rows:,}", status(scale_rows >= 1_000_000)),
        (
            "Dashboard queries < 1 sec",
            f"{max_dashboard:.2f} ms p95",
            status(max_dashboard < 1000.0),
        ),
        ("Tests pass", "passed" if tests_passed else "not recorded", status(tests_passed)),
    ]
    return pd.DataFrame(rows, columns=["Target", "Result", "Status"])
