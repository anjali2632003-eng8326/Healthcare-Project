import os
from dotenv import load_dotenv

load_dotenv()

# ── Database ──────────────────────────────────────────────────────────────────
DB_HOST     = os.getenv("DB_HOST", "localhost")
DB_PORT     = int(os.getenv("DB_PORT", 3306))
DB_NAME     = os.getenv("DB_NAME", "healthcare_db")
DB_USER     = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

DATABASE_URL = (
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# ── App ───────────────────────────────────────────────────────────────────────
APP_TITLE   = os.getenv("APP_TITLE", "Healthcare Analytics Dashboard")
APP_ICON    = os.getenv("APP_ICON", "🏥")
DEBUG       = os.getenv("DEBUG", "False").lower() == "true"

# ── Palette ───────────────────────────────────────────────────────────────────
PRIMARY_COLOR   = "#2563EB"
SECONDARY_COLOR = "#10B981"
ACCENT_COLOR    = "#F59E0B"
DANGER_COLOR    = "#EF4444"
CHART_COLORS    = [
    "#2563EB", "#10B981", "#F59E0B", "#EF4444",
    "#8B5CF6", "#EC4899", "#06B6D4", "#84CC16",
]
