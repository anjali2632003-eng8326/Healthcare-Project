"""
Healthcare Data Analysis & Visualization Dashboard
Entry point - run with: streamlit run app.py
"""
import os
import streamlit as st

# Page config (MUST be first Streamlit call)
st.set_page_config(
    page_title = "Healthcare Analytics Dashboard",
    page_icon  = "+",
    layout     = "wide",
    initial_sidebar_state = "expanded",
    menu_items = {
        "Get Help": None,
        "Report a bug": None,
        "About": "Healthcare Data Analysis Dashboard - MCA Project by Anjali Kumari",
    },
)

# Inject global CSS
css_path = os.path.join(os.path.dirname(__file__), "assets", "style.css")
with open(css_path, "r", encoding="utf-8") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# DB connection check
from database.connection import test_connection, query_df

db_ok = test_connection()

# Sidebar
with st.sidebar:
    st.markdown("""
    <div style="text-align:center;padding:20px 0 10px">
        <div style="font-size:48px">+</div>
        <h2 style="color:#f1f5f9;margin:8px 0 2px;font-size:18px">Healthcare Analytics</h2>
        <p style="color:#64748b;font-size:12px;margin:0">Dashboard v2.0</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    if db_ok:
        st.success("Database Connected")
        try:
            count = query_df("SELECT COUNT(*) AS c FROM healthcare_records").iloc[0]["c"]
            st.markdown(f"""
            <div style="background:#0f172a;border:1px solid #334155;
                        border-radius:10px;padding:12px;margin:8px 0">
                <div style="color:#64748b;font-size:11px;text-transform:uppercase;
                            letter-spacing:1px">Dataset Size</div>
                <div style="color:#60a5fa;font-size:22px;font-weight:700">{count:,}</div>
                <div style="color:#64748b;font-size:11px">patient records</div>
            </div>
            """, unsafe_allow_html=True)
        except Exception:
            pass
    else:
        st.error("Database Not Connected")
        st.markdown("""
        **Setup Required:**
        1. Run: `python database/loader.py`
        """)

    st.markdown("---")
    st.markdown("""
    <div style="color:#64748b;font-size:11px;text-align:center">
        <strong style="color:#94a3b8">Dataset:</strong> Kaggle Healthcare Dataset<br>
        <strong style="color:#94a3b8">By:</strong> prasad22 - CC0 Public Domain<br><br>
        <strong style="color:#94a3b8">Project By:</strong> Anjali Kumari<br>
        <strong style="color:#94a3b8">Guide:</strong> Divakar Purohit<br>
        <strong style="color:#94a3b8">MCA, Andhra University</strong>
    </div>
    """, unsafe_allow_html=True)

# Home page
st.markdown("""
<div class="hero-banner">
    <h1 style="color:#f1f5f9;font-size:32px;font-weight:800;margin:0 0 8px">
        Healthcare Data Analysis Dashboard
    </h1>
    <p style="color:#93c5fd;font-size:16px;margin:0">
        Comprehensive analytics platform for patient demographics, disease trends,
        hospital operations, financial insights &amp; ML-powered risk assessment
    </p>
</div>
""", unsafe_allow_html=True)

# Navigation cards
st.markdown("### Dashboard Pages")
st.markdown("Use the **sidebar** to navigate between pages, or click the cards below:")

col1, col2, col3 = st.columns(3)

pages = [
    ("[Chart]",  "01 - Overview",             "Executive KPIs, trends, and key highlights"),
    ("[People]", "02 - Patient Demographics", "Age, gender, blood type & insurance analysis"),
    ("[Virus]",  "03 - Disease Analysis",     "Conditions, medications & test result trends"),
    ("[Hotel]",  "04 - Hospital Operations",  "LOS, admission types & hospital performance"),
    ("[Money]",  "05 - Financial Analysis",   "Revenue, billing distribution & payer mix"),
    ("[Robot]",  "06 - ML Insights",          "Clustering, risk scoring & predictive models"),
]

for i, (icon, name, desc) in enumerate(pages):
    col = [col1, col2, col3][i % 3]
    with col:
        st.markdown(f"""
        <div style="
            background:linear-gradient(135deg,#1e293b,#0f172a);
            border:1px solid #334155;border-radius:14px;
            padding:20px;margin-bottom:16px;
            box-shadow:0 4px 16px rgba(0,0,0,0.3);
        ">
            <h4 style="color:#60a5fa;margin:0 0 6px;font-size:15px">{name}</h4>
            <p style="color:#64748b;font-size:12px;margin:0">{desc}</p>
        </div>
        """, unsafe_allow_html=True)

# Quick start guide
st.markdown("---")
with st.expander("Quick Start Guide", expanded=not db_ok):
    st.markdown("""
    ### Setup Instructions

    **Step 1 - Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

    **Step 2 - Load dataset:**
    ```bash
    python database/loader.py
    ```
    This auto-generates 10,000 synthetic records if no CSV is present.

    **Step 3 - Launch dashboard:**
    ```bash
    streamlit run app.py
    ```

    ### Dataset Schema
    The Kaggle dataset (`prasad22/healthcare-dataset`) includes:
    - **Patient**: Name, Age, Gender, Blood Type
    - **Clinical**: Medical Condition, Medication, Test Results
    - **Administrative**: Hospital, Doctor, Room Number, Admission Type
    - **Financial**: Billing Amount, Insurance Provider
    - **Temporal**: Date of Admission, Discharge Date (Length of Stay computed)
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align:center;color:#475569;font-size:12px;padding:12px 0">
    Healthcare Data Analysis &amp; Visualization Dashboard |
    MCA Project - Anjali Kumari (A24CA1895) |
    Guide: Divakar Purohit, Sr. Data Analyst, Accenture
</div>
""", unsafe_allow_html=True)
