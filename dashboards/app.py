import os
import sqlite3
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="UN SDG 4: Quality Education Dashboard",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for App Container
st.markdown("""
<style>
    .main {
        background-color: #0f172a;
        color: #f8fafc;
    }
</style>
""", unsafe_allow_html=True)

# Database Connection Helper
def get_connection():
    db_path = os.path.abspath(os.path.join("data", "processed", "ods4_education.db"))
    if not os.path.exists(db_path):
        db_path = os.path.abspath(os.path.join("..", "data", "processed", "ods4_education.db"))
    return sqlite3.connect(db_path)

@st.cache_data
def run_sql(query):
    conn = get_connection()
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# Main Header
st.title("🎓 UN SDG 4: Quality Education — Global Analytics Dashboard")
st.caption("Data Engineering ETL Architecture | Global Education & Socioeconomic Indicators (1990 - 2024)")
st.markdown("---")

# Sidebar Filters powered by SQL Queries
conn = get_connection()
regions = ["All Regions"] + list(pd.read_sql("SELECT DISTINCT region FROM dim_country ORDER BY region", conn)["region"])
income_groups = ["All Income Groups"] + list(pd.read_sql("SELECT DISTINCT income_group FROM dim_country ORDER BY income_group", conn)["income_group"])
year_range = pd.read_sql("SELECT MIN(year) as min_y, MAX(year) as max_y FROM dim_time", conn).iloc[0]
conn.close()

st.sidebar.header("🔍 Global Filters")
selected_region = st.sidebar.selectbox("Geographical Region", regions)
selected_income = st.sidebar.selectbox("World Bank Income Group", income_groups)
selected_years = st.sidebar.slider("Time Period (Years)", int(year_range["min_y"]), int(year_range["max_y"]), (2000, 2024))

# Build Dynamic SQL Query based on filters
where_clauses = [f"year BETWEEN {selected_years[0]} AND {selected_years[1]}"]
if selected_region != "All Regions":
    where_clauses.append(f"region = '{selected_region}'")
if selected_income != "All Income Groups":
    where_clauses.append(f"income_group = '{selected_income}'")

where_str = " WHERE " + " AND ".join(where_clauses)

sql_filtered = f"SELECT * FROM v_sdg4_country_trends {where_str}"
df = run_sql(sql_filtered)

# KPI Overview Section
col1, col2, col3, col4 = st.columns(4)

total_countries = df["country_code"].nunique()
avg_sdg4 = round(df["sdg4_index_score"].mean(), 1)
avg_literacy = round(df["literacy_rate_youth"].mean(), 1)
avg_spending = round(df["govt_expenditure_education_pct_gdp"].mean(), 2)

def render_kpi(title, value):
    return f"""
    <div style="background-color: #1e293b; padding: 16px 20px; border-radius: 10px; border: 1px solid #334155; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);">
        <div style="color: #ffffff !important; font-size: 0.95rem; font-weight: 600; margin-bottom: 6px;">{title}</div>
        <div style="color: #ffffff !important; font-size: 1.8rem; font-weight: 800;">{value}</div>
    </div>
    """

col1.markdown(render_kpi("Tracked Countries", f"{total_countries} Nations"), unsafe_allow_html=True)
col2.markdown(render_kpi("Avg SDG 4 Index Score", f"{avg_sdg4} / 100"), unsafe_allow_html=True)
col3.markdown(render_kpi("Youth Literacy Rate", f"{avg_literacy}%"), unsafe_allow_html=True)
col4.markdown(render_kpi("Govt Education Spend", f"{avg_spending}% GDP"), unsafe_allow_html=True)

st.markdown("---")

# Navigation Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Global SDG 4 Performance", 
    "⚖️ Gender Parity & Equity", 
    "💰 Public Expenditure & Teachers", 
    "💻 Live SQL Query Console"
])

# Tab 1: Global Overview
with tab1:
    st.subheader("Regional Progress & Country Rankings")
    
    col_left, col_right = st.columns([6, 4])
    
    with col_left:
        # Regional SDG 4 Score Timeline
        df_region_time = df.groupby(["region", "year"])["sdg4_index_score"].mean().reset_index()
        fig_timeline = px.line(
            df_region_time, 
            x="year", 
            y="sdg4_index_score", 
            color="region",
            title="Average SDG 4 Index Progression over Time",
            labels={"sdg4_index_score": "SDG 4 Score", "year": "Year"},
            template="plotly_dark"
        )
        fig_timeline.update_layout(height=420)
        st.plotly_chart(fig_timeline, use_container_width=True)

    with col_right:
        # Top 10 Countries by Recent SDG 4 Score
        recent_year = selected_years[1]
        df_recent = df[df["year"] == recent_year].groupby("country_name")["sdg4_index_score"].mean().reset_index()
        df_top10 = df_recent.sort_values("sdg4_index_score", ascending=False).head(10)
        
        fig_top = px.bar(
            df_top10,
            x="sdg4_index_score",
            y="country_name",
            orientation="h",
            title=f"Top 10 Performing Nations in {recent_year}",
            color="sdg4_index_score",
            color_continuous_scale="Viridis",
            template="plotly_dark"
        )
        fig_top.update_layout(yaxis={'categoryorder':'total ascending'}, height=420)
        st.plotly_chart(fig_top, use_container_width=True)

# Tab 2: Gender Equity
with tab2:
    st.subheader("Gender Parity Index (GPI) & Enrollment Disparities")
    
    col_gpi1, col_gpi2 = st.columns(2)
    
    with col_gpi1:
        fig_gpi_dist = px.histogram(
            df,
            x="gender_parity_index_primary",
            color="income_group",
            title="Primary Gender Parity Index Distribution by Income Group",
            labels={"gender_parity_index_primary": "Gender Parity Index (GPI)"},
            barmode="overlay",
            template="plotly_dark"
        )
        st.plotly_chart(fig_gpi_dist, use_container_width=True)

    with col_gpi2:
        df_gpi_cat = df["gender_gap_severity"].value_counts().reset_index()
        df_gpi_cat.columns = ["Gender Parity Status", "Count"]
        fig_pie = px.pie(
            df_gpi_cat,
            names="Gender Parity Status",
            values="Count",
            title="Global Proportion of Gender Parity Statuses",
            hole=0.4,
            template="plotly_dark"
        )
        st.plotly_chart(fig_pie, use_container_width=True)

# Tab 3: Expenditure Analysis
with tab3:
    st.subheader("Public Spending vs Education Outcomes")
    
    col_exp1, col_exp2 = st.columns(2)
    
    with col_exp1:
        fig_scatter = px.scatter(
            df,
            x="govt_expenditure_education_pct_gdp",
            y="sdg4_index_score",
            color="region",
            size="population_school_age_millions",
            hover_name="country_name",
            trendline="ols",
            title="Govt Expenditure (% GDP) vs SDG 4 Score",
            labels={"govt_expenditure_education_pct_gdp": "Education Budget (% GDP)", "sdg4_index_score": "SDG 4 Score"},
            template="plotly_dark"
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

    with col_exp2:
        fig_box = px.box(
            df,
            x="income_group",
            y="pupil_teacher_ratio_primary",
            color="income_group",
            title="Primary Student-to-Teacher Ratio by Income Group",
            labels={"pupil_teacher_ratio_primary": "Pupil-Teacher Ratio"},
            template="plotly_dark"
        )
        st.plotly_chart(fig_box, use_container_width=True)

# Tab 4: Live SQL Console
with tab4:
    st.subheader("💻 Interactive SQL Query Terminal")
    st.markdown("Query the SQLite Data Warehouse (`ods4_education.db`) directly using standard SQL syntax.")
    
    default_sql = """SELECT 
    c.country_name,
    c.region,
    c.income_group,
    ROUND(AVG(f.sdg4_index_score), 2) AS avg_sdg4_score,
    ROUND(AVG(f.govt_expenditure_education_pct_gdp), 2) AS avg_education_budget_gdp
FROM fact_education_indicators f
JOIN dim_country c ON f.country_key = c.country_key
GROUP BY c.country_name, c.region, c.income_group
ORDER BY avg_sdg4_score DESC
LIMIT 15;"""

    user_query = st.text_area("SQL Query Input", value=default_sql, height=160)
    
    if st.button("Execute SQL Query", type="primary"):
        try:
            df_sql_res = run_sql(user_query)
            st.success(f"Query executed successfully! Returned {len(df_sql_res)} rows.")
            st.dataframe(df_sql_res, use_container_width=True)
        except Exception as e:
            st.error(f"SQL Execution Error: {e}")

st.markdown("---")
st.caption("Universidad Autónoma de Occidente — ETL Project Delivery | Data Engineering & AI")
