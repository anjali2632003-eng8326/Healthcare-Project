"""
Page 2: Patient Demographics
"""
import os
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Patient Demographics | Healthcare Dashboard", page_icon="+", layout="wide")
css_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "style.css")
with open(css_path, "r", encoding="utf-8") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

from analytics.patient_analytics import (
    get_age_distribution, get_gender_breakdown, get_blood_type_distribution,
    get_insurance_breakdown, get_age_gender_heatmap, get_age_vs_billing,
    get_condition_by_gender,
)
from visualizations.charts import (
    bar_chart, donut_chart, grouped_bar, scatter_chart, heatmap, histogram
)
from visualizations.kpis import section_header, metric_row

# Header
st.markdown("""
<div class="hero-banner">
    <h1 style="color:#f1f5f9;font-size:28px;font-weight:800;margin:0 0 6px">
        Patient Demographics
    </h1>
    <p style="color:#93c5fd;margin:0;font-size:14px">
        Explore patient population by age, gender, blood type, insurance and more
    </p>
</div>
""", unsafe_allow_html=True)

with st.spinner("Loading demographic data..."):
    try:
        age_df     = get_age_distribution()
        gender_df  = get_gender_breakdown()
        blood_df   = get_blood_type_distribution()
        ins_df     = get_insurance_breakdown()
        heat_df    = get_age_gender_heatmap()
        scatter_df = get_age_vs_billing()
        cond_gen   = get_condition_by_gender()
        data_ok    = True
    except Exception as e:
        st.error(f"Database error: {e}")
        data_ok = False

if not data_ok:
    st.stop()

# KPI metrics
section_header("Population Summary")
metric_row([
    {"label": "Total Records",
     "value": f"{age_df['count'].sum():,}", "icon": ""},
    {"label": "Male Patients",
     "value": f"{gender_df[gender_df['gender']=='Male']['count'].sum():,}", "icon": ""},
    {"label": "Female Patients",
     "value": f"{gender_df[gender_df['gender']=='Female']['count'].sum():,}", "icon": ""},
    {"label": "Insurance Providers",
     "value": str(len(ins_df)), "icon": ""},
])

st.markdown("---")

# Age & Gender distribution
section_header("Age & Gender Analysis")
col1, col2, col3 = st.columns(3)

with col1:
    fig = bar_chart(age_df, x="age_group", y="count",
                    title="Patients by Age Group",
                    color_discrete_sequence=["#2563EB"])
    st.plotly_chart(fig, use_container_width=True)

with col2:
    fig = donut_chart(gender_df, names="gender", values="count",
                      title="Gender Distribution")
    st.plotly_chart(fig, use_container_width=True)

with col3:
    fig = bar_chart(gender_df, x="gender", y="avg_billing",
                    title="Avg Billing by Gender (Rs.)",
                    color_discrete_sequence=["#10B981", "#F59E0B"])
    st.plotly_chart(fig, use_container_width=True)

# Age-Gender heatmap
section_header("Age Group x Gender Heatmap")
pivot = heat_df.pivot_table(index="age_group", columns="gender",
                            values="count", aggfunc="sum", fill_value=0)
age_order = ["Under 18", "18-29", "30-44", "45-59", "60-74", "75+"]
pivot = pivot.reindex([a for a in age_order if a in pivot.index])
fig = heatmap(pivot, title="Patient Count by Age Group and Gender", colorscale="Blues")
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# Blood type
section_header("Blood Type Distribution")
col4, col5 = st.columns(2)
with col4:
    fig = bar_chart(blood_df, x="blood_type", y="count",
                    title="Patients by Blood Type",
                    color_discrete_sequence=["#EF4444"])
    st.plotly_chart(fig, use_container_width=True)
with col5:
    fig = donut_chart(blood_df, names="blood_type", values="count",
                      title="Blood Type Distribution")
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# Insurance provider
section_header("Insurance Provider Analysis")
col6, col7 = st.columns([1.3, 1])
with col6:
    fig = bar_chart(ins_df, x="insurance_provider", y="total_billed",
                    title="Total Billing by Insurance Provider (Rs.)",
                    color_discrete_sequence=["#8B5CF6"])
    st.plotly_chart(fig, use_container_width=True)
with col7:
    fig = donut_chart(ins_df, names="insurance_provider", values="patients",
                      title="Patients by Insurance Provider")
    st.plotly_chart(fig, use_container_width=True)

# Insurance detail table
with st.expander("Insurance Provider Detail Table"):
    st.dataframe(ins_df.style.format({
        "total_billed": "Rs.{:,.0f}",
        "avg_billed":   "Rs.{:,.0f}",
        "pct":          "{:.1f}%",
    }), use_container_width=True)

st.markdown("---")

# Age vs Billing scatter
section_header("Age vs Billing Amount", "Each dot represents a patient record")
fig = scatter_chart(
    scatter_df, x="age", y="billing_amount",
    color="medical_condition",
    title="Age vs. Billing Amount by Medical Condition",
    hover_data=["gender"],
)
st.plotly_chart(fig, use_container_width=True)

# Condition by gender
section_header("Medical Conditions by Gender")
fig = grouped_bar(
    cond_gen, x="medical_condition", y="count", color="gender",
    title="Condition Distribution by Gender",
    barmode="group",
)
fig.update_layout(xaxis_tickangle=-25)
st.plotly_chart(fig, use_container_width=True)

# Download buttons
st.markdown("---")
col_dl1, col_dl2, col_dl3 = st.columns(3)
with col_dl1:
    st.download_button("Download Age Distribution", age_df.to_csv(index=False),
                       "age_distribution.csv", "text/csv")
with col_dl2:
    st.download_button("Download Insurance Data", ins_df.to_csv(index=False),
                       "insurance_breakdown.csv", "text/csv")
with col_dl3:
    st.download_button("Download Blood Types", blood_df.to_csv(index=False),
                       "blood_types.csv", "text/csv")
