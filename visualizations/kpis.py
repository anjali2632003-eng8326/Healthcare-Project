"""
KPI metric card renderer using Streamlit.
"""
import streamlit as st


def kpi_card(label: str, value: str, delta: str = "",
             delta_color: str = "normal", icon: str = "") -> None:
    delta_html = ""
    if delta:
        arrow = "↑" if delta_color in ("normal","green") else "↓"
        color = "#10B981" if delta_color in ("normal","green") else "#EF4444"
        delta_html = f'<div style="color:{color};font-size:13px;margin-top:4px">{arrow} {delta}</div>'

    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid #334155;
        border-radius: 14px;
        padding: 20px 24px;
        text-align: center;
        box-shadow: 0 4px 24px rgba(0,0,0,0.4);
        transition: transform 0.2s;
    ">
        <div style="font-size:28px;margin-bottom:6px">{icon}</div>
        <div style="color:#94a3b8;font-size:12px;text-transform:uppercase;
                    letter-spacing:1.5px;font-weight:600">{label}</div>
        <div style="color:#f1f5f9;font-size:28px;font-weight:700;
                    margin-top:8px;line-height:1.1">{value}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)


def metric_row(metrics: list[dict]) -> None:
    """
    Renders a row of KPI cards.
    Each dict: {label, value, delta?, delta_color?, icon?}
    """
    cols = st.columns(len(metrics))
    for col, m in zip(cols, metrics):
        with col:
            kpi_card(
                label       = m.get("label",""),
                value       = m.get("value",""),
                delta       = m.get("delta",""),
                delta_color = m.get("delta_color","normal"),
                icon        = m.get("icon",""),
            )


def section_header(title: str, subtitle: str = "") -> None:
    st.markdown(f"""
    <div style="margin: 24px 0 16px 0; border-left: 4px solid #2563EB; padding-left:14px">
        <h3 style="color:#f1f5f9;margin:0;font-size:20px">{title}</h3>
        {"<p style='color:#94a3b8;font-size:13px;margin:4px 0 0'>" + subtitle + "</p>" if subtitle else ""}
    </div>
    """, unsafe_allow_html=True)


def status_badge(label: str, color: str = "#2563EB") -> str:
    return (
        f'<span style="background:{color};color:white;padding:3px 10px;'
        f'border-radius:999px;font-size:11px;font-weight:600">{label}</span>'
    )
