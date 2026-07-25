"""
Disease analytics — SQLite-compatible queries.
"""
import pandas as pd
from database.connection import query_df


def get_top_conditions(limit: int = 10) -> pd.DataFrame:
    return query_df(f"""
        SELECT
            medical_condition,
            COUNT(*)                            AS total_cases,
            ROUND(AVG(billing_amount), 2)       AS avg_billing,
            ROUND(AVG(length_of_stay), 2)       AS avg_los,
            SUM(CASE WHEN test_results='Abnormal'     THEN 1 ELSE 0 END) AS abnormal,
            SUM(CASE WHEN test_results='Normal'       THEN 1 ELSE 0 END) AS normal,
            SUM(CASE WHEN test_results='Inconclusive' THEN 1 ELSE 0 END) AS inconclusive,
            ROUND(100.0 * SUM(CASE WHEN test_results='Abnormal' THEN 1 ELSE 0 END)
                  / COUNT(*), 2)                AS abnormal_rate
        FROM healthcare_records
        GROUP BY medical_condition
        ORDER BY total_cases DESC
        LIMIT {limit}
    """)


def get_condition_trend() -> pd.DataFrame:
    return query_df("""
        SELECT
            SUBSTR(date_of_admission, 1, 7) AS month,
            medical_condition,
            COUNT(*) AS cases
        FROM healthcare_records
        WHERE date_of_admission IS NOT NULL
        GROUP BY month, medical_condition
        ORDER BY month
    """)


def get_condition_by_age_group() -> pd.DataFrame:
    return query_df("""
        SELECT age_group, medical_condition, COUNT(*) AS count
        FROM healthcare_records
        GROUP BY age_group, medical_condition
    """)


def get_medication_distribution() -> pd.DataFrame:
    return query_df("""
        SELECT
            medication,
            COUNT(*) AS count,
            ROUND(AVG(billing_amount), 2) AS avg_billing,
            medical_condition
        FROM healthcare_records
        GROUP BY medication, medical_condition
        ORDER BY count DESC
    """)


def get_medication_summary() -> pd.DataFrame:
    return query_df("""
        SELECT
            medication,
            COUNT(*) AS total_prescribed,
            COUNT(DISTINCT medical_condition) AS conditions_treated,
            ROUND(AVG(billing_amount), 2) AS avg_cost
        FROM healthcare_records
        GROUP BY medication
        ORDER BY total_prescribed DESC
    """)


def get_test_results_by_condition() -> pd.DataFrame:
    return query_df("""
        SELECT medical_condition, test_results, COUNT(*) AS count
        FROM healthcare_records
        GROUP BY medical_condition, test_results
        ORDER BY medical_condition, count DESC
    """)


def get_condition_severity_proxy() -> pd.DataFrame:
    return query_df("""
        SELECT
            medical_condition,
            ROUND(AVG(billing_amount), 2)   AS avg_billing,
            ROUND(AVG(length_of_stay), 2)   AS avg_los,
            COUNT(*)                        AS cases,
            ROUND(AVG(age), 1)              AS avg_patient_age
        FROM healthcare_records
        GROUP BY medical_condition
        ORDER BY avg_billing DESC
    """)
