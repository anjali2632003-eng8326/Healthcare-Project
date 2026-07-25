"""
Patient demographics analytics queries — SQLite-compatible.
"""
import pandas as pd
from database.connection import query_df


def get_age_distribution() -> pd.DataFrame:
    return query_df("""
        SELECT
            age_group,
            COUNT(*) AS count,
            ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM healthcare_records), 2) AS pct
        FROM healthcare_records
        GROUP BY age_group
        ORDER BY CASE age_group
            WHEN 'Under 18' THEN 1
            WHEN '18-29'    THEN 2
            WHEN '30-44'    THEN 3
            WHEN '45-59'    THEN 4
            WHEN '60-74'    THEN 5
            WHEN '75+'      THEN 6
            ELSE 7
        END
    """)


def get_gender_breakdown() -> pd.DataFrame:
    return query_df("""
        SELECT
            gender,
            COUNT(*) AS count,
            ROUND(AVG(age), 1) AS avg_age,
            ROUND(AVG(billing_amount), 2) AS avg_billing,
            ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM healthcare_records), 2) AS pct
        FROM healthcare_records
        GROUP BY gender
    """)


def get_blood_type_distribution() -> pd.DataFrame:
    return query_df("""
        SELECT blood_type, COUNT(*) AS count
        FROM healthcare_records
        WHERE blood_type IS NOT NULL
        GROUP BY blood_type
        ORDER BY count DESC
    """)


def get_insurance_breakdown() -> pd.DataFrame:
    return query_df("""
        SELECT
            insurance_provider,
            COUNT(*) AS patients,
            ROUND(SUM(billing_amount), 2) AS total_billed,
            ROUND(AVG(billing_amount), 2) AS avg_billed,
            ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM healthcare_records), 2) AS pct
        FROM healthcare_records
        GROUP BY insurance_provider
        ORDER BY patients DESC
    """)


def get_age_gender_heatmap() -> pd.DataFrame:
    return query_df("""
        SELECT
            age_group,
            gender,
            COUNT(*) AS count
        FROM healthcare_records
        GROUP BY age_group, gender
        ORDER BY CASE age_group
            WHEN 'Under 18' THEN 1
            WHEN '18-29'    THEN 2
            WHEN '30-44'    THEN 3
            WHEN '45-59'    THEN 4
            WHEN '60-74'    THEN 5
            WHEN '75+'      THEN 6
            ELSE 7
        END
    """)


def get_age_vs_billing() -> pd.DataFrame:
    return query_df("""
        SELECT age, billing_amount, medical_condition, gender
        FROM healthcare_records
        LIMIT 3000
    """)


def get_condition_by_gender() -> pd.DataFrame:
    return query_df("""
        SELECT
            medical_condition,
            gender,
            COUNT(*) AS count
        FROM healthcare_records
        GROUP BY medical_condition, gender
    """)
