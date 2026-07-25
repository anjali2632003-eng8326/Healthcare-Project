"""
Page 6: ML Insights - Clustering, Risk Scoring, Prediction
"""
import os
import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="ML Insights | Healthcare Dashboard", page_icon="🤖", layout="wide")
css_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "style.css")
with open(css_path, "r", encoding="utf-8") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

from analytics.ml_insights import run_clustering, get_cluster_summary, \
    run_test_result_classification, compute_risk_scores
from visualizations.charts import (
    scatter_chart, bar_chart, donut_chart, gauge_chart,
    confusion_matrix_chart, grouped_bar,
)
from visualizations.kpis import section_header, metric_row

# Header
st.markdown("""
<div class="hero-banner">
    <h1 style="color:#f1f5f9;font-size:28px;font-weight:800;margin:0 0 6px">
        🤖 Machine Learning Insights
    </h1>
    <p style="color:#93c5fd;margin:0;font-size:14px">
        Patient risk segmentation, predictive modelling &amp; anomaly detection
    </p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### 🤖 ML Configuration")
    n_clusters = st.slider("K-Means Clusters", 2, 8, 4)
    run_rf     = st.checkbox("Run Random Forest (slower, ~5s)", value=True)

# Tabs
tab1, tab2, tab3 = st.tabs([
    "🔵 Patient Clustering",
    "🔮 Test Result Prediction",
    "🚨 Risk Scoring",
])


# ── Tab 1: K-Means Clustering ──────────────────────────────────────────────────
with tab1:
    section_header("🔵 Patient Segmentation (K-Means)", f"{n_clusters} clusters")
    with st.spinner("Running K-Means clustering..."):
        try:
            cluster_df  = run_clustering(n_clusters)
            cluster_sum = get_cluster_summary(cluster_df)
            cluster_ok  = True
        except Exception as e:
            st.error(f"Clustering error: {e}")
            cluster_ok = False

    if cluster_ok:
        metric_row([
            {"label": "Clusters",         "value": str(n_clusters),                                 "icon": "🔵"},
            {"label": "Records Analysed", "value": f"{len(cluster_df):,}",                          "icon": "📋"},
            {"label": "Avg Age",          "value": f"{cluster_df['age'].mean():.0f} yrs",           "icon": "🎂"},
            {"label": "Avg Billing",      "value": f"Rs.{cluster_df['billing_amount'].mean():,.0f}", "icon": "💰"},
        ])

        st.markdown("<br>", unsafe_allow_html=True)

        col1, col2 = st.columns([1.5, 1])
        with col1:
            fig = scatter_chart(
                cluster_df.sample(min(3000, len(cluster_df)), random_state=42),
                x="pca_x", y="pca_y",
                color="cluster_label",
                title="Patient Segments (PCA 2-D Projection)",
                hover_data=["age", "billing_amount", "medical_condition"],
            )
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            fig = donut_chart(
                cluster_df.groupby("cluster_label").size().reset_index(name="count"),
                names="cluster_label", values="count",
                title="Cluster Size Distribution",
            )
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("#### 📊 Cluster Profiles")
        st.dataframe(
            cluster_sum.rename(columns={
                "cluster_label": "Segment",
                "patients":      "Patients",
                "avg_age":       "Avg Age",
                "avg_billing":   "Avg Billing",
                "avg_los":       "Avg LOS",
            }).style.format({
                "Avg Age":     "{:.0f}",
                "Avg Billing": "Rs.{:,.0f}",
                "Avg LOS":     "{:.1f}",
            }).background_gradient(subset=["Avg Billing"], cmap="Blues"),
            use_container_width=True,
        )

        col3, col4 = st.columns(2)
        with col3:
            fig = bar_chart(
                cluster_sum, x="cluster_label", y="avg_billing",
                title="Avg Billing per Cluster",
                color_discrete_sequence=["#2563EB"],
            )
            st.plotly_chart(fig, use_container_width=True)
        with col4:
            fig = bar_chart(
                cluster_sum, x="cluster_label", y="avg_los",
                title="Avg Length of Stay per Cluster",
                color_discrete_sequence=["#EF4444"],
            )
            st.plotly_chart(fig, use_container_width=True)

        cond_cluster = (
            cluster_df.groupby(["cluster_label", "medical_condition"])
            .size().reset_index(name="count")
            .sort_values("count", ascending=False)
        )
        st.markdown("#### 🦠 Medical Conditions per Cluster")
        fig = grouped_bar(
            cond_cluster, x="cluster_label", y="count", color="medical_condition",
            title="Medical Condition Distribution per Cluster",
            barmode="stack",
        )
        st.plotly_chart(fig, use_container_width=True)

        st.download_button(
            "⬇️ Download Cluster Data",
            cluster_df.drop(columns=["pca_x", "pca_y"]).to_csv(index=False),
            "patient_clusters.csv", "text/csv",
        )


# ── Tab 2: Test Result Prediction ─────────────────────────────────────────────
with tab2:
    section_header("🔮 Test Result Prediction (Random Forest)",
                   "Predicts Normal / Abnormal / Inconclusive from patient features")

    if not run_rf:
        st.info("Enable 'Run Random Forest' in the sidebar to see predictions.")
    else:
        with st.spinner("Training Random Forest classifier... (~5 seconds)"):
            try:
                rf_result = run_test_result_classification()
                rf_ok     = True
            except Exception as e:
                st.error(f"ML error: {e}")
                rf_ok = False

        if rf_ok:
            acc = rf_result["accuracy"]
            fi  = rf_result["feature_importance"]

            col5, col6 = st.columns([1, 2])
            with col5:
                fig = gauge_chart(acc, title="Model Accuracy", max_val=100)
                st.plotly_chart(fig, use_container_width=True)
                st.markdown("""
                <div style="text-align:center;color:#94a3b8;font-size:12px;margin-top:8px">
                    Algorithm: Random Forest (100 trees)<br>
                    Test split: 20% &middot; Random state: 42
                </div>
                """, unsafe_allow_html=True)

            with col6:
                report = rf_result["report"]
                classes = ["Normal", "Abnormal", "Inconclusive"]
                report_rows = []
                for cls in classes:
                    if cls in report:
                        r = report[cls]
                        report_rows.append({
                            "Class":     cls,
                            "Precision": f"{r['precision']:.2%}",
                            "Recall":    f"{r['recall']:.2%}",
                            "F1-Score":  f"{r['f1-score']:.2%}",
                            "Support":   int(r["support"]),
                        })
                st.markdown("#### 📊 Classification Report")
                st.dataframe(pd.DataFrame(report_rows), use_container_width=True)

            col7, col8 = st.columns(2)
            with col7:
                fig = confusion_matrix_chart(
                    rf_result["confusion_matrix"],
                    rf_result["labels"],
                    "Confusion Matrix",
                )
                st.plotly_chart(fig, use_container_width=True)
            with col8:
                fig = bar_chart(
                    fi, x="importance", y="feature",
                    orientation="h",
                    title="Feature Importance",
                    color_discrete_sequence=["#10B981"],
                )
                st.plotly_chart(fig, use_container_width=True)

            top_feat = fi.iloc[0]["feature"].replace("_enc", "").replace("_", " ").title()
            st.info(f"""
            **Model Interpretation:**
            - Accuracy: **{acc:.1f}%** on held-out test set (20%)
            - Most predictive feature: **{top_feat}**
            - Billing amount, length of stay, and medical condition are the strongest predictors
              for distinguishing Normal, Abnormal, and Inconclusive test outcomes.
            """)


# ── Tab 3: Risk Scoring ───────────────────────────────────────────────────────
with tab3:
    section_header("🚨 Patient Risk Scoring",
                   "Composite risk score (0-100) based on age, billing, LOS, test results, and admission type")

    with st.spinner("Computing risk scores..."):
        try:
            risk_df = compute_risk_scores()
            risk_ok = True
        except Exception as e:
            st.error(f"Risk scoring error: {e}")
            risk_ok = False

    if risk_ok:
        n_high = (risk_df["risk_tier"] == "High Risk").sum()
        n_mod  = (risk_df["risk_tier"] == "Moderate Risk").sum()
        n_low  = (risk_df["risk_tier"] == "Low Risk").sum()

        metric_row([
            {"label": "High Risk Patients",     "value": f"{n_high:,}",
             "delta": "needs attention", "delta_color": "red",   "icon": "🔴"},
            {"label": "Moderate Risk Patients", "value": f"{n_mod:,}",
             "delta": "monitor closely", "delta_color": "red",   "icon": "🟡"},
            {"label": "Low Risk Patients",      "value": f"{n_low:,}",
             "delta": "routine care",   "delta_color": "green",  "icon": "🟢"},
            {"label": "Avg Risk Score",         "value": f"{risk_df['risk_score'].mean():.1f}",
             "icon": "📊"},
        ])

        st.markdown("<br>", unsafe_allow_html=True)

        col9, col10 = st.columns(2)
        with col9:
            tier_counts = risk_df.groupby("risk_tier").size().reset_index(name="count")
            fig = donut_chart(tier_counts, names="risk_tier", values="count",
                              title="Risk Tier Distribution")
            st.plotly_chart(fig, use_container_width=True)
        with col10:
            fig = scatter_chart(
                risk_df.sample(min(2000, len(risk_df)), random_state=1),
                x="age", y="risk_score",
                color="risk_tier",
                size="billing_amount",
                title="Risk Score vs Age (bubble = billing amount)",
                hover_data=["medical_condition", "admission_type"],
            )
            st.plotly_chart(fig, use_container_width=True)

        risk_cond = (
            risk_df.groupby("medical_condition")["risk_score"]
            .mean().reset_index()
            .sort_values("risk_score", ascending=True)
            .rename(columns={"risk_score": "avg_risk_score"})
        )
        fig = bar_chart(
            risk_cond, x="avg_risk_score", y="medical_condition",
            orientation="h",
            title="Average Risk Score by Medical Condition",
            color_discrete_sequence=["#EF4444"],
        )
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("#### 🔴 High-Risk Patient Records")
        high_risk = risk_df[risk_df["risk_tier"] == "High Risk"].sort_values(
            "risk_score", ascending=False
        ).head(100)

        st.dataframe(
            high_risk.style.format({
                "billing_amount": "Rs.{:,.0f}",
                "risk_score":     "{:.1f}",
                "length_of_stay": "{:.0f}",
            }).background_gradient(subset=["risk_score"], cmap="Reds"),
            use_container_width=True, height=300,
        )

        st.download_button(
            "⬇️ Download Risk Scores",
            risk_df.to_csv(index=False),
            "patient_risk_scores.csv",
            "text/csv",
        )
