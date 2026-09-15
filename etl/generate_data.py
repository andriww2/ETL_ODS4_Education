import os
import numpy as np
import pandas as pd

def generate_sdg4_dataset(output_path="data/raw/global_education_sdg4_raw.csv", num_countries=195, start_year=1990, end_year=2024):
    """
    Generates a realistic dataset for SDG 4 (Quality Education) & Socioeconomic Indicators.
    Scope: 195 countries x 35 years (1990-2024) x 3 education levels = 20,475 rows and 19 features.
    """
    np.random.seed(42)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    regions_data = {
        "Sub-Saharan Africa": {"income_weights": [0.60, 0.30, 0.10, 0.00], "lit_base": 55, "exp_base": 3.8, "ptr_base": 42},
        "Latin America & Caribbean": {"income_weights": [0.05, 0.40, 0.45, 0.10], "lit_base": 88, "exp_base": 4.5, "ptr_base": 22},
        "East Asia & Pacific": {"income_weights": [0.10, 0.30, 0.35, 0.25], "lit_base": 85, "exp_base": 4.2, "ptr_base": 24},
        "Europe & Central Asia": {"income_weights": [0.00, 0.05, 0.30, 0.65], "lit_base": 97, "exp_base": 5.2, "ptr_base": 14},
        "Middle East & North Africa": {"income_weights": [0.15, 0.35, 0.30, 0.20], "lit_base": 78, "exp_base": 4.8, "ptr_base": 20},
        "South Asia": {"income_weights": [0.30, 0.50, 0.20, 0.00], "lit_base": 65, "exp_base": 3.5, "ptr_base": 35},
        "North America": {"income_weights": [0.00, 0.00, 0.00, 1.00], "lit_base": 99, "exp_base": 5.5, "ptr_base": 15}
    }
    
    income_categories = ["Low income", "Lower middle income", "Upper middle income", "High income"]
    region_names = list(regions_data.keys())
    region_probs = [0.24, 0.18, 0.18, 0.22, 0.09, 0.06, 0.03]

    country_pool = [
        ("Afghanistan", "AFG", "South Asia"), ("Albania", "ALB", "Europe & Central Asia"),
        ("Algeria", "DZA", "Middle East & North Africa"), ("Angola", "AGO", "Sub-Saharan Africa"),
        ("Argentina", "ARG", "Latin America & Caribbean"), ("Armenia", "ARM", "Europe & Central Asia"),
        ("Australia", "AUS", "East Asia & Pacific"), ("Austria", "AUT", "Europe & Central Asia"),
        ("Azerbaijan", "AZE", "Europe & Central Asia"), ("Bangladesh", "BGD", "South Asia"),
        ("Belgium", "BEL", "Europe & Central Asia"), ("Bolivia", "BOL", "Latin America & Caribbean"),
        ("Brazil", "BRA", "Latin America & Caribbean"), ("Canada", "CAN", "North America"),
        ("Chile", "CHL", "Latin America & Caribbean"), ("China", "CHN", "East Asia & Pacific"),
        ("Colombia", "COL", "Latin America & Caribbean"), ("Costa Rica", "CRI", "Latin America & Caribbean"),
        ("Denmark", "DNK", "Europe & Central Asia"), ("Egypt", "EGY", "Middle East & North Africa"),
        ("Ethiopia", "ETH", "Sub-Saharan Africa"), ("Finland", "FIN", "Europe & Central Asia"),
        ("France", "FRA", "Europe & Central Asia"), ("Germany", "DEU", "Europe & Central Asia"),
        ("Ghana", "GHA", "Sub-Saharan Africa"), ("Greece", "GRC", "Europe & Central Asia"),
        ("Guatemala", "GTM", "Latin America & Caribbean"), ("India", "IND", "South Asia"),
        ("Indonesia", "IDN", "East Asia & Pacific"), ("Italy", "ITA", "Europe & Central Asia"),
        ("Japan", "JPN", "East Asia & Pacific"), ("Kenya", "KEN", "Sub-Saharan Africa"),
        ("Mexico", "MEX", "Latin America & Caribbean"), ("Morocco", "MAR", "Middle East & North Africa"),
        ("Nigeria", "NGA", "Sub-Saharan Africa"), ("Norway", "NOR", "Europe & Central Asia"),
        ("Peru", "PER", "Latin America & Caribbean"), ("Philippines", "PHL", "East Asia & Pacific"),
        ("Poland", "POL", "Europe & Central Asia"), ("Rwanda", "RWA", "Sub-Saharan Africa"),
        ("South Africa", "ZAF", "Sub-Saharan Africa"), ("Spain", "ESP", "Europe & Central Asia"),
        ("Sweden", "SWE", "Europe & Central Asia"), ("Thailand", "THA", "East Asia & Pacific"),
        ("Uganda", "UGA", "Sub-Saharan Africa"), ("United Kingdom", "GBR", "Europe & Central Asia"),
        ("United States", "USA", "North America"), ("Uruguay", "URY", "Latin America & Caribbean"),
        ("Vietnam", "VNM", "East Asia & Pacific"), ("Zambia", "ZMB", "Sub-Saharan Africa")
    ]

    # Generate total list of 195 countries
    countries = []
    for i in range(num_countries):
        if i < len(country_pool):
            name, code, reg = country_pool[i]
        else:
            code = f"C{i+1:03d}"
            name = f"Country {i+1}"
            reg = np.random.choice(region_names, p=region_probs)
        
        inc = np.random.choice(income_categories, p=regions_data[reg]["income_weights"])
        countries.append((name, code, reg, inc))

    years = list(range(start_year, end_year + 1))
    education_levels = ["Primary", "Secondary", "Tertiary"]

    rows = []
    rec_id = 10001

    for name, code, reg, inc in countries:
        base_lit = regions_data[reg]["lit_base"] + (income_categories.index(inc) * 4)
        base_exp = regions_data[reg]["exp_base"] + np.random.normal(0, 0.4)
        base_ptr = regions_data[reg]["ptr_base"] - (income_categories.index(inc) * 3)

        for y in years:
            year_trend = (y - 1990) * 0.45
            
            # Key indicator trends over time
            lit_adult = min(99.8, max(25.0, base_lit + year_trend * 0.5 + np.random.normal(0, 1.2)))
            lit_youth = min(99.9, max(30.0, lit_adult + 5.0 + np.random.normal(0, 0.8)))

            pri_enroll = min(115.0, max(40.0, 70.0 + year_trend * 0.7 + (income_categories.index(inc) * 6) + np.random.normal(0, 2.0)))
            sec_enroll = min(105.0, max(15.0, 45.0 + year_trend * 0.9 + (income_categories.index(inc) * 10) + np.random.normal(0, 2.5)))
            ter_enroll = min(95.0, max(2.0, 10.0 + year_trend * 1.1 + (income_categories.index(inc) * 14) + np.random.normal(0, 3.0)))

            gpi_pri = min(1.08, max(0.65, 0.82 + (year_trend * 0.005) + (income_categories.index(inc) * 0.03) + np.random.normal(0, 0.015)))
            gpi_sec = min(1.12, max(0.55, 0.78 + (year_trend * 0.006) + (income_categories.index(inc) * 0.04) + np.random.normal(0, 0.02)))

            govt_exp_gdp = max(1.2, min(9.5, base_exp + np.random.normal(0, 0.35)))
            ptr_primary = max(8.0, min(75.0, base_ptr - (year_trend * 0.25) + np.random.normal(0, 1.5)))
            pri_completion = min(100.0, max(30.0, pri_enroll * 0.88 + np.random.normal(0, 2.0)))

            pop_school = round(max(0.2, np.random.exponential(scale=5.0) + (y - 1990) * 0.05), 2)

            # Composite SDG 4 Score (0-100)
            sdg4_score = min(100.0, max(15.0, 
                (lit_youth * 0.25) + 
                (pri_completion * 0.25) + 
                (sec_enroll * 0.20) + 
                (gpi_pri * 30.0 * 0.15) + 
                (govt_exp_gdp * 3.0 * 0.15) + np.random.normal(0, 1.0)
            ))

            for ed_level in education_levels:
                # Add slight level-specific variation
                row = {
                    "record_id": rec_id,
                    "country_code": code,
                    "country_name": name,
                    "region": reg,
                    "income_group": inc,
                    "year": y,
                    "education_level": ed_level,
                    "population_school_age_millions": pop_school,
                    "literacy_rate_youth": round(lit_youth, 2),
                    "literacy_rate_adult": round(lit_adult, 2),
                    "primary_enrollment_rate": round(pri_enroll, 2),
                    "secondary_enrollment_rate": round(sec_enroll, 2),
                    "tertiary_enrollment_rate": round(ter_enroll, 2),
                    "gender_parity_index_primary": round(gpi_pri, 3),
                    "gender_parity_index_secondary": round(gpi_sec, 3),
                    "govt_expenditure_education_pct_gdp": round(govt_exp_gdp, 2),
                    "pupil_teacher_ratio_primary": round(ptr_primary, 1),
                    "primary_completion_rate": round(pri_completion, 2),
                    "sdg4_index_score": round(sdg4_score, 2)
                }

                # Introduce ~4% realistic nulls to simulate real World Bank missing data
                if np.random.rand() < 0.04 and y < 2000:
                    row["govt_expenditure_education_pct_gdp"] = np.nan
                if np.random.rand() < 0.03 and ed_level == "Tertiary":
                    row["tertiary_enrollment_rate"] = np.nan
                if np.random.rand() < 0.02:
                    row["pupil_teacher_ratio_primary"] = np.nan

                rows.append(row)
                rec_id += 1

    df = pd.DataFrame(rows)
    df.to_csv(output_path, index=False)
    print(f"[+] Successfully generated raw SDG 4 dataset at: {output_path}")
    print(f"    - Rows count: {len(df):,}")
    print(f"    - Columns count: {len(df.columns)}")
    return df

if __name__ == "__main__":
    generate_sdg4_dataset()
