"""
Page 4: Hospital Operations
"""
import os
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Hospital Operations | Healthcare Dashboard", page_icon="🏨", layout="wide")
css_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "style.css")
with open(css_path, "r", encoding="utf-8") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

from analytics.hospital_analytics import (
    get_hospital_performance, get_admission_type_breakdown,
    get_los_distribution, get_los_by_condition, get_doctor_performance,
    get_admission_type_by_condition, get_weekly_admission_pattern,
    get_room_utilization,
)
from visualizations.charts import (
    bar_chart, donut_chart, grouped_bar, scatter_chart, heatmap
)
from visualizations.kpis import section_header, metric_row

# Header
st.markdown("""
<div class="hero-banner">
    <h1 style="color:#f1f5f9;font-size:28px;font-weight:800;margin:0 0 6px">
        🏨 Hospital Operations
    </h1>
    <p style="color:#93c5fd;margin:0;font-size:14px">
        Hospital &amp; doctor performance, admission patterns, length-of-stay &amp; room utilisation
    </p>
</div>
""", unsafe_allow_html=True)

with st.spinner("Loading operations data..."):
    try:
        hosp_perf = get_hospital_performance()
        adm_type  = get_admission_type_breakdown()
        los_dist  = get_los_distribution()
        los_cond  = get_los_by_condition()
        doc_perf  = get_doctor_performance()
        adm_cond  = get_admission_type_by_condition()
        weekly    = get_weekly_admission_pattern()
        rooms     = get_room_utilization()
        data_ok   = True
    except Exception as e:
        st.error(f"Database error: {e}")
        data_ok = False

if not data_ok:
    st.stop()

# KPIs
section_header("📊 Operations Summary")
metric_row([
    {"label": "Total Hospitals",    "value": str(len(hosp_perf)),                          "icon": "🏥"},
    {"label": "Total Doctors",      "value": str(len(doc_perf)),                           "icon": "👨‍⚕️"},
    {"label": "Avg LOS (all)",      "value": f"{hosp_perf['avg_los'].mean():.1f} days",   "icon": "🛏️"},
    {"label": "Top Hospital Cases", "value": f"{hosp_perf['total_admissions'].max():,}",   "icon": "🏆"},
])

st.markdown("---")

# Hospital performance
section_header("🏥 Hospital Performance Comparison")
col1, col2 = st.columns(2)
with col1:
    fig = bar_chart(
        hosp_perf.sort_values("total_admissions", ascending=True).tail(10),
        x="total_admissions", y="hospital",
        orientation="h",
        title="Total Admissions by Hospital",
        color_discrete_sequence=["#2563EB"],
    )
    st.plotly_chart(fig, use_container_width=True)
with col2:
    fig = bar_chart(
        hosp_perf.sort_values("total_revenue", ascending=True).tail(10),
        x="total_revenue", y="hospital",
        orientation="h",
        title="Total Revenue by Hospital (Rs.)",
        color_discrete_sequence=["#10B981"],
    )
    st.plotly_chart(fig, use_container_width=True)

fig = scatter_chart(
    hosp_perf, x="total_admissions", y="avg_billing",
    size="avg_los", color="hospital",
    title="Hospital: Admissions vs Avg Billing (bubble = avg LOS)",
    hover_data=["abnormal_rate"],
)
st.plotly_chart(fig, use_container_width=True)

with st.expander("📋 Full Hospital Performance Table"):
    st.dataframe(hosp_perf.style.format({
        "avg_billing":    "Rs.{:,.0f}",
        "total_revenue":  "Rs.{:,.0f}",
        "avg_los":        "{:.1f}",
        "abnormal_rate":  "{:.1f}%",
    }), use_container_width=True)

st.markdown("---")

# Admission types
section_header("🚨 Admission Type Analysis")
col3, col4, col5 = st.columns(3)
with col3:
    fig = donut_chart(adm_type, names="admission_type", values="count",
                      title="Admission Type Mix")
    st.plotly_chart(fig, use_container_width=True)
with col4:
    fig = bar_chart(adm_type, x="admission_type", y="avg_billing",
                    title="Avg Billing by Admission Type",
                    color_discrete_sequence=["#F59E0B"])
    st.plotly_chart(fig, use_container_width=True)
with col5:
    fig = bar_chart(adm_type, x="admission_type", y="avg_los",
                    title="Avg LOS by Admission Type",
                    color_discrete_sequence=["#EF4444"])
    st.plotly_chart(fig, use_container_width=True)

st.markdown("#### Admission Type by Medical Condition")
pivot_adm = adm_cond.pivot_table(
    index="medical_condition", columns="admission_type",
    values="count", aggfunc="sum", fill_value=0,
)
fig = heatmap(pivot_adm, title="Admission Type x Condition Heatmap", colorscale="Viridis")
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# Length of stay
section_header("🛏️ Length of Stay Analysis")
col6, col7 = st.columns(2)
with col6:
    fig = bar_chart(los_dist, x="los", y="count",
                    title="Length of Stay Distribution (days)",
                    color_discrete_sequence=["#8B5CF6"])
    st.plotly_chart(fig, use_container_width=True)
with col7:
    fig = bar_chart(
        los_cond.sort_values("avg_los", ascending=True),
        x="avg_los", y="medical_condition",
        orientation="h",
        title="Average LOS by Medical Condition",
        color_discrete_sequence=["#06B6D4"],
    )
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# Weekly pattern
section_header("📅 Weekly Admission Pattern")
fig = bar_chart(
    weekly, x="day_name", y="admissions",
    title="Admissions by Day of Week",
    color_discrete_sequence=["#EC4899"],
)
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# Doctor performance
section_header("👨‍⚕️ Top Doctor Performance")
with st.sidebar:
    st.markdown("### 🏥 Filters")
    top_doc_n = st.slider("Show Top N Doctors", 5, 20, 10)

doc_display = doc_perf.head(top_doc_n)
col8, col9 = st.columns(2)
with col8:
    fig = bar_chart(
        doc_display.sort_values("patients_seen", ascending=True).tail(top_doc_n),
        x="patients_seen", y="doctor",
        orientation="h",
        title=f"Top {top_doc_n} Doctors by Patients Seen",
        color_discrete_sequence=["#2563EB"],
    )
    st.plotly_chart(fig, use_container_width=True)
with col9:
    fig = scatter_chart(
        doc_display, x="patients_seen", y="avg_billing",
        color="avg_los",
        title="Doctors: Patients vs Avg Billing (color = avg LOS)",
        hover_data=["doctor", "conditions_treated"],
    )
    st.plotly_chart(fig, use_container_width=True)

# Room utilization
section_header("🏠 Top Room Utilization")
fig = bar_chart(rooms, x="room_number", y="usage_count",
                title="Most Used Room Numbers",
                color_discrete_sequence=["#84CC16"])
fig.update_xaxes(type="category")
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.download_button("⬇️ Download Hospital Performance",
    hosp_perf.to_csv(index=False), "hospital_performance.csv", "text/csv")
