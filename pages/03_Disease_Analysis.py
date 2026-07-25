"""
Page 3: Disease Analysis
"""
import os
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Disease Analysis | Healthcare Dashboard", page_icon="🦠", layout="wide")
css_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "style.css")
with open(css_path, "r", encoding="utf-8") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

from analytics.disease_analytics import (
    get_top_conditions, get_condition_trend, get_condition_by_age_group,
    get_medication_distribution, get_medication_summary,
    get_test_results_by_condition, get_condition_severity_proxy,
)
from visualizations.charts import (
    bar_chart, donut_chart, grouped_bar, line_chart, treemap, scatter_chart
)
from visualizations.kpis import section_header, metric_row

# Header
st.markdown("""
<div class="hero-banner">
    <h1 style="color:#f1f5f9;font-size:28px;font-weight:800;margin:0 0 6px">
        🦠 Disease &amp; Medical Condition Analysis
    </h1>
    <p style="color:#93c5fd;margin:0;font-size:14px">
        Diagnoses, medications, test results &amp; disease burden analysis
    </p>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 🔍 Filters")
    top_n = st.slider("Top N Conditions", 3, 10, 6)

with st.spinner("Loading disease data..."):
    try:
        top_cond  = get_top_conditions(10)
        trend_df  = get_condition_trend()
        age_cond  = get_condition_by_age_group()
        med_dist  = get_medication_distribution()
        med_sum   = get_medication_summary()
        test_res  = get_test_results_by_condition()
        severity  = get_condition_severity_proxy()
        data_ok   = True
    except Exception as e:
        st.error(f"Database error: {e}")
        data_ok = False

if not data_ok:
    st.stop()

# KPIs
section_header("📊 Disease Metrics")
metric_row([
    {"label": "Unique Conditions",   "value": str(len(top_cond)),                          "icon": "🦠"},
    {"label": "Most Common",         "value": top_cond.iloc[0]["medical_condition"],        "icon": "📊"},
    {"label": "Highest Avg Billing", "value": f"Rs.{top_cond['avg_billing'].max():,.0f}",  "icon": "💰"},
    {"label": "Max Abnormal Rate",   "value": f"{top_cond['abnormal_rate'].max():.1f}%",   "icon": "⚠️"},
])

st.markdown("---")

# Top conditions
section_header("🏆 Top Medical Conditions")
col1, col2 = st.columns([1.5, 1])
with col1:
    fig = bar_chart(
        top_cond.head(top_n),
        x="medical_condition", y="total_cases",
        title=f"Top {top_n} Conditions by Case Count",
        color_discrete_sequence=["#2563EB"],
    )
    fig.update_layout(xaxis_tickangle=-20)
    st.plotly_chart(fig, use_container_width=True)
with col2:
    fig = donut_chart(top_cond, names="medical_condition", values="total_cases",
                      title="Case Distribution")
    st.plotly_chart(fig, use_container_width=True)

# Severity proxy
section_header("📈 Condition Severity Proxy", "Avg billing & LOS as severity indicators")
fig = scatter_chart(
    severity, x="avg_billing", y="avg_los",
    color="medical_condition", size="cases",
    title="Avg Billing vs Avg LOS by Condition (bubble = case volume)",
    hover_data=["avg_patient_age"],
)
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# Condition trend
section_header("📅 Condition Trend Over Time")
cond_list = sorted(trend_df["medical_condition"].unique())
selected_conds = st.multiselect("Select Conditions to Compare", options=cond_list, default=cond_list[:4])

if selected_conds:
    trend_filtered = trend_df[trend_df["medical_condition"].isin(selected_conds)].copy()
    trend_filtered["month"] = pd.to_datetime(trend_filtered["month"])
    fig = line_chart(
        trend_filtered.sort_values("month"),
        x="month", y="cases", color="medical_condition",
        title="Monthly Case Trends by Condition",
    )
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# Conditions across age groups
section_header("🎂 Conditions Across Age Groups")
fig = grouped_bar(
    age_cond, x="age_group", y="count", color="medical_condition",
    title="Medical Condition Distribution by Age Group",
    barmode="stack",
)
age_order = ["Under 18", "18-29", "30-44", "45-59", "60-74", "75+"]
fig.update_xaxes(categoryorder="array", categoryarray=age_order)
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# Medications
section_header("💊 Medication Analysis")
col3, col4 = st.columns(2)
with col3:
    fig = bar_chart(
        med_sum.sort_values("total_prescribed", ascending=True).tail(10),
        x="total_prescribed", y="medication",
        orientation="h",
        title="Most Prescribed Medications",
        color_discrete_sequence=["#8B5CF6"],
    )
    st.plotly_chart(fig, use_container_width=True)
with col4:
    fig = bar_chart(
        med_sum.sort_values("avg_cost", ascending=True).tail(10),
        x="avg_cost", y="medication",
        orientation="h",
        title="Avg Cost per Medication (Rs.)",
        color_discrete_sequence=["#F59E0B"],
    )
    st.plotly_chart(fig, use_container_width=True)

# Treemap
section_header("🗺️ Medication x Condition Treemap")
fig = treemap(
    med_dist.head(80),
    path=["medical_condition", "medication"],
    values="count",
    title="Medication Distribution by Medical Condition",
)
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# Test results
section_header("🔬 Test Results by Condition")
col5, col6 = st.columns([1.6, 1])
with col5:
    fig = grouped_bar(
        test_res, x="medical_condition", y="count", color="test_results",
        title="Test Results Distribution by Condition",
        barmode="group",
    )
    fig.update_layout(xaxis_tickangle=-25)
    st.plotly_chart(fig, use_container_width=True)
with col6:
    res_total = test_res.groupby("test_results")["count"].sum().reset_index()
    fig = donut_chart(res_total, names="test_results", values="count",
                      title="Overall Test Results")
    st.plotly_chart(fig, use_container_width=True)

# Condition detail table
with st.expander("📋 Condition Detail Table (Abnormal Rates)"):
    display_df = top_cond[[
        "medical_condition", "total_cases", "avg_billing", "avg_los", "abnormal_rate"
    ]].rename(columns={
        "medical_condition": "Condition",
        "total_cases":       "Cases",
        "avg_billing":       "Avg Billing",
        "avg_los":           "Avg LOS (days)",
        "abnormal_rate":     "Abnormal Rate %",
    })
    st.dataframe(
        display_df.style
            .format({"Avg Billing": "Rs.{:,.0f}", "Avg LOS (days)": "{:.1f}", "Abnormal Rate %": "{:.1f}%"})
            .background_gradient(subset=["Abnormal Rate %"], cmap="Reds"),
        use_container_width=True,
    )

st.markdown("---")
st.download_button("⬇️ Download Disease Analysis (CSV)",
    top_cond.to_csv(index=False), "disease_analysis.csv", "text/csv")
