"""
Dataset Loader — SQLite backend
================================
Downloads the Kaggle healthcare dataset and loads it into SQLite.

Priority order:
  1. Kaggle API  (needs ~/.kaggle/kaggle.json)
  2. Local CSV   (place healthcare_dataset.csv in data/ folder)
  3. Synthetic   (auto-generated 10,000 records — no Kaggle account needed)

Usage:
    python database/loader.py
"""
# Force UTF-8 output on Windows
import sys, os
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import warnings
warnings.filterwarnings("ignore")

import datetime
import random
import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE_DIR     = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR     = os.path.join(BASE_DIR, "data")
DB_PATH      = os.path.join(DATA_DIR, "healthcare.db")
RAW_DIR      = os.path.join(DATA_DIR, "raw")
CSV_FILENAME = "healthcare_dataset.csv"
DATABASE_URL = f"sqlite:///{DB_PATH}"

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(RAW_DIR,  exist_ok=True)


# ── Schema ─────────────────────────────────────────────────────────────────────
def _create_schema(engine):
    print("  Creating schema...")
    schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
    with open(schema_path, "r", encoding="utf-8") as f:
        sql = f.read()
    with engine.connect() as conn:
        for stmt in sql.split(";"):
            stmt = stmt.strip()
            if stmt:
                try:
                    conn.execute(text(stmt))
                except Exception as e:
                    if "already exists" not in str(e).lower():
                        print(f"    SQL note: {e}")
        conn.commit()
    print("  Schema ready.")


# ── Kaggle download ────────────────────────────────────────────────────────────
def _try_kaggle_download() -> str | None:
    """Try Kaggle API download. Returns CSV path or None."""
    try:
        kaggle_json = os.path.join(os.path.expanduser("~"), ".kaggle", "kaggle.json")
        if not os.path.exists(kaggle_json):
            return None

        print("  Kaggle credentials found. Downloading dataset...")
        ret = os.system(
            f'kaggle datasets download -d prasad22/healthcare-dataset '
            f'--path "{RAW_DIR}" --unzip -q'
        )
        if ret != 0:
            return None

        for fname in os.listdir(RAW_DIR):
            if fname.lower().endswith(".csv"):
                path = os.path.join(RAW_DIR, fname)
                print(f"  Downloaded: {fname}")
                return path
    except Exception as e:
        print(f"  Kaggle note: {e}")
    return None


# ── Local CSV ──────────────────────────────────────────────────────────────────
def _try_local_csv() -> str | None:
    candidates = [
        os.path.join(RAW_DIR,     CSV_FILENAME),
        os.path.join(DATA_DIR,    CSV_FILENAME),
        os.path.join(BASE_DIR,    CSV_FILENAME),
    ]
    for p in candidates:
        if os.path.exists(p):
            print(f"  Found local CSV: {os.path.basename(p)}")
            return p
    return None


# ── Synthetic data ─────────────────────────────────────────────────────────────
def _generate_synthetic(n: int = 10_000) -> pd.DataFrame:
    print(f"  Generating {n:,} synthetic records (mirrors Kaggle schema)...")

    try:
        from faker import Faker
        fake = Faker("en_US")
        names = [fake.name() for _ in range(n)]
    except Exception:
        names = [f"Patient {i+1}" for i in range(n)]

    rng = np.random.default_rng(2024)

    conditions  = ["Diabetes","Hypertension","Asthma","Obesity","Arthritis","Cancer"]
    adm_types   = ["Emergency","Elective","Urgent"]
    test_res    = ["Normal","Abnormal","Inconclusive"]
    medications = ["Aspirin","Ibuprofen","Penicillin","Paracetamol","Lipitor"]
    insurers    = ["Aetna","Blue Cross","Cigna","UnitedHealthcare","Medicare"]
    blood_types = ["A+","A-","B+","B-","AB+","AB-","O+","O-"]
    hospitals   = [
        "Smith-Johnson Hospital","Wallace-Hamilton Medical",
        "Hernandez LLC Medical","Thompson Medical Center",
        "White-Robinson Hospital","Anderson Health System",
        "Davis Medical Group","Martinez Hospital",
        "Taylor Health Center","Brown Memorial Hospital",
    ]
    try:
        from faker import Faker
        _f = Faker("en_US")
        doctors = [f"Dr. {_f.name()}" for _ in range(200)]
    except Exception:
        doctors = [f"Dr. Smith {i}" for i in range(200)]

    base_date = datetime.date(2019, 1, 1)
    span_days = (datetime.date(2024, 12, 31) - base_date).days

    rows = []
    for i in range(n):
        adm_offset  = int(rng.integers(0, span_days))
        stay        = int(rng.integers(1, 30))
        adm_date    = base_date + datetime.timedelta(days=adm_offset)
        disc_date   = adm_date  + datetime.timedelta(days=stay)
        age         = int(rng.integers(18, 85))

        rows.append({
            "Name":               names[i],
            "Age":                age,
            "Gender":             rng.choice(["Male","Female"]),
            "Blood Type":         rng.choice(blood_types),
            "Medical Condition":  rng.choice(conditions),
            "Date of Admission":  adm_date.isoformat(),
            "Doctor":             rng.choice(doctors),
            "Hospital":           rng.choice(hospitals),
            "Insurance Provider": rng.choice(insurers),
            "Billing Amount":     round(float(rng.uniform(1000, 50000)), 2),
            "Room Number":        int(rng.integers(100, 500)),
            "Admission Type":     rng.choice(adm_types, p=[0.3, 0.5, 0.2]),
            "Discharge Date":     disc_date.isoformat(),
            "Medication":         rng.choice(medications),
            "Test Results":       rng.choice(test_res, p=[0.45, 0.35, 0.20]),
        })

    df = pd.DataFrame(rows)
    print(f"  Generated {len(df):,} records.")
    return df


# ── Preprocessing ──────────────────────────────────────────────────────────────
def _preprocess(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = [c.strip() for c in df.columns]

    rename_map = {
        "Name":               "patient_name",
        "Age":                "age",
        "Gender":             "gender",
        "Blood Type":         "blood_type",
        "Medical Condition":  "medical_condition",
        "Date of Admission":  "date_of_admission",
        "Doctor":             "doctor",
        "Hospital":           "hospital",
        "Insurance Provider": "insurance_provider",
        "Billing Amount":     "billing_amount",
        "Room Number":        "room_number",
        "Admission Type":     "admission_type",
        "Discharge Date":     "discharge_date",
        "Medication":         "medication",
        "Test Results":       "test_results",
    }
    df = df.rename(columns=rename_map)

    # Parse & convert dates to ISO strings for SQLite
    for col in ["date_of_admission", "discharge_date"]:
        df[col] = pd.to_datetime(df[col], errors="coerce")

    # Drop rows missing essentials
    df = df.dropna(subset=["patient_name","age","medical_condition","date_of_admission"])

    # Numeric types
    df["age"]            = pd.to_numeric(df["age"], errors="coerce").fillna(0).astype(int)
    df["billing_amount"] = pd.to_numeric(df["billing_amount"], errors="coerce").fillna(0).round(2)
    df["room_number"]    = pd.to_numeric(df["room_number"], errors="coerce").fillna(0).astype(int)

    # String normalisation
    for col in ["gender","blood_type","medical_condition","doctor","hospital",
                "insurance_provider","admission_type","medication","test_results"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().str.title()

    # Age groups
    bins   = [0, 17, 29, 44, 59, 74, 200]
    labels = ["Under 18","18-29","30-44","45-59","60-74","75+"]
    df["age_group"] = pd.cut(df["age"], bins=bins, labels=labels, right=True).astype(str)

    # Length of stay (days between admission and discharge)
    df["length_of_stay"] = (df["discharge_date"] - df["date_of_admission"]).dt.days
    df["length_of_stay"] = df["length_of_stay"].fillna(0).clip(lower=0).astype(int)

    # Store dates as ISO strings
    df["date_of_admission"] = df["date_of_admission"].dt.strftime("%Y-%m-%d")
    df["discharge_date"]    = df["discharge_date"].dt.strftime("%Y-%m-%d")

    keep = list(rename_map.values()) + ["age_group","length_of_stay"]
    df = df[[c for c in keep if c in df.columns]]

    return df.reset_index(drop=True)


# ── Load to SQLite ─────────────────────────────────────────────────────────────
def _load_to_db(df: pd.DataFrame, engine) -> int:
    print(f"  Loading {len(df):,} records into SQLite...")
    df.to_sql(
        name      = "healthcare_records",
        con       = engine,
        if_exists = "append",
        index     = False,
        chunksize = 500,
        method    = "multi",
    )
    with engine.connect() as conn:
        count = conn.execute(text("SELECT COUNT(*) FROM healthcare_records")).scalar()
    print(f"  Total rows in DB: {count:,}")
    return count


# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    print("=" * 58)
    print("  Healthcare Dashboard - Dataset Loader")
    print("=" * 58)
    print(f"  DB: {DB_PATH}")
    print()

    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=False,
    )

    _create_schema(engine)

    # Check if already loaded
    with engine.connect() as conn:
        count = conn.execute(
            text("SELECT COUNT(*) FROM healthcare_records")
        ).scalar()

    if count and count > 0:
        print(f"\n  Table already has {count:,} rows.")
        ans = input("  Re-load? Existing data will be DELETED. [y/N]: ").strip().lower()
        if ans != "y":
            print("  Aborted - no changes made.")
            return
        with engine.connect() as conn:
            conn.execute(text("DELETE FROM healthcare_records"))
            conn.commit()
        print("  Cleared existing records.")

    # --- Acquire data ---
    print("\nStep 1/3 - Acquiring data...")
    csv_path = _try_kaggle_download() or _try_local_csv()

    if csv_path:
        print(f"\nStep 2/3 - Reading CSV: {os.path.basename(csv_path)}")
        df_raw = pd.read_csv(csv_path)
        print(f"  Rows read: {len(df_raw):,}")
    else:
        print("""
  Kaggle credentials not found and no local CSV detected.
  To use the real Kaggle dataset:
    1. Sign up at https://www.kaggle.com -> Account -> Create API Token
    2. Place kaggle.json in C:\\Users\\<you>\\.kaggle\\
    OR download manually from:
       https://www.kaggle.com/datasets/prasad22/healthcare-dataset
       and place 'healthcare_dataset.csv' in the data/ folder.

  Falling back to synthetic data...
""")
        df_raw = _generate_synthetic(10_000)

    print("\nStep 2/3 - Preprocessing...")
    df = _preprocess(df_raw)
    print(f"  Clean rows: {len(df):,}")

    print("\nStep 3/3 - Loading into SQLite...")
    inserted = _load_to_db(df, engine)

    print(f"\n{'='*58}")
    print(f"  Done! {inserted:,} records loaded.")
    print(f"  DB file: {DB_PATH}")
    print(f"  Run dashboard: streamlit run app.py")
    print(f"{'='*58}")


if __name__ == "__main__":
    main()
