"""
Synthetic data generator.
Populates healthcare_db with realistic fake data using Faker + NumPy.

Usage:
    python database/seed_data.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import random
from datetime import date, timedelta, datetime

import numpy as np
from faker import Faker
from sqlalchemy import create_engine, text

from config.settings import DATABASE_URL

fake = Faker("en_IN")
rng  = np.random.default_rng(42)

# ── Constants ─────────────────────────────────────────────────────────────────
DEPARTMENTS = [
    ("Cardiology",         "Dr. Rajesh Kumar",   3, 40),
    ("Neurology",          "Dr. Priya Sharma",   4, 35),
    ("Orthopedics",        "Dr. Amit Singh",     2, 50),
    ("Pediatrics",         "Dr. Meena Verma",    1, 60),
    ("Oncology",           "Dr. Suresh Patel",   5, 30),
    ("Emergency Medicine", "Dr. Kavya Reddy",    0, 80),
    ("Gynecology",         "Dr. Sunita Das",     2, 45),
    ("Gastroenterology",   "Dr. Vikram Nair",    3, 30),
    ("Pulmonology",        "Dr. Ananya Iyer",    4, 35),
    ("Endocrinology",      "Dr. Ravi Menon",     3, 25),
]

SPECIALIZATIONS = [
    "Cardiologist", "Neurologist", "Orthopedic Surgeon", "Pediatrician",
    "Oncologist", "Emergency Physician", "Gynecologist", "Gastroenterologist",
    "Pulmonologist", "Endocrinologist", "General Surgeon", "Radiologist",
]

CONDITIONS = [
    ("I21", "Acute Myocardial Infarction"),
    ("I10", "Essential Hypertension"),
    ("E11", "Type 2 Diabetes Mellitus"),
    ("J18", "Community-Acquired Pneumonia"),
    ("N18", "Chronic Kidney Disease"),
    ("C34", "Malignant Neoplasm of Bronchus"),
    ("I63", "Cerebral Infarction"),
    ("K92", "Gastrointestinal Hemorrhage"),
    ("J44", "Chronic Obstructive Pulmonary Disease"),
    ("M54", "Dorsalgia / Back Pain"),
    ("F32", "Major Depressive Disorder"),
    ("Z38", "Liveborn Infant"),
    ("S72", "Fracture of Femur"),
    ("I50", "Heart Failure"),
    ("A09", "Gastroenteritis"),
    ("K80", "Cholelithiasis"),
    ("G40", "Epilepsy"),
    ("R51", "Headache Disorders"),
    ("E78", "Disorders of Lipoprotein Metabolism"),
    ("I48", "Atrial Fibrillation"),
]

TREATMENTS = [
    ("Medication",  ["Metformin", "Atorvastatin", "Lisinopril", "Amlodipine",
                     "Metoprolol", "Aspirin", "Omeprazole", "Insulin Glargine"]),
    ("Surgery",     ["Angioplasty", "Appendectomy", "Hip Replacement",
                     "Laparoscopic Cholecystectomy", "CABG", "Knee Arthroplasty"]),
    ("Therapy",     ["Physiotherapy", "Radiation Therapy", "Dialysis",
                     "Chemotherapy", "Respiratory Therapy"]),
    ("Diagnostic",  ["CT Scan", "MRI", "ECG", "Echocardiogram",
                     "Endoscopy", "Colonoscopy", "Biopsy"]),
]

CITIES = [
    "Bengaluru", "Hyderabad", "Chennai", "Mumbai", "Delhi",
    "Pune", "Kolkata", "Ahmedabad", "Jaipur", "Lucknow",
    "Coimbatore", "Visakhapatnam", "Bhopal", "Kochi", "Nagpur",
]

STATES = {
    "Bengaluru": "Karnataka",    "Hyderabad": "Telangana",
    "Chennai":   "Tamil Nadu",   "Mumbai":    "Maharashtra",
    "Delhi":     "Delhi",        "Pune":      "Maharashtra",
    "Kolkata":   "West Bengal",  "Ahmedabad": "Gujarat",
    "Jaipur":    "Rajasthan",    "Lucknow":   "Uttar Pradesh",
    "Coimbatore":"Tamil Nadu",   "Visakhapatnam": "Andhra Pradesh",
    "Bhopal":    "Madhya Pradesh","Kochi":    "Kerala",
    "Nagpur":    "Maharashtra",
}

BLOOD_GROUPS  = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
INS_TYPES     = ["Private", "Medicare", "Medicaid", "Uninsured", "Other"]
ADM_TYPES     = ["Emergency", "Elective", "Urgent"]
DISC_STATUSES = ["Recovered", "Referred", "Deceased", "Against Advice", "Transferred"]
SEVERITIES    = ["Mild", "Moderate", "Severe", "Critical"]


def create_schema(engine):
    print("Creating schema...")
    schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
    with open(schema_path, "r") as f:
        sql = f.read()
    with engine.connect() as conn:
        for statement in sql.split(";"):
            stmt = statement.strip()
            if stmt:
                try:
                    conn.execute(text(stmt))
                except Exception as e:
                    if "already exists" not in str(e).lower():
                        print(f"  Warning: {e}")
        conn.commit()
    print("  Schema ready.")


def seed_departments(conn):
    print("Seeding departments...")
    dept_ids = []
    for name, head, floor, beds in DEPARTMENTS:
        r = conn.execute(text(
            "INSERT INTO departments (name, head_doctor, floor_number, bed_capacity) "
            "VALUES (:n,:h,:f,:b)"
        ), {"n": name, "h": head, "f": floor, "b": beds})
        dept_ids.append(r.lastrowid)
    conn.commit()
    return dept_ids


def seed_doctors(conn, dept_ids, n=60):
    print(f"Seeding {n} doctors...")
    doctor_ids = []
    for _ in range(n):
        dept_id = random.choice(dept_ids)
        r = conn.execute(text(
            "INSERT INTO doctors (full_name, specialization, department_id, experience_yrs, phone, email) "
            "VALUES (:fn,:sp,:di,:ex,:ph,:em)"
        ), {
            "fn": fake.name(),
            "sp": random.choice(SPECIALIZATIONS),
            "di": dept_id,
            "ex": random.randint(1, 30),
            "ph": fake.phone_number()[:20],
            "em": fake.email(),
        })
        doctor_ids.append(r.lastrowid)
    conn.commit()
    return doctor_ids


def seed_patients(conn, n=5000):
    print(f"Seeding {n} patients...")
    patient_ids = []
    for _ in range(n):
        city  = random.choice(CITIES)
        state = STATES[city]
        dob   = fake.date_of_birth(minimum_age=1, maximum_age=95)
        r = conn.execute(text(
            "INSERT INTO patients "
            "(full_name, date_of_birth, gender, blood_group, phone, email, "
            " address, city, state, zip_code, insurance_type) "
            "VALUES (:fn,:dob,:g,:bg,:ph,:em,:ad,:ci,:st,:zp,:it)"
        ), {
            "fn":  fake.name(),
            "dob": dob,
            "g":   random.choice(["Male", "Female", "Other"]),
            "bg":  random.choice(BLOOD_GROUPS),
            "ph":  fake.phone_number()[:20],
            "em":  fake.email(),
            "ad":  fake.street_address(),
            "ci":  city,
            "st":  state,
            "zp":  str(random.randint(100000, 999999)),
            "it":  random.choices(INS_TYPES, weights=[40,25,20,10,5])[0],
        })
        patient_ids.append(r.lastrowid)
    conn.commit()
    return patient_ids


def seed_admissions(conn, patient_ids, doctor_ids, dept_ids, n=8000):
    print(f"Seeding {n} admissions...")
    admission_ids = []
    base_date = date(2022, 1, 1)
    span_days = (date(2025, 12, 31) - base_date).days

    for _ in range(n):
        adm_date = base_date + timedelta(days=random.randint(0, span_days))
        los       = int(rng.integers(1, 30))
        disc_date = adm_date + timedelta(days=los)
        if disc_date > date.today():
            disc_date = date.today()

        r = conn.execute(text(
            "INSERT INTO admissions "
            "(patient_id, doctor_id, department_id, admission_date, discharge_date, "
            " admission_type, discharge_status, readmission) "
            "VALUES (:pi,:di,:dpi,:ad,:dd,:at,:ds,:re)"
        ), {
            "pi":  random.choice(patient_ids),
            "di":  random.choice(doctor_ids),
            "dpi": random.choice(dept_ids),
            "ad":  adm_date,
            "dd":  disc_date,
            "at":  random.choices(ADM_TYPES, weights=[30, 50, 20])[0],
            "ds":  random.choices(DISC_STATUSES, weights=[70, 10, 3, 5, 12])[0],
            "re":  1 if random.random() < 0.12 else 0,
        })
        admission_ids.append(r.lastrowid)
    conn.commit()
    return admission_ids


def seed_diagnoses(conn, admission_ids):
    print("Seeding diagnoses...")
    rows = []
    for adm_id in admission_ids:
        # Primary diagnosis
        icd, cond = random.choice(CONDITIONS)
        rows.append({
            "ai": adm_id, "ic": icd, "cn": cond,
            "dt": "Primary", "sv": random.choices(SEVERITIES, weights=[30,40,20,10])[0]
        })
        # Possibly a secondary
        if random.random() < 0.45:
            icd2, cond2 = random.choice(CONDITIONS)
            rows.append({
                "ai": adm_id, "ic": icd2, "cn": cond2,
                "dt": "Secondary", "sv": random.choices(SEVERITIES, weights=[40,35,20,5])[0]
            })
    with conn.begin_nested():
        for row in rows:
            conn.execute(text(
                "INSERT INTO diagnoses (admission_id, icd10_code, condition_name, diagnosis_type, severity) "
                "VALUES (:ai,:ic,:cn,:dt,:sv)"
            ), row)
    conn.commit()
    print(f"  {len(rows)} diagnoses seeded.")


def seed_treatments(conn, admission_ids):
    print("Seeding treatments...")
    rows = []
    for adm_id in admission_ids:
        n_treatments = random.randint(1, 3)
        for _ in range(n_treatments):
            t_type, items = random.choice(TREATMENTS)
            rows.append({
                "ai": adm_id,
                "tt": t_type,
                "tn": random.choice(items),
                "oc": random.choices(["Successful","Partial","Failed","Ongoing"],
                                     weights=[65, 20, 5, 10])[0],
            })
    with conn.begin_nested():
        for row in rows:
            conn.execute(text(
                "INSERT INTO treatments (admission_id, treatment_type, treatment_name, outcome) "
                "VALUES (:ai,:tt,:tn,:oc)"
            ), row)
    conn.commit()
    print(f"  {len(rows)} treatment records seeded.")


def seed_billing(conn, admission_ids):
    print("Seeding billing records...")
    rows = []
    for adm_id in admission_ids:
        total    = round(random.uniform(5000, 500000), 2)
        ins_pct  = random.uniform(0.0, 0.9)
        ins_cov  = round(total * ins_pct, 2)
        pat_paid = round(min(total - ins_cov, random.uniform(0, total - ins_cov)), 2)
        rows.append({
            "ai": adm_id,
            "tc": total,
            "ic": ins_cov,
            "pp": pat_paid,
            "bs": random.choices(
                ["Paid","Partial","Pending","Written Off"],
                weights=[40,30,25,5]
            )[0],
            "bd": fake.date_between(start_date="-3y", end_date="today"),
        })
    with conn.begin_nested():
        for row in rows:
            conn.execute(text(
                "INSERT INTO billing (admission_id, total_charges, insurance_covered, "
                "patient_paid, billing_status, billing_date) "
                "VALUES (:ai,:tc,:ic,:pp,:bs,:bd)"
            ), row)
    conn.commit()
    print(f"  {len(rows)} billing records seeded.")


def seed_vitals(conn, admission_ids):
    print("Seeding vital signs...")
    rows = []
    sample_adm = random.sample(admission_ids, min(2000, len(admission_ids)))
    for adm_id in sample_adm:
        for day_offset in range(random.randint(1, 5)):
            rows.append({
                "ai":  adm_id,
                "ra":  datetime.now() - timedelta(days=random.randint(0, 900),
                                                   hours=random.randint(0,23)),
                "sbp": random.randint(90, 180),
                "dbp": random.randint(60, 110),
                "hr":  random.randint(55, 120),
                "tmp": round(random.uniform(36.0, 39.5), 1),
                "oxy": round(random.uniform(92.0, 100.0), 1),
                "wt":  round(random.uniform(40.0, 120.0), 1),
            })
    with conn.begin_nested():
        for row in rows:
            conn.execute(text(
                "INSERT INTO vital_signs "
                "(admission_id, recorded_at, systolic_bp, diastolic_bp, "
                " heart_rate, temperature, oxygen_sat, weight_kg) "
                "VALUES (:ai,:ra,:sbp,:dbp,:hr,:tmp,:oxy,:wt)"
            ), row)
    conn.commit()
    print(f"  {len(rows)} vital sign records seeded.")


def main():
    print("=" * 60)
    print("  Healthcare Dashboard — Database Seeder")
    print("=" * 60)

    engine = create_engine(DATABASE_URL, echo=False)

    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✅ Database connection successful.\n")
    except Exception as e:
        print(f"❌ Cannot connect to MySQL: {e}")
        print("   Make sure MySQL is running and credentials in .env are correct.")
        sys.exit(1)

    create_schema(engine)

    with engine.connect() as conn:
        # Check if already seeded
        count = conn.execute(text("SELECT COUNT(*) FROM patients")).scalar()
        if count > 0:
            print(f"\n⚠️  Database already has {count} patients.")
            ans = input("   Re-seed? This will DROP and recreate all tables. [y/N]: ")
            if ans.strip().lower() != "y":
                print("Aborted. No changes made.")
                return
            # Drop and recreate
            tables = ["vital_signs","billing","treatments","diagnoses",
                      "admissions","patients","doctors","departments"]
            for t in tables:
                conn.execute(text(f"DROP TABLE IF EXISTS {t}"))
            conn.commit()
            create_schema(engine)

        dept_ids      = seed_departments(conn)
        doctor_ids    = seed_doctors(conn, dept_ids, n=60)
        patient_ids   = seed_patients(conn, n=5000)
        admission_ids = seed_admissions(conn, patient_ids, doctor_ids, dept_ids, n=8000)
        seed_diagnoses(conn, admission_ids)
        seed_treatments(conn, admission_ids)
        seed_billing(conn, admission_ids)
        seed_vitals(conn, admission_ids)

    print("\n✅ Database seeding complete!")
    print(f"   Patients:   5,000")
    print(f"   Admissions: 8,000")
    print(f"   Diagnoses:  ~12,000")
    print(f"   Treatments: ~18,000")
    print(f"   Billing:    8,000")
    print(f"   Vitals:     ~8,000")


if __name__ == "__main__":
    main()
