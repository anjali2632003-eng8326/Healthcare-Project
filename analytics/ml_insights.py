"""
ML-powered insights: clustering, risk scoring, test result prediction.
Uses scikit-learn on data pulled from MySQL.
"""
import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import numpy as np
from database.connection import query_df


# ── Raw data for ML ────────────────────────────────────────────────────────────
def get_ml_data() -> pd.DataFrame:
    return query_df("""
        SELECT
            id, age, gender, blood_type, medical_condition,
            insurance_provider, billing_amount, room_number,
            admission_type, length_of_stay, medication, test_results
        FROM healthcare_records
        WHERE billing_amount IS NOT NULL
          AND length_of_stay IS NOT NULL
          AND length_of_stay > 0
    """)


# ── K-Means Clustering ─────────────────────────────────────────────────────────
def run_clustering(n_clusters: int = 4) -> pd.DataFrame:
    """Cluster patients into risk/cost segments."""
    from sklearn.preprocessing import LabelEncoder, StandardScaler
    from sklearn.cluster import KMeans
    from sklearn.decomposition import PCA

    df = get_ml_data()

    features = ["age", "billing_amount", "length_of_stay"]
    le = LabelEncoder()
    df["gender_enc"]         = le.fit_transform(df["gender"].astype(str))
    df["admission_enc"]      = le.fit_transform(df["admission_type"].astype(str))
    df["condition_enc"]      = le.fit_transform(df["medical_condition"].astype(str))

    feature_cols = features + ["gender_enc", "admission_enc", "condition_enc"]
    X = df[feature_cols].fillna(0)

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    km = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    df["cluster"] = km.fit_predict(X_scaled)

    cluster_labels = {
        0: "Low Cost / Short Stay",
        1: "High Cost / Long Stay",
        2: "Emergency / Critical",
        3: "Elective / Routine",
    }
    df["cluster_label"] = df["cluster"].map(
        lambda c: cluster_labels.get(c, f"Segment {c+1}")
    )

    # PCA for 2-D visualization
    pca = PCA(n_components=2, random_state=42)
    coords = pca.fit_transform(X_scaled)
    df["pca_x"] = coords[:, 0]
    df["pca_y"] = coords[:, 1]

    return df[[
        "id","age","billing_amount","length_of_stay","medical_condition",
        "gender","admission_type","cluster","cluster_label","pca_x","pca_y"
    ]]


def get_cluster_summary(cluster_df: pd.DataFrame) -> pd.DataFrame:
    return (
        cluster_df.groupby("cluster_label")
        .agg(
            patients    = ("id", "count"),
            avg_age     = ("age", "mean"),
            avg_billing = ("billing_amount", "mean"),
            avg_los     = ("length_of_stay", "mean"),
        )
        .round(2)
        .reset_index()
        .sort_values("avg_billing", ascending=False)
    )


# ── Test Result Predictor ──────────────────────────────────────────────────────
def run_test_result_classification():
    """
    Predict test result (Normal / Abnormal / Inconclusive)
    using a Random Forest.  Returns model metrics + feature importance.
    """
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import LabelEncoder
    from sklearn.metrics import (classification_report,
                                  confusion_matrix, accuracy_score)

    df = get_ml_data()
    df = df[df["test_results"].isin(["Normal","Abnormal","Inconclusive"])]

    le_map = {}
    for col in ["gender","admission_type","medical_condition","medication",
                "insurance_provider","blood_type"]:
        le = LabelEncoder()
        df[col + "_enc"] = le.fit_transform(df[col].astype(str))
        le_map[col] = le

    feature_cols = [
        "age","billing_amount","length_of_stay",
        "gender_enc","admission_type_enc","medical_condition_enc",
        "medication_enc","insurance_provider_enc",
    ]
    X = df[feature_cols].fillna(0)
    y = df["test_results"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    clf = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
    clf.fit(X_train, y_train)
    y_pred = clf.predict(X_test)

    acc    = round(accuracy_score(y_test, y_pred) * 100, 2)
    report = classification_report(y_test, y_pred, output_dict=True)
    cm     = confusion_matrix(y_test, y_pred, labels=["Normal","Abnormal","Inconclusive"])
    fi     = pd.DataFrame({
        "feature":   feature_cols,
        "importance": clf.feature_importances_
    }).sort_values("importance", ascending=False)

    return {
        "accuracy":     acc,
        "report":       report,
        "confusion_matrix": cm,
        "labels":       ["Normal","Abnormal","Inconclusive"],
        "feature_importance": fi,
        "model":        clf,
    }


# ── Risk Score ─────────────────────────────────────────────────────────────────
def compute_risk_scores() -> pd.DataFrame:
    """
    Composite risk score per patient record based on:
    - Age (older = higher risk)
    - Billing amount (higher = more complex)
    - Length of stay (longer = more serious)
    - Abnormal test result (+risk)
    - Emergency admission (+risk)
    Returns DataFrame with risk_score (0-100) and risk_tier.
    """
    df = get_ml_data()

    # Normalise 0-1
    def norm(s):
        mn, mx = s.min(), s.max()
        return (s - mn) / (mx - mn + 1e-9)

    score = (
        0.30 * norm(df["age"]) +
        0.30 * norm(df["billing_amount"]) +
        0.25 * norm(df["length_of_stay"]) +
        0.10 * (df["test_results"] == "Abnormal").astype(float) +
        0.05 * (df["admission_type"] == "Emergency").astype(float)
    )
    df["risk_score"] = (score * 100).round(1)
    df["risk_tier"]  = pd.cut(
        df["risk_score"],
        bins=[0, 33, 66, 100],
        labels=["Low Risk","Moderate Risk","High Risk"]
    ).astype(str)

    return df[["id","age","billing_amount","length_of_stay",
               "medical_condition","gender","admission_type",
               "test_results","risk_score","risk_tier"]]
