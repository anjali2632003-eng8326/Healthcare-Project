# Healthcare Dashboard — Easy Demo Day Study Notes

**Project:** Healthcare Data Analysis & Visualization Dashboard  
**Type:** MCA / College Project (Streamlit + Python + SQLite + ML)  
**Goal in one line:** Turn 10,000 patient records into interactive charts, KPIs, and ML insights so hospitals can understand patients, diseases, operations, money, and risk.

---

## 1. 30-Second Elevator Pitch (memorize this)

> “Sir/Madam, this is a **Healthcare Analytics Dashboard**.  
> We took a Kaggle dataset of **10,000 patient records**, cleaned it, stored it in **SQLite**, and built a **multi-page Streamlit app**.  
> It shows demographics, disease trends, hospital operations, financial analysis, and also **Machine Learning** — K-Means clustering, Random Forest prediction, and patient risk scoring.  
> Everything runs locally with three commands: install, load data, run Streamlit.”

---

## 2. What Problem Does This Solve? (why this project)

Hospitals collect a lot of data, but raw Excel/CSV is hard to understand.

| Without dashboard | With our dashboard |
|---|---|
| Scattered CSV files | One clean SQLite database |
| Manual Excel charts | Auto interactive Plotly charts |
| Hard to find trends | Instant KPIs + filters |
| No prediction | ML risk + test-result prediction |

**Business value:** management can see revenue, disease burden, doctor/hospital load, and high-risk patients quickly.

---

## 3. Technology Stack (say in viva)

| Layer | Technology | Simple meaning |
|---|---|---|
| UI | **Streamlit** | Python library that creates a website/dashboard without HTML/JS |
| Language | **Python** | Main coding language |
| Database | **SQLite** (+ SQLAlchemy) | File-based DB (`data/healthcare.db`) — no MySQL server needed |
| Data handling | **Pandas, NumPy** | Clean, group, calculate |
| Charts | **Plotly** | Interactive graphs (zoom, hover) |
| ML | **scikit-learn** | K-Means, Random Forest, PCA |
| Fake data (backup) | **Faker** | Creates fake patients if CSV missing |
| Dataset | **Kaggle healthcare-dataset** | Real public domain data (CC0) |

> Tip: If asked “Why SQLite?” → “Zero setup, portable single file, enough for 10k rows, easy to demo on any laptop.”

---

## 4. How to Run (demo setup — practice this)

```bash
pip install -r requirements.txt
python database/loader.py
streamlit run app.py
```

Then open: **http://localhost:8501**

### What each step does
1. `pip install...` → installs Streamlit, pandas, plotly, sklearn, etc.
2. `loader.py` → creates table + loads CSV (or generates synthetic data) into `data/healthcare.db`
3. `streamlit run app.py` → starts the dashboard website

---

## 5. Folder Structure (easy map)

Think of the project like a restaurant:

```
CSV / Kaggle data     = raw ingredients
database/loader.py    = kitchen that cleans & stores food
analytics/*.py        = chefs who prepare specific dishes (SQL queries)
visualizations/*.py   = plating / presentation (charts & KPI cards)
pages/*.py            = menu pages customer sees
app.py                = entrance / home page
```

### Real folders

```
healthcare/
├── app.py                    ← Home page (start here)
├── requirements.txt          ← All libraries needed
├── data/
│   ├── healthcare_dataset.csv
│   └── healthcare.db         ← SQLite database (10,000 rows)
├── database/
│   ├── connection.py         ← Connect + run SQL → DataFrame
│   ├── schema.sql            ← Table structure
│   └── loader.py             ← Load CSV/Kaggle/synthetic into DB
├── analytics/                ← Business logic (SQL queries)
│   ├── overview.py
│   ├── patient_analytics.py
│   ├── disease_analytics.py
│   ├── hospital_analytics.py
│   ├── financial_analytics.py
│   └── ml_insights.py
├── visualizations/
│   ├── charts.py             ← Plotly chart helpers
│   └── kpis.py               ← Big number cards
├── pages/                    ← Streamlit auto-loads these in sidebar
│   ├── 01_Overview.py
│   ├── 02_Patient_Demographics.py
│   ├── 03_Disease_Analysis.py
│   ├── 04_Hospital_Operations.py
│   ├── 05_Financial_Analysis.py
│   └── 06_ML_Insights.py
├── assets/style.css          ← Dark theme styling
└── config/settings.py        ← Colors / optional MySQL settings
```

**Important:** Ignore many `build_*report.py` files at root — those are only for generating the college Word/PDF report, **not** the live dashboard.

---

## 6. Data Flow (very important for viva)

```
Kaggle CSV / Local CSV / Synthetic data
              ↓
     database/loader.py
   (rename columns, clean, age_group, length_of_stay)
              ↓
     SQLite table: healthcare_records
              ↓
     analytics/*.py  (SQL queries via query_df)
              ↓
     pages/*.py      (call analytics + draw charts)
              ↓
     Browser dashboard (Streamlit + Plotly)
```

### Main table columns (memorize a few)

Patient: `patient_name, age, gender, blood_type, age_group`  
Clinical: `medical_condition, medication, test_results`  
Ops: `hospital, doctor, room_number, admission_type, length_of_stay`  
Money: `billing_amount, insurance_provider`  
Dates: `date_of_admission, discharge_date`

**Extra columns we create in preprocessing:**
- `age_group` → Under 18, 18–29, 30–44, 45–59, 60–74, 75+
- `length_of_stay` → discharge − admission (in days)

---

## 7. Page-by-Page Demo Script (what to say while clicking)

### Home (`app.py`)
**Show:** hero banner, 6 page cards, DB connected + record count in sidebar.  
**Say:** “This is the navigation hub. Sidebar shows database is connected and we have 10,000 records.”

---

### Page 01 — Overview
**What it shows:** total records, patients, hospitals, doctors, revenue, avg billing, avg LOS, abnormal test %. Monthly admission/revenue trends. Recent records table.  
**Say:** “This is the executive summary for management — one screen to understand the whole hospital dataset.”  
**Code idea:** `analytics/overview.py` → `get_kpis()`, `get_monthly_trend()`.

---

### Page 02 — Patient Demographics
**What it shows:** age groups, male/female, blood types, insurance providers, age×gender heatmap, age vs billing scatter.  
**Say:** “Who are our patients? Age, gender, blood type, insurance mix — useful for planning and outreach.”  
**Code idea:** `analytics/patient_analytics.py`.

---

### Page 03 — Disease Analysis
**What it shows:** top medical conditions, medications, test results (Normal/Abnormal/Inconclusive), condition trends, treemap.  
**Say:** “Which diseases are most common, which medicines are prescribed, and how abnormal tests vary by condition.”  
**Sidebar filter:** Top N conditions slider.  
**Code idea:** `analytics/disease_analytics.py`.

---

### Page 04 — Hospital Operations
**What it shows:** hospital performance, doctor workload, admission type (Emergency/Elective/Urgent), length of stay, weekly admission pattern, room usage.  
**Say:** “This is operations management — which hospitals/doctors handle more cases, how long patients stay, emergency vs elective load.”  
**Code idea:** `analytics/hospital_analytics.py`.

---

### Page 05 — Financial Analysis
**What it shows:** total/avg/min/max billing, revenue by condition/insurance/hospital, monthly revenue, high-value cases.  
**Say:** “Financial view — where revenue comes from, payer mix (insurance), and expensive cases above a threshold.”  
**Sidebar:** high-value threshold (default ₹30,000).  
**Code idea:** `analytics/financial_analytics.py`.

---

### Page 06 — ML Insights (most impressive page — spend time here)
Three tabs:

#### A) Patient Clustering (K-Means)
- Groups similar patients using age, billing, LOS, gender, admission type, condition.
- Scales features → K-Means → PCA to show clusters in 2D.
- Slider: 2–8 clusters.
- **Say:** “Unsupervised learning. We segment patients into cost/stay groups without labels.”

#### B) Test Result Prediction (Random Forest)
- Predicts Normal / Abnormal / Inconclusive.
- Train/test split 80/20, 100 trees.
- Shows accuracy, confusion matrix, feature importance.
- **Say:** “Supervised classification. Model learns from historical features to predict test outcome.”

#### C) Risk Scoring
- Score 0–100 using weighted formula:
  - 30% age + 30% billing + 25% LOS + 10% abnormal test + 5% emergency
- Tiers: Low / Moderate / High risk.
- **Say:** “Rule-based composite score for prioritizing high-risk patients.”

---

## 8. Code Explained Simply (for viva)

### A) Database connection (`database/connection.py`)

```python
def query_df(sql):
    # run SQL on SQLite and return pandas DataFrame
```

**One-liner:** “Every analytics function calls `query_df()` to get data as a table.”

### B) Loader (`database/loader.py`) — priority order
1. Try Kaggle download  
2. Else use local CSV in `data/`  
3. Else generate 10,000 synthetic rows with Faker  

Then preprocess → insert into `healthcare_records`.

### C) Typical page pattern (all pages follow this)

```
1. set_page_config + load CSS
2. import analytics functions + chart helpers
3. call analytics to get DataFrames
4. show KPI cards (metric_row)
5. draw Plotly charts (st.plotly_chart)
6. show tables (st.dataframe)
```

### D) Architecture pattern name
**Layered architecture:**
- Data layer → `database/`
- Business/analytics layer → `analytics/`
- Presentation layer → `pages/` + `visualizations/`

This is good software design — UI does not contain heavy SQL; SQL lives in analytics modules.

---

## 9. ML in Simple Words (must prepare)

| Topic | Type | Algorithm | Purpose |
|---|---|---|---|
| Clustering | Unsupervised | **K-Means** | Group similar patients |
| PCA | Dimensionality reduction | **PCA** | Plot clusters in 2D |
| Prediction | Supervised | **Random Forest** | Predict test result class |
| Risk | Heuristic / scoring | Weighted formula | Rank patient risk 0–100 |

### Why StandardScaler before K-Means?
Age is ~18–85, billing is thousands. Without scaling, billing dominates distance. Scaling makes features comparable.

### Why Random Forest?
Many trees vote → usually stronger than one decision tree, handles mixed features well, gives feature importance.

---

## 10. Likely Viva Q&A (study answers)

**Q1. What is your project?**  
Healthcare analytics dashboard on 10k patient records with SQL analytics + Plotly charts + ML insights.

**Q2. Frontend or backend?**  
Mostly Python. Streamlit is the UI; SQLite is the backend DB; no separate React/Node app.

**Q3. Why Streamlit?**  
Fast to build interactive dashboards in pure Python; ideal for data science projects.

**Q4. Dataset source?**  
Kaggle `prasad22/healthcare-dataset`, CC0 public domain. Fallback synthetic data if CSV missing.

**Q5. How is length of stay calculated?**  
`discharge_date − date_of_admission` in days, during preprocessing in `loader.py`.

**Q6. Difference between clustering and classification?**  
Clustering = no labels, find groups. Classification = labels exist (Normal/Abnormal/Inconclusive), model learns to predict them.

**Q7. Can this go to production?**  
Yes as a prototype. For real hospitals you’d add auth, HIPAA/privacy, MySQL/Postgres, scheduled ETL, model monitoring.

**Q8. What did you personally implement / understand?**  
Explain confidently: data loading → SQL analytics modules → Streamlit pages → ML tabs. Point to files above.

**Q9. Indexes in schema — why?**  
Faster `GROUP BY` / filters on condition, hospital, doctor, dates, etc.

**Q10. What is SQLAlchemy doing?**  
Python library to connect to DB and run SQL safely; we use it with SQLite URL `sqlite:///data/healthcare.db`.

---

## 11. Demo Day Flow (recommended 8–10 minutes)

1. **Intro (45 sec)** — elevator pitch  
2. **Run app / Home (30 sec)** — show DB connected, 10k records  
3. **Overview (1 min)** — KPIs + monthly trend  
4. **Demographics (1 min)** — age/gender/insurance  
5. **Disease (1 min)** — top conditions + meds + tests  
6. **Operations (1 min)** — hospitals, LOS, admission types  
7. **Financial (1 min)** — revenue + high-value cases filter  
8. **ML page (2–3 min)** — clustering slider, RF accuracy, risk tiers  
9. **Code walk (1 min)** — open `loader.py` → `overview.py` → `01_Overview.py` → `ml_insights.py`  
10. **Close (20 sec)** — “Dashboard converts raw healthcare data into decisions using Python, SQL, visualization, and ML.”

---

## 12. Quick Memory Cheatsheet

- **App start:** `streamlit run app.py`
- **DB file:** `data/healthcare.db`
- **Main table:** `healthcare_records`
- **Rows:** 10,000
- **UI:** Streamlit multi-page (`pages/` folder auto-appears in sidebar)
- **Charts:** Plotly (`visualizations/charts.py`)
- **ML file:** `analytics/ml_insights.py`
- **Best page to impress:** `06_ML_Insights.py`
- **Report scripts:** ignore for live demo

---

## 13. If Something Breaks During Demo

| Problem | Fix |
|---|---|
| Database not connected | Run `python database/loader.py` |
| Empty charts / error | Confirm `data/healthcare.db` exists and has rows |
| Package missing | `pip install -r requirements.txt` |
| Port busy | `streamlit run app.py --server.port 8502` |

---

## Final Confidence Line

> “Our project follows a clean layered design: data is loaded once into SQLite, analytics modules run SQL, visualization helpers draw charts, and Streamlit pages present insights — including unsupervised clustering, supervised prediction, and risk scoring.”

Study this file once fully, then practice the demo flow with the app open. Focus on **Home → Overview → ML Insights → one analytics file + `ml_insights.py`**. That is enough for a strong college demo.
