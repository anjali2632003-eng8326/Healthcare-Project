# Healthcare Data Analysis & Visualization Dashboard
 
**MCA Project — Anjali Kumari (A24CA1895)**  
**Guide: Divakar Purohit, Sr. Data Analyst**  
**Institution: Centre for Distance and Online Education — Online MCA Programme, 4th Semester**
 
---
 
## Project Overview
 
A production-grade, multi-page **Streamlit** healthcare analytics dashboard powered by **Python** and **SQLite** (zero-config, no server needed). Based on the real Kaggle `prasad22/healthcare-dataset` (10,000 patient records). Falls back to synthetic data if Kaggle credentials are unavailable.
 
---
 
## Quick Start (3 steps)
 
### Step 1 — Install dependencies
```bash
pip install -r requirements.txt
```
 
### Step 2 — Load the dataset
```bash
python database/loader.py
```
 
This will auto-generate 10,000 synthetic records if the Kaggle dataset is not available locally.  
**To use the real Kaggle dataset:**
1. Download from: https://www.kaggle.com/datasets/prasad22/healthcare-dataset
2. Place `healthcare_dataset.csv` in the `data/` folder
3. Re-run: `python database/loader.py`
 
### Step 3 — Launch the dashboard
```bash
streamlit run app.py
```
Open **http://localhost:8501** in your browser.
 
---
 
## Dashboard Pages
 
| # | Page | Description |
|---|------|-------------|
| 🏠 | **Home** | Navigation hub with project overview |
| 📈 | **Overview** | Executive KPIs, monthly trends, recent records |
| 👥 | **Patient Demographics** | Age groups, gender, blood type, insurance breakdown |
| 🦠 | **Disease Analysis** | Conditions, medications, test results, treemap |
| 🏨 | **Hospital Operations** | Hospital/doctor performance, LOS, admission patterns |
| 💰 | **Financial Analysis** | Revenue, billing distribution, payer mix, high-value cases |
| 🤖 | **ML Insights** | K-Means clustering, Random Forest prediction, risk scoring |
 
---
 
## Project Structure
 
```
healthcare/
├── app.py                         # Streamlit home page + navigation
├── requirements.txt               # Python dependencies
├── database/
│   ├── connection.py              # SQLite connection (SQLAlchemy)
│   ├── schema.sql                 # Database schema
│   └── loader.py                  # Dataset loader (Kaggle / CSV / Synthetic)
├── analytics/
│   ├── overview.py                # KPIs & trend queries
│   ├── patient_analytics.py       # Demographics queries
│   ├── disease_analytics.py       # Conditions & medication queries
│   ├── hospital_analytics.py      # Hospital/doctor/LOS queries
│   ├── financial_analytics.py     # Revenue & billing queries
│   └── ml_insights.py             # K-Means, Random Forest, Risk Scoring
├── visualizations/
│   ├── charts.py                  # 14 reusable Plotly chart builders
│   └── kpis.py                    # KPI card components
├── pages/                         # Streamlit multi-page app pages
│   ├── 01_Overview.py
│   ├── 02_Patient_Demographics.py
│   ├── 03_Disease_Analysis.py
│   ├── 04_Hospital_Operations.py
│   ├── 05_Financial_Analysis.py
│   └── 06_ML_Insights.py
├── assets/
│   └── style.css                  # Dark glassmorphism theme
├── data/
│   └── healthcare.db              # SQLite database (auto-created)
└── .streamlit/
    └── config.toml                # Dark theme configuration
```
 
---
 
## Technology Stack
 
| Layer | Technology |
|-------|------------|
| **UI Framework** | Streamlit 1.59 |
| **Database** | SQLite (via SQLAlchemy) |
| **Data Processing** | Pandas, NumPy |
| **Visualizations** | Plotly Express |
| **Machine Learning** | scikit-learn (K-Means, Random Forest, PCA) |
| **Data Generation** | Faker |
| **Dataset** | Kaggle — prasad22/healthcare-dataset |
 
---
 
## Dataset
 
- **Source**: [Kaggle — prasad22/healthcare-dataset](https://www.kaggle.com/datasets/prasad22/healthcare-dataset)
- **License**: CC0 (Public Domain)
- **Records**: 10,000 patient records
- **Columns**: Name, Age, Gender, Blood Type, Medical Condition, Date of Admission, Doctor, Hospital, Insurance Provider, Billing Amount, Room Number, Admission Type, Discharge Date, Medication, Test Results
 
---
 
## ML Features
 
- **Patient Segmentation**: K-Means clustering with PCA 2-D visualization (configurable 2–8 clusters)
- **Test Result Prediction**: Random Forest classifier (Normal / Abnormal / Inconclusive) with confusion matrix
- **Risk Scoring**: Composite 0–100 risk score based on age, billing, LOS, test results, and admission type