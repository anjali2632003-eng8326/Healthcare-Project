# Healthcare Project — Easy CODE Flow Notes (For Viva)

Use this when lecturer asks **coding questions**.  
Read each section like a story: **Who calls whom → what happens → what comes out**.

---

# PART A — Big Picture (memorize this first)

## Whole project code flow (one diagram)

```
User opens browser
        ↓
streamlit run app.py
        ↓
┌─────────────────────────────────────────────┐
│  app.py  OR  pages/0X_....py                │  ← UI layer
│  (shows cards, charts, tables)              │
└──────────────────┬──────────────────────────┘
                   ↓ calls
┌─────────────────────────────────────────────┐
│  analytics/*.py                             │  ← Logic layer
│  (writes SQL questions)                     │
└──────────────────┬──────────────────────────┘
                   ↓ uses
┌─────────────────────────────────────────────┐
│  database/connection.py → query_df(sql)     │  ← Data access
└──────────────────┬──────────────────────────┘
                   ↓ reads
┌─────────────────────────────────────────────┐
│  data/healthcare.db  (table: healthcare_records)
└─────────────────────────────────────────────┘

For charts:
  analytics result (DataFrame)
        ↓
  visualizations/charts.py  (bar_chart, donut_chart…)
        ↓
  st.plotly_chart(fig) on the page
```

### One sentence to say in viva
> “We use a **layered architecture**: pages only display, analytics only query, connection only talks to SQLite, charts only draw graphs.”

---

# PART B — Section by Section Code Flow

---

## 1) `app.py` — Home page (entry point)

### What this file does
Starts the Streamlit app, loads CSS, checks DB, shows home screen.

### Code flow (step by step)

```
1. st.set_page_config(...)     → sets title, wide layout, sidebar
2. Read assets/style.css       → inject dark theme with st.markdown
3. test_connection()           → check if SQLite works
4. If DB ok → COUNT(*) records → show in sidebar
5. Show hero banner + 6 page cards
6. Streamlit auto-loads pages/ folder into sidebar navigation
```

### Important code meaning

| Code | Easy meaning |
|---|---|
| `st.set_page_config(...)` | Must be first Streamlit call. Sets page settings. |
| `st.markdown(f"<style>{css}</style>")` | Injects custom CSS for dark look |
| `test_connection()` | Runs `SELECT 1` on DB; True/False |
| `query_df("SELECT COUNT(*) ...")` | Gets how many patient rows exist |

### Likely coding Q
**Q:** Why is `set_page_config` first?  
**A:** Streamlit rule — page config must be the first Streamlit command, otherwise error.

---

## 2) `database/connection.py` — Talk to database

### What this file does
Creates SQLite connection and converts SQL result into Pandas table.

### Key functions

#### `get_engine()`
```
Create SQLAlchemy engine for:
sqlite:///.../data/healthcare.db
```
- Uses singleton (`_engine`) so connection is reused
- `check_same_thread=False` needed because Streamlit is multi-threaded

#### `query_df(sql, params=None)`  ★ MOST IMPORTANT
```
SQL text
  → engine.connect()
  → execute SQL
  → fetch all rows
  → return pandas DataFrame
```

**Say this:**  
> “`query_df` is our bridge. Every analytics function passes SQL into it and gets a DataFrame back.”

#### `test_connection()`
Runs `SELECT 1`. If no exception → DB is fine.

#### `db_has_data()`
Counts rows in `healthcare_records`. If count > 0 → data exists.

### Likely coding Q
**Q:** Why return DataFrame, not raw SQL rows?  
**A:** Pandas is easy for charts, grouping, and Streamlit tables.

---

## 3) `database/schema.sql` — Table design

### Main table: `healthcare_records`

Important columns:
- Patient: `patient_name, age, gender, blood_type, age_group`
- Clinical: `medical_condition, medication, test_results`
- Ops: `hospital, doctor, admission_type, length_of_stay`
- Money: `billing_amount, insurance_provider`
- Dates: `date_of_admission, discharge_date`

### Why indexes?
```sql
CREATE INDEX ... ON healthcare_records (medical_condition);
CREATE INDEX ... ON healthcare_records (hospital);
...
```
**Easy answer:** Indexes make `GROUP BY` / filters faster.

---

## 4) `database/loader.py` — How data enters the project ★★★

### Full flow

```
main()
  ↓
create SQLite engine
  ↓
_create_schema()          → run schema.sql (create table + indexes)
  ↓
If table already has rows → ask user to re-load or abort
  ↓
Acquire data (priority):
  1) _try_kaggle_download()
  2) _try_local_csv()
  3) _generate_synthetic(10000)
  ↓
_preprocess(df)           → clean + rename + add columns
  ↓
_load_to_db(df)           → df.to_sql("healthcare_records")
```

### `_preprocess()` — what cleaning happens (very common viva topic)

| Step | What code does |
|---|---|
| Rename columns | `Name` → `patient_name`, `Age` → `age`, etc. |
| Parse dates | convert admission/discharge to datetime |
| Drop bad rows | remove rows missing name/age/condition/date |
| Fix numbers | age, billing, room → numeric |
| Title-case text | Gender, Hospital, Condition cleaned |
| Create `age_group` | bins: Under 18, 18-29, 30-44, 45-59, 60-74, 75+ |
| Create `length_of_stay` | discharge − admission (days) |
| Save dates as text | SQLite-friendly `YYYY-MM-DD` |

### Synthetic fallback
If no Kaggle + no CSV:
- Faker creates names
- NumPy random creates age, billing, condition, etc.
- Generates 10,000 fake but realistic rows

### Likely coding Q
**Q:** What if CSV is missing?  
**A:** Loader falls back to synthetic data generation, so demo still works.

**Q:** Where is LOS calculated?  
**A:** In `loader.py` `_preprocess()`, not in Streamlit pages.

---

## 5) `analytics/` — SQL logic for each page

### Pattern used in EVERY analytics file

```python
from database.connection import query_df

def get_something() -> pd.DataFrame:
    return query_df("""
        SELECT ...
        FROM healthcare_records
        GROUP BY ...
        ORDER BY ...
    """)
```

**Easy meaning:**  
Analytics files = “ask questions in SQL”.  
Pages = “show answers as charts”.

---

### 5.1 `analytics/overview.py` → used by Overview page

| Function | What it returns | Simple meaning |
|---|---|---|
| `get_kpis()` | one dict of totals | total records, revenue, avg LOS, abnormal % |
| `get_monthly_trend()` | month-wise table | admissions + revenue each month |
| `get_yearly_trend()` | year-wise table | yearly summary |
| `get_condition_summary()` | condition table | cases/billing/LOS by disease |
| `get_recent_records(n)` | latest n rows | recent admissions list |

**KPI SQL idea (say in viva):**
```sql
COUNT(*) AS total_records,
SUM(billing_amount) AS total_revenue,
AVG(length_of_stay) AS avg_los,
100.0 * abnormal / total AS abnormal_rate
```

---

### 5.2 `analytics/patient_analytics.py` → Demographics page

| Function | Meaning |
|---|---|
| `get_age_distribution()` | count + % by age_group |
| `get_gender_breakdown()` | male/female counts + avg age/billing |
| `get_blood_type_distribution()` | A+, O-, etc. counts |
| `get_insurance_breakdown()` | patients + billed amount by insurer |
| `get_age_gender_heatmap()` | age_group × gender counts |
| `get_age_vs_billing()` | sample points for scatter chart |
| `get_condition_by_gender()` | disease counts by gender |

---

### 5.3 `analytics/disease_analytics.py` → Disease page

| Function | Meaning |
|---|---|
| `get_top_conditions(limit)` | top diseases + abnormal rate |
| `get_condition_trend()` | disease cases by month |
| `get_condition_by_age_group()` | which age gets which disease |
| `get_medication_summary()` | medicines prescribed most |
| `get_test_results_by_condition()` | Normal/Abnormal/Inconclusive per disease |
| `get_condition_severity_proxy()` | high billing + long stay ≈ more severe |

---

### 5.4 `analytics/hospital_analytics.py` → Operations page

| Function | Meaning |
|---|---|
| `get_hospital_performance()` | admissions, revenue, LOS per hospital |
| `get_doctor_performance()` | patients seen, outcomes per doctor |
| `get_admission_type_breakdown()` | Emergency / Elective / Urgent |
| `get_los_distribution()` | how many patients stayed X days |
| `get_weekly_admission_pattern()` | Mon–Sun admission counts |
| `get_room_utilization()` | most used rooms |

**Nice SQL trick:** `strftime('%w', date)` gets weekday number in SQLite.

---

### 5.5 `analytics/financial_analytics.py` → Finance page

| Function | Meaning |
|---|---|
| `get_revenue_summary()` | total/avg/min/max billing (+ std in Python) |
| `get_revenue_by_condition()` | which disease brings most money |
| `get_revenue_by_insurance()` | payer mix |
| `get_monthly_revenue_trend()` | revenue over months |
| `get_high_value_cases(threshold)` | billing >= threshold (default 30000) |
| `get_revenue_by_hospital()` | hospital-wise money |

---

### 5.6 `analytics/ml_insights.py` → ML page ★★★

#### A) `get_ml_data()`
Pulls ML-needed columns from DB (age, billing, LOS, gender, condition, test_results…).

#### B) `run_clustering(n_clusters)`
```
1. Get ML data
2. Encode text columns with LabelEncoder (gender, admission, condition → numbers)
3. Select features: age, billing, LOS + encoded cols
4. StandardScaler (make scales comparable)
5. KMeans.fit_predict → cluster id
6. PCA(n_components=2) → pca_x, pca_y for 2D plot
7. Return dataframe with cluster + labels
```

**Why StandardScaler?**  
Age is ~20–80, billing is thousands. Without scaling, billing dominates distance.

#### C) `run_test_result_classification()`
```
1. Get data where test_results is Normal/Abnormal/Inconclusive
2. Encode categorical features
3. X = features, y = test_results
4. train_test_split(80% train, 20% test, stratify=y)
5. RandomForestClassifier(n_estimators=100).fit(...)
6. Predict on test set
7. Return accuracy, confusion matrix, feature importance
```

#### D) `compute_risk_scores()`
```
score =
  0.30 * normalized(age) +
  0.30 * normalized(billing) +
  0.25 * normalized(LOS) +
  0.10 * (test == Abnormal) +
  0.05 * (admission == Emergency)

risk_score = score * 100
risk_tier  = Low / Moderate / High
```

---

## 6) `pages/` — UI screens (same pattern every page)

### Common page flow (memorize — answers almost every page coding Q)

```
1. st.set_page_config(...)
2. Load CSS
3. Import analytics functions + chart helpers + KPI helpers
4. Optional sidebar filters (slider / number input)
5. Call analytics functions inside try/except
6. If DB error → show message + st.stop()
7. metric_row([...])          → KPI cards
8. Create charts via visualizations/charts.py
9. st.plotly_chart(fig)
10. st.dataframe(...)         → tables
```

### Page ↔ Analytics map

| Page file | Analytics file |
|---|---|
| `01_Overview.py` | `overview.py` |
| `02_Patient_Demographics.py` | `patient_analytics.py` |
| `03_Disease_Analysis.py` | `disease_analytics.py` |
| `04_Hospital_Operations.py` | `hospital_analytics.py` |
| `05_Financial_Analysis.py` | `financial_analytics.py` |
| `06_ML_Insights.py` | `ml_insights.py` |

### Example (Overview) in plain English
```
get_kpis() → show 8 KPI cards
get_monthly_trend() → area/line charts
get_condition_summary() → bar/donut
get_recent_records(50) → table
```

### Example (ML page) tabs
```
Tab1: run_clustering(n_clusters) → scatter + donut + cluster table
Tab2: run_test_result_classification() → accuracy gauge + confusion matrix + feature importance
Tab3: compute_risk_scores() → risk tier counts + high risk table
```

Sidebar controls:
- cluster slider (2–8)
- checkbox to run Random Forest

---

## 7) `visualizations/` — Drawing layer

### `charts.py`
Reusable Plotly functions. Pages do **not** write Plotly code from scratch every time.

Common functions:
- `bar_chart`, `grouped_bar`
- `donut_chart`, `line_chart`, `area_chart`
- `scatter_chart`, `heatmap`, `histogram`
- `treemap`, `gauge_chart`, `confusion_matrix_chart`

All go through `_theme(fig)` for dark styling.

### `kpis.py`
- `kpi_card(...)` → one big number card (HTML)
- `metric_row([...])` → many cards in one row
- `section_header(title, subtitle)` → blue left-border heading

**Say this:**  
> “We separated presentation helpers so chart style stays consistent across pages.”

---

## 8) Config & theme files

| File | Role |
|---|---|
| `config/settings.py` | colors, optional MySQL env vars (app mainly uses SQLite) |
| `.streamlit/config.toml` | Streamlit dark theme colors |
| `assets/style.css` | Extra custom CSS (hero banner, cards) |
| `requirements.txt` | Libraries to install |

---

# PART C — Mini Code Walk Scripts (practice speaking)

## Walk 1 (2 minutes) — Data path
1. Open `database/loader.py` → “This loads CSV/Kaggle/synthetic.”  
2. Open `schema.sql` → “This is table structure.”  
3. Open `connection.py` → “This is query_df bridge.”  
4. Open `analytics/overview.py` → “This asks KPI SQL.”  
5. Open `pages/01_Overview.py` → “This displays KPIs and charts.”

## Walk 2 (2 minutes) — ML path
1. Open `ml_insights.py`  
2. Point to `run_clustering` → scaler + KMeans + PCA  
3. Point to `run_test_result_classification` → RandomForest + split  
4. Point to `compute_risk_scores` → weighted formula  
5. Open `06_ML_Insights.py` → tabs call these functions

---

# PART D — Coding Viva Cheat Answers

**Q1. Explain end-to-end request flow when I open Overview page.**  
Streamlit loads `01_Overview.py` → calls `get_kpis()` etc. → those call `query_df(SQL)` → SQLite returns rows → Pandas DataFrame → KPI cards + Plotly charts shown.

**Q2. Where is business logic?**  
In `analytics/`, not inside page files. Pages are presentation.

**Q3. Why not put SQL inside pages?**  
Separation of concerns. Easier to maintain, reuse, and test.

**Q4. What is LabelEncoder?**  
Converts text categories (Male/Female) into numbers (0/1) for ML models.

**Q5. What is train_test_split?**  
Splits data into training set (learn) and test set (evaluate). We use 80/20.

**Q6. What is confusion matrix?**  
Table showing correct vs wrong predictions for each class.

**Q7. What is feature importance?**  
Which input columns most influenced Random Forest decisions.

**Q8. Difference between K-Means and Random Forest in your code?**  
K-Means = unsupervised grouping (no labels). Random Forest = supervised prediction of test_results.

**Q9. How does Streamlit multi-page work?**  
Files inside `pages/` starting with numbers auto-appear in sidebar.

**Q10. Can this use MySQL?**  
`settings.py` has MySQL URL style, but current working backend is SQLite via `connection.py` for easy demo.

---

# PART E — Super Short Memory Card

```
app.py / pages     = SCREEN
analytics          = SQL BRAIN
connection.query_df= BRIDGE
healthcare.db      = STORAGE
loader.py          = DATA ENTRY + CLEANING
charts.py / kpis.py= DRAWING TOOLS
ml_insights.py     = AI BRAIN
```

### 5 functions you MUST know by name
1. `query_df()`  
2. `_preprocess()` in loader  
3. `get_kpis()`  
4. `run_clustering()`  
5. `run_test_result_classification()` / `compute_risk_scores()`

### One closing coding sentence
> “Every screen follows the same flow: Page → Analytics SQL → query_df → DataFrame → Chart/KPI. ML is an extra analytics module using scikit-learn on the same database data.”

---

Study tip: open these 5 files side by side while reading this note:
1. `database/loader.py`
2. `database/connection.py`
3. `analytics/overview.py`
4. `pages/01_Overview.py`
5. `analytics/ml_insights.py`
