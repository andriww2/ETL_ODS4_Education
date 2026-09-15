import time
import sqlite3
from etl.generate_data import generate_sdg4_dataset
from etl.load_raw import load_raw_to_db
from etl.load_warehouse import load_star_schema

def main():
    print("=" * 70)
    print(" UN SDG 4: QUALITY EDUCATION — ETL PIPELINE & DATA WAREHOUSE")
    print(" Global Education & Socioeconomic Indicators Architecture")
    print("=" * 70)
    start_time = time.time()

    # Step 1: Generate / Ensure Raw Data CSV (~20,475 rows, 19 columns)
    print("\n[STEP 1/4] Generating Raw CSV Dataset...")
    csv_path = "data/raw/global_education_sdg4_raw.csv"
    generate_sdg4_dataset(csv_path)

    # Step 2: Load Raw Dataset to SQLite Staging Database
    print("\n[STEP 2/4] Ingesting Raw Dataset to Relational Staging Database...")
    db_path = "data/processed/ods4_education.db"
    load_raw_to_db(csv_path, db_path)

    # Step 3: Transform & Build Star Schema Data Warehouse
    print("\n[STEP 3/4] Transforming Data & Building Star Schema Warehouse...")
    load_star_schema(db_path)

    # Step 4: Verification & SQL Audit
    print("\n[STEP 4/4] Executing SQL Verification Audits...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    queries = [
        ("Total Records in Fact Table", "SELECT COUNT(*) FROM fact_education_indicators;"),
        ("Total Countries Tracked", "SELECT COUNT(*) FROM dim_country;"),
        ("Years Range", "SELECT MIN(year), MAX(year) FROM dim_time;"),
        ("Average SDG 4 Score Global (Post-2015)", "SELECT ROUND(AVG(sdg4_index_score), 2) FROM v_sdg4_country_trends WHERE is_post_2015 = 1;"),
        ("Top 3 Regions by Literacy Rate (2020s)", "SELECT region, ROUND(AVG(avg_youth_literacy), 2) AS literacy FROM v_sdg4_regional_summary WHERE decade = '2020s' GROUP BY region ORDER BY literacy DESC LIMIT 3;")
    ]

    for title, q in queries:
        cursor.execute(q)
        res = cursor.fetchall()
        print(f"  - {title}: {res}")

    conn.close()

    elapsed = time.time() - start_time
    print("\n" + "=" * 70)
    print(f"[SUCCESS] ETL Pipeline completed successfully in {elapsed:.2f} seconds!")
    print(f"Data Warehouse ready at: {db_path}")
    print("=" * 70)

if __name__ == "__main__":
    main()
