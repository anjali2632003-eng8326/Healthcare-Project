"""
Page 5: Financial Analysis
"""
import os
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Financial Analysis | Healthcare Dashboard", page_icon="💰", layout="wide")
css_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "style.css")
with open(css_path, "r", encoding="utf-8") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

from analytics.financial_analytics import (
    get_revenue_summary, get_revenue_by_condition, get_revenue_by_insurance,
    get_revenue_by_admission_type, get_monthly_revenue_trend,
    get_billing_distribution, get_revenue_by_hospital, get_high_value_cases,
)
from visualizations.charts import (
    bar_chart, donut_chart, area_chart, scatter_chart, histogram, line_chart
)
from visualizations.kpis import section_header, metric_row

# Header
st.markdown("""
<div class="hero-banner">
    <h1 style="color:#f1f5f9;font-size:28px;font-weight:800;margin:0 0 6px">
        💰 Financial Analysis
    </h1>
    <p style="color:#93c5fd;margin:0;font-size:14px">
        Revenue trends, billing distribution, payer mix &amp; high-value case analysis
    </p>
</div>
""", unsafe_allow_html=True)

# Sidebar filter
with st.sidebar:
    st.markdown("### 💰 Filters")
    hv_threshold = st.number_input(
        "High-Value Case Threshold (Rs.)",
        min_value=5000, max_value=100000,
        value=30000, step=1000,
    )

with st.spinner("Loading financial data..."):
    try:
        rev_sum     = get_revenue_summary()
        rev_cond    = get_revenue_by_condition()
        rev_ins     = get_revenue_by_insurance()
        rev_adm     = get_revenue_by_admission_type()
        monthly_rev = get_monthly_revenue_trend()
        bill_dist   = get_billing_distribution()
        rev_hosp    = get_revenue_by_hospital()
        hv_cases    = get_high_value_cases(hv_threshold)
        data_ok     = True
    except Exception as e:
        st.error(f"Database error: {e}")
        data_ok = False

if not data_ok:
    st.stop()

# KPIs
section_header("💵 Revenue Summary")
metric_row([
    {"label": "Total Revenue",   "value": f"Rs.{rev_sum['total_revenue']/1e6:.2f}M",  "icon": "💰"},
    {"label": "Average Billing", "value": f"Rs.{rev_sum['avg_billing']:,.0f}",         "icon": "🧾"},
    {"label": "Min Billing",     "value": f"Rs.{rev_sum['min_billing']:,.0f}",         "icon": "📉"},
    {"label": "Max Billing",     "value": f"Rs.{rev_sum['max_billing']:,.0f}",         "icon": "📈"},
])

st.markdown("<br>", unsafe_allow_html=True)
col_g1, col_g2, col_g3 = st.columns(3)
with col_g1:
    st.metric("Std. Deviation", f"Rs.{rev_sum['stddev_billing']:,.0f}")
with col_g2:
    st.metric("High-Value Cases", f"{len(hv_cases):,}",
              help=f"Billing >= Rs.{hv_threshold:,}")
with col_g3:
    pct_hv = 100 * len(hv_cases) / max(rev_cond["cases"].sum(), 1)
    st.metric("High-Value %", f"{pct_hv:.1f}%")

st.markdown("---")

# Monthly revenue trend
section_header("📅 Monthly Revenue & Admission Trend")
monthly_rev["month"] = pd.to_datetime(monthly_rev["month"])
col1, col2 = st.columns(2)
with col1:
    fig = area_chart(monthly_rev, x="month", y="revenue",
                     title="Monthly Revenue (Rs.)")
    st.plotly_chart(fig, use_container_width=True)
with col2:
    fig = line_chart(monthly_rev, x="month", y="avg_billing",
                     title="Avg Billing per Month (Rs.)")
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# Revenue breakdown
section_header("🏥 Revenue Breakdown")
col3, col4 = st.columns(2)
with col3:
    fig = bar_chart(
        rev_cond.sort_values("total_revenue", ascending=True),
        x="total_revenue", y="medical_condition",
        orientation="h",
        title="Total Revenue by Medical Condition (Rs.)",
        color_discrete_sequence=["#2563EB"],
    )
    st.plotly_chart(fig, use_container_width=True)
with col4:
    fig = donut_chart(rev_ins, names="insurance_provider", values="total_billed",
                      title="Revenue by Insurance Provider")
    st.plotly_chart(fig, use_container_width=True)

col5, col6 = st.columns(2)
with col5:
    fig = bar_chart(
        rev_adm, x="admission_type", y="total_revenue",
        title="Total Revenue by Admission Type (Rs.)",
        color_discrete_sequence=["#10B981"],
    )
    st.plotly_chart(fig, use_container_width=True)
with col6:
    fig = bar_chart(
        rev_hosp.sort_values("total_revenue", ascending=True),
        x="total_revenue", y="hospital",
        orientation="h",
        title="Revenue by Hospital (Rs.)",
        color_discrete_sequence=["#8B5CF6"],
    )
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# Billing distribution
section_header("📊 Billing Amount Distribution")
col7, col8 = st.columns(2)
with col7:
    fig = histogram(bill_dist, x="billing_amount", bins=50,
                    title="Billing Amount Histogram")
    st.plotly_chart(fig, use_container_width=True)
with col8:
    fig = histogram(bill_dist, x="billing_amount", color="medical_condition",
                    title="Billing Distribution by Condition", bins=30)
    st.plotly_chart(fig, use_container_width=True)

section_header("💸 Billing Scatter by Insurance Provider")
fig = scatter_chart(
    bill_dist.head(3000),
    x="insurance_provider", y="billing_amount",
    color="medical_condition",
    title="Billing Amount by Insurance Provider",
)
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# High-value cases
section_header(f"⭐ High-Value Cases (>= Rs.{hv_threshold:,})", f"{len(hv_cases):,} cases identified")

if not hv_cases.empty:
    cond_filter = st.selectbox(
        "Filter by Condition",
        ["All"] + sorted(hv_cases["medical_condition"].unique().tolist()),
    )
    disp = hv_cases if cond_filter == "All" else hv_cases[hv_cases["medical_condition"] == cond_filter]

    st.dataframe(
        disp.style
            .format({"billing_amount": "Rs.{:,.2f}"})
            .background_gradient(subset=["billing_amount"], cmap="Blues"),
        use_container_width=True, height=300,
    )
    st.download_button(
        "⬇️ Download High-Value Cases",
        disp.to_csv(index=False),
        "high_value_cases.csv",
        "text/csv",
    )

with st.expander("📋 Insurance Provider Detail"):
    st.dataframe(rev_ins.style.format({
        "total_billed": "Rs.{:,.0f}",
        "avg_billed":   "Rs.{:,.0f}",
        "min_billed":   "Rs.{:,.0f}",
        "max_billed":   "Rs.{:,.0f}",
    }), use_container_width=True)
