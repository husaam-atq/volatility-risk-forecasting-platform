from __future__ import annotations


def dashboard_css() -> str:
    return """
<style>
:root {
    --bg: #070b12;
    --panel: #101826;
    --panel-2: #121f2f;
    --text: #edf5ff;
    --muted: #8da0b6;
    --accent: #35d0ba;
    --accent-2: #7aa7ff;
    --danger: #ff5c7a;
}
.stApp { background: radial-gradient(circle at top left, #122033 0%, #070b12 32%, #070b12 100%); color: var(--text); }
section[data-testid="stSidebar"] { background: #0b111b; border-right: 1px solid rgba(255,255,255,0.06); }
.metric-card {
    background: linear-gradient(180deg, rgba(18,31,47,0.96), rgba(12,18,28,0.96));
    border: 1px solid rgba(122,167,255,0.18);
    border-radius: 8px;
    padding: 16px 18px;
    box-shadow: 0 0 24px rgba(53,208,186,0.06);
}
.metric-label { color: var(--muted); font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0; }
.metric-value { color: var(--text); font-size: 1.5rem; font-weight: 700; margin-top: 4px; }
.metric-sub { color: var(--muted); font-size: 0.82rem; margin-top: 2px; }
.section-title { font-size: 1.25rem; font-weight: 700; color: var(--text); margin: 18px 0 10px; }
.status-pass { color: var(--accent); font-weight: 700; }
.status-fail { color: var(--danger); font-weight: 700; }
div[data-testid="stMetric"] {
    background: rgba(16,24,38,0.94);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 8px;
    padding: 12px;
}
</style>
"""
