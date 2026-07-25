"""
Database connection — SQLite backend (zero-configuration).

SQLite is used here for maximum portability:
  - No server to install or start
  - Database lives in a single file: data/healthcare.db
  - Full SQL support via SQLAlchemy
"""
import os
import pandas as pd
from sqlalchemy import create_engine, text

# ── DB file path ───────────────────────────────────────────────────────────────
_BASE_DIR    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH      = os.path.join(_BASE_DIR, "data", "healthcare.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"

_engine = None


def get_engine():
    global _engine
    if _engine is None:
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        _engine = create_engine(
            DATABASE_URL,
            connect_args={"check_same_thread": False},
            echo=False,
        )
    return _engine


def query_df(sql: str, params: dict = None) -> pd.DataFrame:
    """Execute SQL and return a DataFrame."""
    engine = get_engine()
    with engine.connect() as conn:
        result = conn.execute(text(sql), params or {})
        return pd.DataFrame(result.fetchall(), columns=result.keys())


def test_connection() -> bool:
    try:
        engine = get_engine()
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


def db_has_data() -> bool:
    try:
        engine = get_engine()
        with engine.connect() as conn:
            count = conn.execute(
                text("SELECT COUNT(*) FROM healthcare_records")
            ).scalar()
        return (count or 0) > 0
    except Exception:
        return False
