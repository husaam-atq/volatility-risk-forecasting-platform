from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"

for path in (ROOT, SRC):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

import duckdb
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from app.styles import dashboard_css
from app.ui_components import metric_card, section_title
from volatility_platform.config import DATABASE_PATH

st.set_page_config(
    page_title="Volatility Risk Forecasting Platform",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.markdown(dashboard_css(), unsafe_allow_html=True)


@st.cache_data(ttl=30)
def query(sql: str) -> pd.DataFrame:
    with duckdb.connect(str(DATABASE_PATH), read_only=True) as con:
        return con.execute(sql).fetchdf()


def database_ready() -> bool:
    return DATABASE_PATH.exists()


st.title("Volatility Risk Forecasting Platform")
st.caption(
    "SQL-backed volatility forecasts, VaR/ES backtests, regime detection and portfolio risk analytics."
)

if not database_ready():
    st.warning(
        "Database not found. Run `python examples/build_database.py` and the pipeline examples first."
    )
    st.stop()

assets = query("SELECT DISTINCT asset FROM clean_prices ORDER BY asset")["asset"].tolist()
models = query("SELECT DISTINCT model FROM volatility_forecasts ORDER BY model")["model"].tolist()
section = st.sidebar.radio(
    "Section",
    [
        "Overview",
        "SQL Data Pipeline",
        "Asset Explorer",
        "Realised Volatility",
        "Forecast Model Comparison",
        "VaR and Expected Shortfall Backtesting",
        "Breach Analysis",
        "Regime Detection",
        "Portfolio Risk",
        "SQL Query Performance",
        "Validation Summary",
        "Limitations",
    ],
)
asset = st.sidebar.selectbox("Asset", assets, index=0)
model = st.sidebar.selectbox("Model", models, index=0 if models else None)
date_bounds = query("SELECT MIN(date) AS min_date, MAX(date) AS max_date FROM clean_prices").iloc[0]
date_range = st.sidebar.date_input(
    "Date range",
    value=(
        pd.to_datetime(date_bounds["min_date"]).date(),
        pd.to_datetime(date_bounds["max_date"]).date(),
    ),
)
if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = (
        pd.to_datetime(date_bounds["min_date"]).date(),
        pd.to_datetime(date_bounds["max_date"]).date(),
    )

if section == "Overview":
    overview = query("SELECT * FROM v_dashboard_overview").iloc[0]
    cols = st.columns(4)
    with cols[0]:
        metric_card("Assets", f"{int(overview.asset_count)}", "fixed universe")
    with cols[1]:
        metric_card("Price rows", f"{int(overview.clean_price_rows):,}", "clean_prices")
    with cols[2]:
        metric_card("Forecast rows", f"{int(overview.forecast_rows):,}", "volatility_forecasts")
    with cols[3]:
        metric_card("Breach rows", f"{int(overview.breach_rows):,}", "breach_events")
    section_title("Model Leaderboard")
    st.dataframe(
        query("SELECT * FROM v_model_rank_summary ORDER BY avg_qlike"), use_container_width=True
    )

elif section == "SQL Data Pipeline":
    section_title("Database Row Counts")
    st.dataframe(
        query("""
            SELECT 'asset_universe' AS table_name, COUNT(*) AS rows FROM asset_universe
            UNION ALL SELECT 'clean_prices', COUNT(*) FROM clean_prices
            UNION ALL SELECT 'daily_returns', COUNT(*) FROM daily_returns
            UNION ALL SELECT 'realised_volatility', COUNT(*) FROM realised_volatility
            UNION ALL SELECT 'volatility_features', COUNT(*) FROM volatility_features
            UNION ALL SELECT 'volatility_forecasts', COUNT(*) FROM volatility_forecasts
            UNION ALL SELECT 'breach_events', COUNT(*) FROM breach_events
            UNION ALL SELECT 'sql_query_benchmarks', COUNT(*) FROM sql_query_benchmarks
            ORDER BY rows DESC
            """),
        use_container_width=True,
    )
    section_title("Asset Coverage")
    st.dataframe(query("SELECT * FROM v_asset_coverage"), use_container_width=True)

elif section == "Asset Explorer":
    prices = query(f"""
        SELECT date, adj_close
        FROM clean_prices
        WHERE asset = '{asset}' AND date BETWEEN DATE '{start_date}' AND DATE '{end_date}'
        ORDER BY date
        """)
    fig = px.line(prices, x="date", y="adj_close", title=f"{asset} adjusted close")
    fig.update_layout(template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(
        query(f"SELECT * FROM v_asset_risk_summary WHERE asset = '{asset}'"),
        use_container_width=True,
    )

elif section == "Realised Volatility":
    rv = query(f"""
        SELECT date, estimator, "window" AS window, realised_vol
        FROM realised_volatility
        WHERE asset = '{asset}' AND "window" IN (21, 63)
          AND date BETWEEN DATE '{start_date}' AND DATE '{end_date}'
        ORDER BY date
        """)
    fig = px.line(
        rv,
        x="date",
        y="realised_vol",
        color="estimator",
        line_dash="window",
        title=f"{asset} realised volatility",
    )
    fig.update_layout(template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

elif section == "Forecast Model Comparison":
    comp = query("SELECT * FROM v_model_comparison ORDER BY asset, rank_qlike")
    st.dataframe(comp, use_container_width=True)
    fvr = query(f"""
        SELECT target_date, realised_vol, forecast_vol
        FROM v_forecast_vs_realised
        WHERE asset = '{asset}' AND model = '{model}'
          AND target_date BETWEEN DATE '{start_date}' AND DATE '{end_date}'
        ORDER BY target_date
        """)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=fvr["target_date"], y=fvr["realised_vol"], name="Realised vol"))
    fig.add_trace(go.Scatter(x=fvr["target_date"], y=fvr["forecast_vol"], name="Forecast vol"))
    fig.update_layout(template="plotly_dark", title=f"{asset}: realised vs forecast volatility")
    st.plotly_chart(fig, use_container_width=True)

elif section == "VaR and Expected Shortfall Backtesting":
    summary = query(f"""
        SELECT *
        FROM v_var_breach_summary
        WHERE asset = '{asset}' AND model = '{model}'
        ORDER BY confidence_level
        """)
    st.dataframe(summary, use_container_width=True)
    breaches = query(f"""
        SELECT target_date, realised_return, var_return, es_return, breach, confidence_level
        FROM breach_events
        WHERE asset = '{asset}' AND model = '{model}' AND confidence_level = 0.95
          AND target_date BETWEEN DATE '{start_date}' AND DATE '{end_date}'
        ORDER BY target_date
        """)
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=breaches["target_date"], y=breaches["realised_return"], name="Return", mode="lines"
        )
    )
    fig.add_trace(
        go.Scatter(
            x=breaches["target_date"], y=breaches["var_return"], name="95% VaR", mode="lines"
        )
    )
    fig.add_trace(
        go.Scatter(x=breaches["target_date"], y=breaches["es_return"], name="95% ES", mode="lines")
    )
    fig.update_layout(template="plotly_dark", title=f"{asset}: VaR and ES timeline")
    st.plotly_chart(fig, use_container_width=True)

elif section == "Breach Analysis":
    st.dataframe(
        query("SELECT * FROM v_breach_clustering ORDER BY max_cluster_length DESC"),
        use_container_width=True,
    )

elif section == "Regime Detection":
    regimes = query(f"""
        SELECT date, realised_vol, regime, high_vol_flag, is_top_decile
        FROM regime_labels
        WHERE asset = '{asset}' AND date BETWEEN DATE '{start_date}' AND DATE '{end_date}'
        ORDER BY date
        """)
    fig = px.scatter(
        regimes, x="date", y="realised_vol", color="regime", title=f"{asset} volatility regimes"
    )
    fig.update_layout(template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(
        query(f"SELECT * FROM regime_metrics WHERE asset = '{asset}'"), use_container_width=True
    )

elif section == "Portfolio Risk":
    port = query("SELECT * FROM portfolio_risk ORDER BY date")
    fig = px.line(
        port[port["model"] == model],
        x="date",
        y=["portfolio_return", "var_95", "var_99"],
        title=f"Equal-weight portfolio risk: {model}",
    )
    fig.update_layout(template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(query("SELECT * FROM v_portfolio_risk_summary"), use_container_width=True)

elif section == "SQL Query Performance":
    bench = query("SELECT * FROM sql_query_benchmarks ORDER BY p95_ms")
    st.dataframe(bench, use_container_width=True)
    fig = px.bar(bench, x="query_name", y="p95_ms", title="Query p95 latency")
    fig.update_layout(template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

elif section == "Validation Summary":
    st.dataframe(query("SELECT * FROM data_quality_checks"), use_container_width=True)
    st.dataframe(query("SELECT * FROM v_validation_dashboard_queries"), use_container_width=True)

else:
    st.markdown(Path("docs/limitations.md").read_text(encoding="utf-8"))
