"""
Financial analytics — SQLite-compatible queries.
"""
import pandas as pd
from database.connection import query_df


def get_revenue_summary() -> dict:
    df = query_df("""
        SELECT
            ROUND(SUM(billing_amount), 2)    AS total_revenue,
            ROUND(AVG(billing_amount), 2)    AS avg_billing,
            ROUND(MIN(billing_amount), 2)    AS min_billing,
            ROUND(MAX(billing_amount), 2)    AS max_billing
        FROM healthcare_records
    """)
    row = df.iloc[0].to_dict()
    # Compute stddev manually in Python (SQLite has no STDDEV)
    bills_df = query_df("SELECT billing_amount FROM healthcare_records WHERE billing_amount IS NOT NULL")
    import numpy as np
    row["stddev_billing"] = round(float(np.std(bills_df["billing_amount"])), 2)
    return row


def get_revenue_by_condition() -> pd.DataFrame:
    return query_df("""
        SELECT
            medical_condition,
            ROUND(SUM(billing_amount), 2)   AS total_revenue,
            ROUND(AVG(billing_amount), 2)   AS avg_billing,
            COUNT(*)                        AS cases
        FROM healthcare_records
        GROUP BY medical_condition
        ORDER BY total_revenue DESC
    """)


def get_revenue_by_insurance() -> pd.DataFrame:
    return query_df("""
        SELECT
            insurance_provider,
            COUNT(*)                        AS patients,
            ROUND(SUM(billing_amount), 2)   AS total_billed,
            ROUND(AVG(billing_amount), 2)   AS avg_billed,
            ROUND(MIN(billing_amount), 2)   AS min_billed,
            ROUND(MAX(billing_amount), 2)   AS max_billed
        FROM healthcare_records
        GROUP BY insurance_provider
        ORDER BY total_billed DESC
    """)


def get_revenue_by_admission_type() -> pd.DataFrame:
    return query_df("""
        SELECT
            admission_type,
            COUNT(*)                        AS cases,
            ROUND(SUM(billing_amount), 2)   AS total_revenue,
            ROUND(AVG(billing_amount), 2)   AS avg_revenue
        FROM healthcare_records
        GROUP BY admission_type
        ORDER BY total_revenue DESC
    """)


def get_monthly_revenue_trend() -> pd.DataFrame:
    return query_df("""
        SELECT
            SUBSTR(date_of_admission, 1, 7) AS month,
            ROUND(SUM(billing_amount), 2)   AS revenue,
            COUNT(*)                        AS admissions,
            ROUND(AVG(billing_amount), 2)   AS avg_billing
        FROM healthcare_records
        WHERE date_of_admission IS NOT NULL
        GROUP BY month
        ORDER BY month
    """)


def get_billing_distribution() -> pd.DataFrame:
    return query_df("""
        SELECT billing_amount, medical_condition, insurance_provider
        FROM healthcare_records
        WHERE billing_amount IS NOT NULL
        LIMIT 5000
    """)


def get_revenue_by_hospital() -> pd.DataFrame:
    return query_df("""
        SELECT
            hospital,
            COUNT(*)                        AS admissions,
            ROUND(SUM(billing_amount), 2)   AS total_revenue,
            ROUND(AVG(billing_amount), 2)   AS avg_billing
        FROM healthcare_records
        GROUP BY hospital
        ORDER BY total_revenue DESC
    """)


def get_high_value_cases(threshold: float = 30000) -> pd.DataFrame:
    return query_df(f"""
        SELECT
            patient_name, age, gender, medical_condition,
            hospital, doctor, billing_amount, length_of_stay,
            insurance_provider, admission_type, test_results
        FROM healthcare_records
        WHERE billing_amount >= {threshold}
        ORDER BY billing_amount DESC
        LIMIT 200
    """)
