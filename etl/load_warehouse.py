import sqlite3
import pandas as pd
from etl.transform import transform_sdg4_data

def load_star_schema(db_path="data/processed/ods4_education.db"):
    """
    Phase 3: Creates Star Schema Data Warehouse (Fact & Dimension Tables + Analytical Views) in SQLite.
    """
    df_clean = transform_sdg4_data(db_path)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 1. Create Dimension Tables
    cursor.executescript("""
    -- Dimension: Country
    DROP TABLE IF EXISTS dim_country;
    CREATE TABLE dim_country (
        country_key INTEGER PRIMARY KEY AUTOINCREMENT,
        country_code TEXT UNIQUE NOT NULL,
        country_name TEXT NOT NULL,
        region TEXT NOT NULL,
        income_group TEXT NOT NULL
    );

    -- Dimension: Time
    DROP TABLE IF EXISTS dim_time;
    CREATE TABLE dim_time (
        time_key INTEGER PRIMARY KEY AUTOINCREMENT,
        year INTEGER UNIQUE NOT NULL,
        decade TEXT NOT NULL,
        is_post_2015 INTEGER NOT NULL
    );

    -- Dimension: Education Level
    DROP TABLE IF EXISTS dim_education_level;
    CREATE TABLE dim_education_level (
        level_key INTEGER PRIMARY KEY AUTOINCREMENT,
        education_level TEXT UNIQUE NOT NULL
    );

    -- Fact Table: Education Indicators
    DROP TABLE IF EXISTS fact_education_indicators;
    CREATE TABLE fact_education_indicators (
        fact_id INTEGER PRIMARY KEY AUTOINCREMENT,
        country_key INTEGER NOT NULL,
        time_key INTEGER NOT NULL,
        level_key INTEGER NOT NULL,
        population_school_age_millions REAL,
        literacy_rate_youth REAL,
        literacy_rate_adult REAL,
        primary_enrollment_rate REAL,
        secondary_enrollment_rate REAL,
        tertiary_enrollment_rate REAL,
        gender_parity_index_primary REAL,
        gender_parity_index_secondary REAL,
        govt_expenditure_education_pct_gdp REAL,
        pupil_teacher_ratio_primary REAL,
        primary_completion_rate REAL,
        sdg4_index_score REAL,
        gender_gap_severity TEXT,
        sdg4_performance_tier TEXT,
        FOREIGN KEY (country_key) REFERENCES dim_country (country_key),
        FOREIGN KEY (time_key) REFERENCES dim_time (time_key),
        FOREIGN KEY (level_key) REFERENCES dim_education_level (level_key)
    );
    """)

    # 2. Populate Dimension Tables
    # dim_country
    dim_c = df_clean[["country_code", "country_name", "region", "income_group"]].drop_duplicates().reset_index(drop=True)
    dim_c.to_sql("dim_country", conn, if_exists="append", index=False)

    # dim_time
    dim_t = df_clean[["year", "decade", "is_post_2015"]].drop_duplicates().sort_values("year").reset_index(drop=True)
    dim_t.to_sql("dim_time", conn, if_exists="append", index=False)

    # dim_education_level
    dim_l = df_clean[["education_level"]].drop_duplicates().reset_index(drop=True)
    dim_l.to_sql("dim_education_level", conn, if_exists="append", index=False)

    # 3. Read surrogate keys back from SQLite
    dim_country_df = pd.read_sql("SELECT country_key, country_code FROM dim_country", conn)
    dim_time_df = pd.read_sql("SELECT time_key, year FROM dim_time", conn)
    dim_level_df = pd.read_sql("SELECT level_key, education_level FROM dim_education_level", conn)

    # 4. Map surrogate keys into fact DataFrame
    fact_df = df_clean.merge(dim_country_df, on="country_code", how="left")
    fact_df = fact_df.merge(dim_time_df, on="year", how="left")
    fact_df = fact_df.merge(dim_level_df, on="education_level", how="left")

    fact_cols = [
        "country_key", "time_key", "level_key",
        "population_school_age_millions", "literacy_rate_youth", "literacy_rate_adult",
        "primary_enrollment_rate", "secondary_enrollment_rate", "tertiary_enrollment_rate",
        "gender_parity_index_primary", "gender_parity_index_secondary",
        "govt_expenditure_education_pct_gdp", "pupil_teacher_ratio_primary",
        "primary_completion_rate", "sdg4_index_score",
        "gender_gap_severity", "sdg4_performance_tier"
    ]

    fact_records = fact_df[fact_cols]
    fact_records.to_sql("fact_education_indicators", conn, if_exists="append", index=False)

    # 5. Create Analytical SQL Views
    cursor.executescript("""
    -- View 1: Regional Summary by Decade
    DROP VIEW IF EXISTS v_sdg4_regional_summary;
    CREATE VIEW v_sdg4_regional_summary AS
    SELECT 
        c.region,
        t.decade,
        ROUND(AVG(f.sdg4_index_score), 2) AS avg_sdg4_score,
        ROUND(AVG(f.literacy_rate_youth), 2) AS avg_youth_literacy,
        ROUND(AVG(f.primary_completion_rate), 2) AS avg_primary_completion,
        ROUND(AVG(f.govt_expenditure_education_pct_gdp), 2) AS avg_govt_expenditure_gdp,
        ROUND(AVG(f.gender_parity_index_primary), 3) AS avg_primary_gpi
    FROM fact_education_indicators f
    JOIN dim_country c ON f.country_key = c.country_key
    JOIN dim_time t ON f.time_key = t.time_key
    GROUP BY c.region, t.decade;

    -- View 2: Country Full Time-Series Analysis
    DROP VIEW IF EXISTS v_sdg4_country_trends;
    CREATE VIEW v_sdg4_country_trends AS
    SELECT 
        c.country_code,
        c.country_name,
        c.region,
        c.income_group,
        t.year,
        t.decade,
        t.is_post_2015,
        l.education_level,
        f.population_school_age_millions,
        f.literacy_rate_youth,
        f.literacy_rate_adult,
        f.primary_enrollment_rate,
        f.secondary_enrollment_rate,
        f.tertiary_enrollment_rate,
        f.gender_parity_index_primary,
        f.gender_parity_index_secondary,
        f.govt_expenditure_education_pct_gdp,
        f.pupil_teacher_ratio_primary,
        f.primary_completion_rate,
        f.sdg4_index_score,
        f.gender_gap_severity,
        f.sdg4_performance_tier
    FROM fact_education_indicators f
    JOIN dim_country c ON f.country_key = c.country_key
    JOIN dim_time t ON f.time_key = t.time_key
    JOIN dim_education_level l ON f.level_key = l.level_key;
    """)

    # Verify counts
    cursor.execute("SELECT COUNT(*) FROM fact_education_indicators;")
    fact_count = cursor.fetchone()[0]

    conn.commit()
    conn.close()

    print(f"[+] [Phase 3: Data Warehouse] Star Schema Data Warehouse successfully built at: '{db_path}'")
    print(f"    - Dimensions created: dim_country ({len(dim_c)} rows), dim_time ({len(dim_t)} rows), dim_education_level ({len(dim_l)} rows)")
    print(f"    - Fact table created: fact_education_indicators ({fact_count:,} rows)")
    print(f"    - Analytical SQL Views: 'v_sdg4_regional_summary', 'v_sdg4_country_trends'")
    return fact_count

if __name__ == "__main__":
    load_star_schema()
