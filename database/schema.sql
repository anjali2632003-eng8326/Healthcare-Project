-- SQLite Schema for Healthcare Analytics Dashboard
-- Run automatically by loader.py — no manual setup needed

CREATE TABLE IF NOT EXISTS healthcare_records (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_name        TEXT     NOT NULL,
    age                 INTEGER  NOT NULL,
    gender              TEXT     NOT NULL,
    blood_type          TEXT,
    medical_condition   TEXT     NOT NULL,
    date_of_admission   TEXT,
    doctor              TEXT,
    hospital            TEXT,
    insurance_provider  TEXT,
    billing_amount      REAL,
    room_number         INTEGER,
    admission_type      TEXT,
    discharge_date      TEXT,
    medication          TEXT,
    test_results        TEXT,
    length_of_stay      INTEGER,
    age_group           TEXT,
    created_at          TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_medical_condition   ON healthcare_records (medical_condition);
CREATE INDEX IF NOT EXISTS idx_date_of_admission   ON healthcare_records (date_of_admission);
CREATE INDEX IF NOT EXISTS idx_hospital            ON healthcare_records (hospital);
CREATE INDEX IF NOT EXISTS idx_doctor              ON healthcare_records (doctor);
CREATE INDEX IF NOT EXISTS idx_insurance           ON healthcare_records (insurance_provider);
CREATE INDEX IF NOT EXISTS idx_admission_type      ON healthcare_records (admission_type);
CREATE INDEX IF NOT EXISTS idx_test_results        ON healthcare_records (test_results);
CREATE INDEX IF NOT EXISTS idx_gender              ON healthcare_records (gender);
CREATE INDEX IF NOT EXISTS idx_age_group           ON healthcare_records (age_group);
