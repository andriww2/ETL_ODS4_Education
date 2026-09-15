import sqlite3
import pandas as pd
import numpy as np

def transform_sdg4_data(db_path="data/processed/ods4_education.db"):
    """
    Phase 2: Cleans raw data from SQLite database, handles missing values, and creates transformed features.
    Returns cleaned DataFrames ready for Data Warehouse modeling.
    """
    conn = sqlite3.connect(db_path)
    df_raw = pd.read_sql("SELECT * FROM raw_sdg4_education", conn)
    conn.close()

    print(f"[+] [Phase 2: Transformation] Processing {len(df_raw):,} records from raw_sdg4_education...")

    df_clean = df_raw.copy()

    # 1. Missing Value Imputation using regional & income group medians
    num_cols = [
        "govt_expenditure_education_pct_gdp", 
        "tertiary_enrollment_rate", 
        "pupil_teacher_ratio_primary"
    ]

    for col in num_cols:
        if col in df_clean.columns and df_clean[col].isnull().sum() > 0:
            null_count_before = df_clean[col].isnull().sum()
            df_clean[col] = df_clean.groupby(["region", "income_group"])[col].transform(lambda x: x.fillna(x.median()))
            # Global median fallback if group has all NaNs
            df_clean[col] = df_clean[col].fillna(df_clean[col].median())
            print(f"    - Imputed {null_count_before} null values in '{col}' with group medians.")

    # 2. Feature Engineering & Categories
    df_clean["decade"] = df_clean["year"].apply(lambda y: f"{(y // 10) * 10}s")
    df_clean["is_post_2015"] = df_clean["year"].apply(lambda y: 1 if y >= 2015 else 0)

    # Gender Parity Category
    def categorize_gpi(gpi):
        if pd.isnull(gpi):
            return "Unknown"
        elif gpi < 0.85:
            return "Severe Disparity (Male Favored)"
        elif gpi < 0.95:
            return "Moderate Disparity"
        elif gpi <= 1.05:
            return "Gender Parity Achieved"
        else:
            return "Female Dominance (>1.05)"

    df_clean["gender_gap_severity"] = df_clean["gender_parity_index_primary"].apply(categorize_gpi)

    # SDG 4 Achievement Tier
    def categorize_sdg4_score(score):
        if pd.isnull(score):
            return "Unknown"
        elif score >= 80.0:
            return "Tier 1: High Achievement"
        elif score >= 65.0:
            return "Tier 2: Moderate Achievement"
        elif score >= 50.0:
            return "Tier 3: In Progress"
        else:
            return "Tier 4: Critical Need"

    df_clean["sdg4_performance_tier"] = df_clean["sdg4_index_score"].apply(categorize_sdg4_score)

    print("    - Transformation completed successfully. Calculated derived metrics & categories.")
    return df_clean

if __name__ == "__main__":
    transform_sdg4_data()
