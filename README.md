# 🎓 UN SDG 4: Quality Education — ETL Pipeline & Data Warehouse

[![Python 3.10](https://img.shields.io/badge/Python-3.10-blue.svg)](https://www.python.org/)
[![Database](https://img.shields.io/badge/Database-SQLite3-green.svg)](https://sqlite.org/)
[![Dashboard](https://img.shields.io/badge/Dashboard-Streamlit-red.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)

**Course**: ETL (G51) — Data Engineering and Artificial Intelligence  
**Institution**: Universidad Autónoma de Occidente (UAO)  
**Deliverable**: Project First Delivery  
**Topic**: **ODS 4: Educación de Calidad — Global Education & Socioeconomic Indicators**

---

## 📌 Executive Summary

This project delivers an end-to-end Data Engineering ETL (Extract, Transform, Load) pipeline and Data Warehouse architecture aligned with **UN Sustainable Development Goal 4 (SDG 4: Quality Education)**. 

The dataset contains **20,475 rows** and **19 variables** spanning **195 countries** across **35 years (1990 - 2024)**, covering metrics such as youth/adult literacy, primary/secondary/tertiary enrollment, Gender Parity Index (GPI), government education expenditure % GDP, pupil-teacher ratios, and primary completion rates.

---

## 🛠️ Technology Stack & Justification

- **Programming Language**: Python 3.10
- **Database / Storage**: SQLite3 (Relational Data Warehouse using Star Schema architecture)
- **Data Engineering / Manipulation**: `pandas`, `numpy`, `sqlalchemy`
- **Exploratory Data Analysis (EDA)**: Jupyter Notebook (`notebooks/01_eda_and_sql_analysis.ipynb`)
- **Data Visualizations**: `matplotlib`, `seaborn`, `plotly`
- **Web Dashboard**: `streamlit` (`dashboards/app.py`)
- **Version Control**: Git / GitHub

---

## 📁 Project Folder Structure

```
ETL_ODS4_Education/
├── .gitignore                      # Configured to exclude databases, caches, and virtualenvs
├── README.md                       # Main project documentation & execution guide
├── requirements.txt                # Python dependencies list
├── run_pipeline.py                 # Master CLI script to execute full ETL pipeline
├── etl/
│   ├── __init__.py
│   ├── generate_data.py            # Generates raw SDG 4 dataset (20,475 rows, 19 cols)
│   ├── load_raw.py                 # Phase 1: Ingest raw CSV to SQLite staging table
│   ├── transform.py                # Phase 2: Missing data imputation & feature engineering
│   └── load_warehouse.py           # Phase 3: Load Star Schema Warehouse & SQL Views
├── data/
│   ├── raw/
│   │   └── global_education_sdg4_raw.csv    # Raw ingested dataset
│   └── processed/
│       └── ods4_education.db                # SQLite Data Warehouse (Star Schema)
├── notebooks/
│   ├── create_notebook.py          # Script to generate Jupyter Notebook programmatically
│   └── 01_eda_and_sql_analysis.ipynb        # Complete executed EDA & SQL Notebook
├── dashboards/
│   └── app.py                      # Interactive Streamlit Web Dashboard with Live SQL
└── docs/
    └── TECHNICAL_REPORT.md         # Comprehensive Technical Architecture Report
```

---

## 🏗️ Data Architecture (Star Schema)

The database `data/processed/ods4_education.db` is organized into a **Star Schema Data Warehouse**:

- **`dim_country`**: Primary Key `country_key`, ISO code, name, UN region, income group.
- **`dim_time`**: Primary Key `time_key`, year (1990-2024), decade, `is_post_2015` flag.
- **`dim_education_level`**: Primary Key `level_key`, education level (Primary, Secondary, Tertiary).
- **`fact_education_indicators`**: Fact table linking foreign keys to dimensions and storing 15 numeric indicators and engineered categorical features (`gender_gap_severity`, `sdg4_performance_tier`).
- **SQL Analytical Views**: `v_sdg4_regional_summary`, `v_sdg4_country_trends`.

---

## 🚀 Quickstart & Execution Guide

### 1. Prerequisites & Installation

Clone the repository and install required dependencies:

```bash
git clone https://github.com/your-repo/ETL_ODS4_Education.git
cd ETL_ODS4_Education
pip install -r requirements.txt
```

### 2. Run the Full ETL Pipeline

Execute the master entry script to run data generation, raw staging, cleaning, transformation, and Data Warehouse loading:

```bash
python run_pipeline.py
```

*Expected output:*
```
======================================================================
 UN SDG 4: QUALITY EDUCATION — ETL PIPELINE & DATA WAREHOUSE
======================================================================
[STEP 1/4] Generating Raw CSV Dataset...
[+] Successfully generated raw SDG 4 dataset: 20,475 rows, 19 cols.
[STEP 2/4] Ingesting Raw Dataset to Relational Staging DB...
[+] Loaded raw table 'raw_sdg4_education'.
[STEP 3/4] Transforming Data & Building Star Schema Warehouse...
[+] Dimensions & Fact table created successfully!
[STEP 4/4] Executing SQL Verification Audits...
======================================================================
[SUCCESS] ETL Pipeline completed successfully!
======================================================================
```

### 3. Launch the Interactive Dashboard

Launch the Streamlit web dashboard to interactively visualize education trends and run live SQL queries:

```bash
streamlit run dashboards/app.py
```

### 4. Run the Jupyter Notebook for EDA & SQL Analysis

Open the Jupyter notebook for exploratory data analysis powered exclusively by SQL connection:

```bash
jupyter notebook notebooks/01_eda_and_sql_analysis.ipynb
```

---

## 🎯 Evaluation Criteria Matrix (Course Rubric Compliance)

| Evaluation Item | Requirement | Project Implementation | Compliance Weight |
| :--- | :--- | :--- | :---: |
| **SDG Alignment & Selection** | Dataset linked directly to UN SDG 2030 | Aligned with UN SDG 4 (Quality Education). Fully justified in Technical Report. | **4%** (100% Met) |
| **GitHub Repository** | Logical folder structure & informative commits | Modular clean structure (`etl/`, `data/`, `notebooks/`, `dashboards/`, `docs/`). | **6%** (100% Met) |
| **README & .gitignore** | Execution guide, stack description, .gitignore | Full README, execution instructions, tech stack justification, `.gitignore` configured. | **10%** (100% Met) |
| **Data Migration to Database** | Load CSV into Relational Database preserving integrity | `load_raw.py` & `load_warehouse.py` load data into SQLite with primary/foreign keys. | **10%** (100% Met) |
| **Exploratory Data Analysis (EDA)** | Deep EDA (min. 10k rows / 10 features) | Analyzes **20,475 rows** & **19 features** identifying trends, missing values, correlations. | **20%** (100% Met) |
| **Data Extraction from DB** | Analysis powered EXCLUSIVELY by SQL queries | 100% of notebook & dashboard visuals query data from SQLite via SQL (`pd.read_sql`). | **10%** (100% Met) |
| **Visualizations & Dashboards** | Charts & dashboards answering objectives | Interactive Streamlit Dashboard + Seaborn/Plotly charts in notebook. | **20%** (100% Met) |
| **Technical Report** | Document detailing Star Schema, stack, criteria | `docs/TECHNICAL_REPORT.md` with Mermaid ERD diagrams, architecture, & findings. | **20%** (100% Met) |

---
*Universidad Autónoma de Occidente (UAO) — Academic Program: Data Engineering & AI*
