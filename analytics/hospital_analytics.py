"""
Hospital operations analytics — SQLite-compatible queries.
"""
import pandas as pd
from database.connection import query_df


def get_hospital_performance() -> pd.DataFrame:
    return query_df("""
        SELECT
            hospital,
            COUNT(*)                            AS total_admissions,
            ROUND(AVG(billing_amount), 2)       AS avg_billing,
            ROUND(SUM(billing_amount), 2)       AS total_revenue,
            ROUND(AVG(length_of_stay), 2)       AS avg_los,
            COUNT(DISTINCT doctor)              AS doctors,
            SUM(CASE WHEN test_results='Abnormal' THEN 1 ELSE 0 END) AS abnormal_cases,
            ROUND(100.0 * SUM(CASE WHEN test_results='Abnormal' THEN 1 ELSE 0 END)
                  / COUNT(*), 2)                AS abnormal_rate
        FROM healthcare_records
        GROUP BY hospital
        ORDER BY total_admissions DESC
    """)


def get_admission_type_breakdown() -> pd.DataFrame:
    return query_df("""
        SELECT
            admission_type,
            COUNT(*) AS count,
            ROUND(AVG(billing_amount), 2) AS avg_billing,
            ROUND(AVG(length_of_stay), 2) AS avg_los,
            ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM healthcare_records), 2) AS pct
        FROM healthcare_records
        GROUP BY admission_type
    """)


def get_los_distribution() -> pd.DataFrame:
    return query_df("""
        SELECT length_of_stay AS los, COUNT(*) AS count
        FROM healthcare_records
        WHERE length_of_stay IS NOT NULL
          AND length_of_stay BETWEEN 1 AND 60
        GROUP BY length_of_stay
        ORDER BY length_of_stay
    """)


def get_los_by_condition() -> pd.DataFrame:
    return query_df("""
        SELECT
            medical_condition,
            ROUND(AVG(length_of_stay), 2) AS avg_los,
            MIN(length_of_stay) AS min_los,
            MAX(length_of_stay) AS max_los
        FROM healthcare_records
        WHERE length_of_stay IS NOT NULL
        GROUP BY medical_condition
        ORDER BY avg_los DESC
    """)


def get_doctor_performance() -> pd.DataFrame:
    return query_df("""
        SELECT
            doctor,
            COUNT(*)                            AS patients_seen,
            ROUND(AVG(billing_amount), 2)       AS avg_billing,
            ROUND(AVG(length_of_stay), 2)       AS avg_los,
            COUNT(DISTINCT medical_condition)   AS conditions_treated,
            COUNT(DISTINCT hospital)            AS hospitals_worked,
            SUM(CASE WHEN test_results='Normal'   THEN 1 ELSE 0 END) AS normal_outcomes,
            SUM(CASE WHEN test_results='Abnormal' THEN 1 ELSE 0 END) AS abnormal_outcomes
        FROM healthcare_records
        GROUP BY doctor
        ORDER BY patients_seen DESC
        LIMIT 50
    """)


def get_admission_type_by_condition() -> pd.DataFrame:
    return query_df("""
        SELECT medical_condition, admission_type, COUNT(*) AS count
        FROM healthcare_records
        GROUP BY medical_condition, admission_type
    """)


def get_weekly_admission_pattern() -> pd.DataFrame:
    return query_df("""
        SELECT
            CASE CAST(strftime('%w', date_of_admission) AS INTEGER)
                WHEN 0 THEN 'Sunday'
                WHEN 1 THEN 'Monday'
                WHEN 2 THEN 'Tuesday'
                WHEN 3 THEN 'Wednesday'
                WHEN 4 THEN 'Thursday'
                WHEN 5 THEN 'Friday'
                WHEN 6 THEN 'Saturday'
            END AS day_name,
            CAST(strftime('%w', date_of_admission) AS INTEGER) AS day_num,
            COUNT(*) AS admissions
        FROM healthcare_records
        WHERE date_of_admission IS NOT NULL
        GROUP BY day_num, day_name
        ORDER BY day_num
    """)


def get_room_utilization() -> pd.DataFrame:
    return query_df("""
        SELECT
            room_number,
            COUNT(*) AS usage_count,
            ROUND(AVG(billing_amount), 2) AS avg_billing
        FROM healthcare_records
        WHERE room_number IS NOT NULL AND room_number > 0
        GROUP BY room_number
        ORDER BY usage_count DESC
        LIMIT 20
    """)
