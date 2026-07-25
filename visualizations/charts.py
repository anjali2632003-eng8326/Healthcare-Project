"""
Reusable Plotly chart builders for the healthcare dashboard.
All functions return a plotly.graph_objects.Figure.
"""
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from config.settings import CHART_COLORS

# ── Shared theme ───────────────────────────────────────────────────────────────
LAYOUT_BASE = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", color="#e2e8f0"),
    margin=dict(l=20, r=20, t=50, b=20),
)


def _theme(fig: go.Figure, title: str = "") -> go.Figure:
    fig.update_layout(
        title=dict(text=title, font=dict(size=16, color="#f1f5f9")),
        **LAYOUT_BASE,
        xaxis=dict(gridcolor="#334155", linecolor="#475569"),
        yaxis=dict(gridcolor="#334155", linecolor="#475569"),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#cbd5e1")),
    )
    return fig


# ── Bar Charts ─────────────────────────────────────────────────────────────────
def bar_chart(df: pd.DataFrame, x: str, y: str, title: str = "",
              color: str = None, orientation: str = "v",
              color_discrete_sequence=None) -> go.Figure:
    fig = px.bar(
        df, x=x, y=y,
        color=color,
        orientation=orientation,
        color_discrete_sequence=color_discrete_sequence or CHART_COLORS,
        text_auto=".2s",
    )
    fig.update_traces(
        textfont_size=11,
        marker_line_width=0,
        opacity=0.9,
    )
    return _theme(fig, title)


def grouped_bar(df: pd.DataFrame, x: str, y: str, color: str,
                title: str = "", barmode: str = "group") -> go.Figure:
    fig = px.bar(
        df, x=x, y=y, color=color,
        barmode=barmode,
        color_discrete_sequence=CHART_COLORS,
        text_auto=".2s",
    )
    fig.update_traces(marker_line_width=0, opacity=0.88)
    return _theme(fig, title)


# ── Pie / Donut ────────────────────────────────────────────────────────────────
def donut_chart(df: pd.DataFrame, names: str, values: str,
                title: str = "", hole: float = 0.55) -> go.Figure:
    fig = px.pie(
        df, names=names, values=values,
        hole=hole,
        color_discrete_sequence=CHART_COLORS,
    )
    fig.update_traces(
        textposition="outside",
        textinfo="percent+label",
        marker=dict(line=dict(color="#0f172a", width=2)),
    )
    return _theme(fig, title)


# ── Line Charts ────────────────────────────────────────────────────────────────
def line_chart(df: pd.DataFrame, x: str, y: str | list,
               title: str = "", color: str = None) -> go.Figure:
    if isinstance(y, list):
        fig = go.Figure()
        for i, col in enumerate(y):
            fig.add_trace(go.Scatter(
                x=df[x], y=df[col], mode="lines+markers",
                name=col.replace("_", " ").title(),
                line=dict(color=CHART_COLORS[i % len(CHART_COLORS)], width=2),
                marker=dict(size=5),
            ))
    else:
        fig = px.line(
            df, x=x, y=y, color=color,
            color_discrete_sequence=CHART_COLORS,
            markers=True,
        )
    return _theme(fig, title)


# ── Area Chart ─────────────────────────────────────────────────────────────────
def area_chart(df: pd.DataFrame, x: str, y: str,
               title: str = "") -> go.Figure:
    fig = px.area(
        df, x=x, y=y,
        color_discrete_sequence=[CHART_COLORS[0]],
    )
    fig.update_traces(line=dict(width=2), fillcolor="rgba(37,99,235,0.25)")
    return _theme(fig, title)


# ── Scatter Plot ───────────────────────────────────────────────────────────────
def scatter_chart(df: pd.DataFrame, x: str, y: str,
                  color: str = None, size: str = None,
                  title: str = "", hover_data: list = None) -> go.Figure:
    fig = px.scatter(
        df, x=x, y=y, color=color, size=size,
        hover_data=hover_data or [],
        color_discrete_sequence=CHART_COLORS,
        opacity=0.65,
    )
    fig.update_traces(marker=dict(line=dict(width=0)))
    return _theme(fig, title)


# ── Heatmap ────────────────────────────────────────────────────────────────────
def heatmap(pivot_df: pd.DataFrame, title: str = "",
            colorscale: str = "Blues") -> go.Figure:
    fig = go.Figure(go.Heatmap(
        z=pivot_df.values,
        x=list(pivot_df.columns),
        y=list(pivot_df.index),
        colorscale=colorscale,
        showscale=True,
        text=pivot_df.values,
        texttemplate="%{text}",
        textfont=dict(size=11, color="white"),
    ))
    return _theme(fig, title)


# ── Box Plot ───────────────────────────────────────────────────────────────────
def box_plot(df: pd.DataFrame, x: str, y: str,
             title: str = "", color: str = None) -> go.Figure:
    fig = px.box(
        df, x=x, y=y, color=color or x,
        color_discrete_sequence=CHART_COLORS,
        notched=False,
    )
    fig.update_traces(marker_size=3)
    return _theme(fig, title)


# ── Histogram ─────────────────────────────────────────────────────────────────
def histogram(df: pd.DataFrame, x: str, bins: int = 30,
              color: str = None, title: str = "") -> go.Figure:
    fig = px.histogram(
        df, x=x, nbins=bins, color=color,
        color_discrete_sequence=CHART_COLORS,
        barmode="overlay",
        opacity=0.8,
    )
    fig.update_traces(marker_line_width=0)
    return _theme(fig, title)


# ── Treemap ────────────────────────────────────────────────────────────────────
def treemap(df: pd.DataFrame, path: list, values: str,
            title: str = "", color: str = None) -> go.Figure:
    fig = px.treemap(
        df, path=path, values=values,
        color=color or values,
        color_continuous_scale="Blues",
    )
    fig.update_traces(
        textinfo="label+value",
        marker=dict(line=dict(width=2, color="#0f172a")),
    )
    return _theme(fig, title)


# ── Funnel ─────────────────────────────────────────────────────────────────────
def funnel_chart(df: pd.DataFrame, x: str, y: str,
                 title: str = "") -> go.Figure:
    fig = px.funnel(
        df, x=x, y=y,
        color_discrete_sequence=CHART_COLORS,
    )
    return _theme(fig, title)


# ── Gauge ─────────────────────────────────────────────────────────────────────
def gauge_chart(value: float, title: str = "",
                max_val: float = 100) -> go.Figure:
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=value,
        title={"text": title, "font": {"color": "#e2e8f0", "size": 14}},
        gauge={
            "axis": {"range": [0, max_val], "tickcolor": "#64748b"},
            "bar":  {"color": "#2563EB"},
            "steps": [
                {"range": [0, max_val*0.33], "color": "#0f172a"},
                {"range": [max_val*0.33, max_val*0.66], "color": "#1e3a5f"},
                {"range": [max_val*0.66, max_val], "color": "#1d4ed8"},
            ],
            "threshold": {
                "line": {"color": "#EF4444", "width": 3},
                "thickness": 0.75,
                "value": max_val * 0.8,
            },
        },
        number={"font": {"color": "#f1f5f9"}},
    ))
    fig.update_layout(**LAYOUT_BASE, height=220)
    return fig


# ── Confusion Matrix ──────────────────────────────────────────────────────────
def confusion_matrix_chart(cm: np.ndarray, labels: list,
                            title: str = "Confusion Matrix") -> go.Figure:
    fig = go.Figure(go.Heatmap(
        z=cm,
        x=labels, y=labels,
        colorscale="Blues",
        showscale=False,
        text=cm,
        texttemplate="%{text}",
        textfont=dict(size=14, color="white"),
    ))
    fig.update_layout(
        xaxis_title="Predicted", yaxis_title="Actual",
        **LAYOUT_BASE,
    )
    return _theme(fig, title)
