"""
Overview analytics — SQLite-compatible queries.
"""
import pandas as pd
from database.connection import query_df


def get_kpis() -> dict:
    df = query_df("""
        SELECT
            COUNT(*)                                        AS total_records,
            COUNT(DISTINCT patient_name)                    AS unique_patients,
            COUNT(DISTINCT hospital)                        AS total_hospitals,
            COUNT(DISTINCT doctor)                          AS total_doctors,
            ROUND(AVG(billing_amount), 2)                   AS avg_billing,
            ROUND(SUM(billing_amount), 2)                   AS total_revenue,
            ROUND(AVG(length_of_stay), 2)                   AS avg_los,
            SUM(CASE WHEN test_results='Abnormal' THEN 1 ELSE 0 END) AS abnormal_tests,
            COUNT(DISTINCT medical_condition)               AS unique_conditions,
            ROUND(100.0 * SUM(CASE WHEN test_results='Abnormal' THEN 1 ELSE 0 END)
                  / COUNT(*), 2)                            AS abnormal_rate
        FROM healthcare_records
    """)
    return df.iloc[0].to_dict()


def get_monthly_trend() -> pd.DataFrame:
    return query_df("""
        SELECT
            SUBSTR(date_of_admission, 1, 7)     AS month,
            COUNT(*)                            AS admissions,
            ROUND(SUM(billing_amount), 2)       AS revenue,
            ROUND(AVG(billing_amount), 2)       AS avg_billing,
            ROUND(AVG(length_of_stay), 2)       AS avg_los
        FROM healthcare_records
        WHERE date_of_admission IS NOT NULL
        GROUP BY month
        ORDER BY month
    """)


def get_yearly_trend() -> pd.DataFrame:
    return query_df("""
        SELECT
            SUBSTR(date_of_admission, 1, 4)             AS year,
            COUNT(*)                                    AS admissions,
            ROUND(SUM(billing_amount), 2)               AS revenue,
            COUNT(DISTINCT medical_condition)           AS conditions_seen
        FROM healthcare_records
        WHERE date_of_admission IS NOT NULL
        GROUP BY year
        ORDER BY year
    """)


def get_condition_summary() -> pd.DataFrame:
    return query_df("""
        SELECT
            medical_condition,
            COUNT(*)                            AS count,
            ROUND(AVG(billing_amount), 2)       AS avg_billing,
            ROUND(AVG(length_of_stay), 2)       AS avg_los,
            SUM(CASE WHEN test_results='Abnormal' THEN 1 ELSE 0 END) AS abnormal
        FROM healthcare_records
        GROUP BY medical_condition
        ORDER BY count DESC
    """)


def get_recent_records(n: int = 50) -> pd.DataFrame:
    return query_df(f"""
        SELECT
            patient_name, age, gender, medical_condition,
            admission_type, date_of_admission, discharge_date,
            length_of_stay, billing_amount, test_results, hospital
        FROM healthcare_records
        ORDER BY date_of_admission DESC
        LIMIT {n}
    """)
