from __future__ import annotations

import plotly.graph_objects as go


def empty_figure(title: str = "No data") -> go.Figure:
    fig = go.Figure()
    fig.update_layout(title=title, template="plotly_dark")
    return fig
