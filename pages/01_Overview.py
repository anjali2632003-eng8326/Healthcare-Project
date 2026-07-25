"""
Page 1: Overview - Executive KPIs & Trend Analysis
"""
import os
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Overview | Healthcare Dashboard", page_icon="+", layout="wide")

css_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "style.css")
with open(css_path, "r", encoding="utf-8") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

from analytics.overview import (
    get_kpis, get_monthly_trend, get_yearly_trend,
    get_condition_summary, get_recent_records,
)
from visualizations.charts import area_chart, bar_chart, line_chart, donut_chart
from visualizations.kpis import metric_row, section_header

# Header
st.markdown("""
<div class="hero-banner">
    <h1 style="color:#f1f5f9;font-size:28px;font-weight:800;margin:0 0 6px">
        Executive Overview
    </h1>
    <p style="color:#93c5fd;margin:0;font-size:14px">
        High-level KPIs and trend analysis across the entire healthcare dataset
    </p>
</div>
""", unsafe_allow_html=True)

# Sidebar filters
with st.sidebar:
    st.markdown("### Filters")
    year_range = st.slider("Year Range", 2019, 2024, (2019, 2024))

# Load data
with st.spinner("Loading data..."):
    try:
        kpis       = get_kpis()
        monthly    = get_monthly_trend()
        yearly     = get_yearly_trend()
        conditions = get_condition_summary()
        recent     = get_recent_records(50)
        data_ok    = True
    except Exception as e:
        st.error(f"Database error: {e}")
        st.info("Make sure the dataset is loaded: `python database/loader.py`")
        data_ok = False

if not data_ok:
    st.stop()

# KPI Row 1
section_header("Key Performance Indicators", "Core metrics across the entire dataset")

metric_row([
    {"label": "Total Records",    "value": f"{int(kpis['total_records']):,}",   "icon": ""},
    {"label": "Unique Patients",  "value": f"{int(kpis['unique_patients']):,}", "icon": ""},
    {"label": "Total Hospitals",  "value": f"{int(kpis['total_hospitals']):,}", "icon": ""},
    {"label": "Total Doctors",    "value": f"{int(kpis['total_doctors']):,}",   "icon": ""},
])

st.markdown("<br>", unsafe_allow_html=True)

metric_row([
    {"label": "Total Revenue",       "value": f"Rs.{kpis['total_revenue']/1e6:.1f}M",  "icon": ""},
    {"label": "Avg Billing",         "value": f"Rs.{kpis['avg_billing']:,.0f}",         "icon": ""},
    {"label": "Avg Length of Stay",  "value": f"{kpis['avg_los']:.1f} days",            "icon": ""},
    {"label": "Abnormal Test Rate",  "value": f"{kpis['abnormal_rate']:.1f}%",
     "delta": "needs attention", "delta_color": "red", "icon": ""},
])

st.markdown("---")

# Monthly trend
section_header("Monthly Admissions & Revenue Trend")

monthly["month"] = pd.to_datetime(monthly["month"])
col1, col2 = st.columns(2)
with col1:
    fig = area_chart(monthly, x="month", y="admissions", title="Monthly Admissions")
    st.plotly_chart(fig, use_container_width=True)
with col2:
    fig = area_chart(monthly, x="month", y="revenue", title="Monthly Revenue (Rs.)")
    st.plotly_chart(fig, use_container_width=True)

col3, col4 = st.columns(2)
with col3:
    fig = line_chart(monthly, x="month", y="avg_billing",
                     title="Avg Billing Amount Over Time (Rs.)")
    st.plotly_chart(fig, use_container_width=True)
with col4:
    fig = line_chart(monthly, x="month", y="avg_los",
                     title="Avg Length of Stay Over Time (days)")
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# Condition summary
section_header("Top Medical Conditions", "Cases, average billing & abnormal test rates")

col5, col6 = st.columns([1.4, 1])
with col5:
    fig = bar_chart(
        conditions.head(10),
        x="medical_condition", y="count",
        title="Cases by Medical Condition",
        color_discrete_sequence=["#2563EB"],
    )
    fig.update_layout(xaxis_tickangle=-30)
    st.plotly_chart(fig, use_container_width=True)
with col6:
    fig = donut_chart(
        conditions,
        names="medical_condition",
        values="count",
        title="Condition Distribution",
    )
    st.plotly_chart(fig, use_container_width=True)

fig = bar_chart(
    conditions.sort_values("avg_billing", ascending=True),
    x="avg_billing", y="medical_condition",
    title="Average Billing Amount by Condition (Rs.)",
    orientation="h",
    color_discrete_sequence=["#10B981"],
)
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# Recent records table
section_header("Recent Admissions", "Latest 50 patient records")

col_a, col_b, col_c = st.columns([1, 1, 4])
with col_a:
    cond_filter = st.selectbox("Filter Condition",
        ["All"] + sorted(recent["medical_condition"].unique().tolist()))
with col_b:
    result_filter = st.selectbox("Test Result",
        ["All"] + sorted(recent["test_results"].dropna().unique().tolist()))

filtered = recent.copy()
if cond_filter  != "All": filtered = filtered[filtered["medical_condition"] == cond_filter]
if result_filter != "All": filtered = filtered[filtered["test_results"] == result_filter]

st.dataframe(
    filtered.style.map(
        lambda v: "color: #10B981" if v == "Normal"
             else "color: #EF4444" if v == "Abnormal"
             else "color: #F59E0B" if v == "Inconclusive"
             else "",
        subset=["test_results"]
    ),
    use_container_width=True, height=300,
)

# Download
st.download_button(
    "Download Recent Records (CSV)",
    data      = filtered.to_csv(index=False),
    file_name = "recent_records.csv",
    mime      = "text/csv",
)
