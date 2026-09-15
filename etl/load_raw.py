import os
import sqlite3
import pandas as pd

def load_raw_to_db(csv_path="data/raw/global_education_sdg4_raw.csv", db_path="data/processed/ods4_education.db"):
    """
    Phase 1: Ingests raw CSV dataset into a Relational Staging Table in SQLite.
    """
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV file not found at {csv_path}. Please run generate_data.py first.")

    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    df_raw = pd.read_csv(csv_path)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Drop existing staging table if any
    cursor.execute("DROP TABLE IF EXISTS raw_sdg4_education;")
    
    # Insert raw data frame
    df_raw.to_sql("raw_sdg4_education", conn, if_exists="replace", index=False)
    
    # Count rows in raw table
    cursor.execute("SELECT COUNT(*) FROM raw_sdg4_education;")
    row_count = cursor.fetchone()[0]
    
    conn.commit()
    conn.close()

    print(f"[+] [Phase 1: Ingestion] Loaded raw dataset into SQLite DB: '{db_path}'")
    print(f"    - Table: 'raw_sdg4_education'")
    print(f"    - Rows inserted: {row_count:,}")
    return row_count

if __name__ == "__main__":
    load_raw_to_db()
