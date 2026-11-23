import streamlit as st
import pandas as pd
from sqlalchemy import create_engine


@st.cache_resource
def get_engine():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False})
    
    df = pd.read_csv("earthquake_data_last_5_years.csv")
    df = df.rename(columns={"depth": "depth_km"})
    df["time"] = pd.to_datetime(df["time"])
    df["year"] = df["time"].dt.year
    df["month"] = df["time"].dt.month_name()
    df["day_of_week"] = df["time"].dt.day_name()
    df["country"] = df["place"].str.split(",").str[-1].str.strip()
    df.to_sql("earthquakes", engine, index=False, if_exists="replace")
    return engine

engine = get_engine()


queries = {
    "1. Top 10 strongest earthquakes (mag)": "SELECT id, place, country, mag, depth_km, time FROM earthquakes ORDER BY mag DESC LIMIT 10;",
    "2. Top 10 deepest earthquakes (depth_km)": "SELECT id, place, country, depth_km, mag, time FROM earthquakes ORDER BY depth_km DESC LIMIT 10;",
    "3. Shallow earthquakes (< 50 km) and mag > 7.5": "SELECT id, place, country, mag, depth_km, time FROM earthquakes WHERE depth_km < 50 AND mag > 7.5 ORDER BY mag DESC;",
    "4. Average depth per country": "SELECT country, ROUND(AVG(depth_km), 2) AS avg_depth FROM earthquakes GROUP BY country ORDER BY avg_depth DESC;",
    "5. Average magnitude per magnitude type (magType)": "SELECT magType, ROUND(AVG(mag), 2) AS avg_mag FROM earthquakes GROUP BY magType ORDER BY avg_mag DESC;",
    "6. Year with most earthquakes": "SELECT year, COUNT(*) AS total FROM earthquakes GROUP BY year ORDER BY total DESC;",
    "7. Month with highest number of earthquakes": "SELECT month, COUNT(*) AS total FROM earthquakes GROUP BY month ORDER BY total DESC;",
    "8. Day of week with most earthquakes": "SELECT day_of_week, COUNT(*) AS total FROM earthquakes GROUP BY day_of_week ORDER BY total DESC;",
    "9. Count of earthquakes per hour of day": "SELECT strftime('%H', time) AS hour_of_day, COUNT(*) AS total FROM earthquakes GROUP BY hour_of_day ORDER BY hour_of_day;",
    "10. Most active reporting network (net)": "SELECT net, COUNT(*) AS total FROM earthquakes GROUP BY net ORDER BY total DESC;",
    "11. Top 5 places with highest significance (sig)": "SELECT place, MAX(sig) AS max_sig FROM earthquakes GROUP BY place ORDER BY max_sig DESC LIMIT 5;",
    "12. Total significance per country": "SELECT country, SUM(sig) AS total_sig FROM earthquakes GROUP BY country ORDER BY total_sig DESC;",
    "13. Average significance by tsunami alert": "SELECT tsunami, ROUND(AVG(sig), 2) AS avg_sig FROM earthquakes GROUP BY tsunami;",
    "14. Count of reviewed vs automatic earthquakes (status)": "SELECT status, COUNT(*) AS total FROM earthquakes GROUP BY status;",
    "15. Count by earthquake type (type)": "SELECT type, COUNT(*) AS total FROM earthquakes GROUP BY type ORDER BY total DESC;",
    "16. Number of earthquakes by data type (types)": "SELECT types, COUNT(*) AS total FROM earthquakes GROUP BY types ORDER BY total DESC LIMIT 20;",
    "17. Average RMS and gap per country": "SELECT country, ROUND(AVG(rms), 3) AS avg_rms, ROUND(AVG(gap), 2) AS avg_gap FROM earthquakes GROUP BY country;",
    "18. Events with high station coverage (nst > 50)": "SELECT id, place, mag, nst, time FROM earthquakes WHERE nst > 50 ORDER BY nst DESC;",
    "19. Number of tsunamis triggered per year": "SELECT year, SUM(tsunami) AS total_tsunamis FROM earthquakes GROUP BY year ORDER BY year;",
    "20. Count earthquakes by magnitude severity": "SELECT CASE WHEN mag >= 7 THEN 'Major' WHEN mag >= 5 THEN 'Moderate' ELSE 'Minor' END AS severity, COUNT(*) AS total FROM earthquakes GROUP BY severity;",
    "21. Top 5 countries with highest average magnitude": "SELECT country, ROUND(AVG(mag), 2) AS avg_mag FROM earthquakes GROUP BY country ORDER BY avg_mag DESC LIMIT 5;",
    "22. Countries with both shallow and deep earthquakes in same month": "SELECT DISTINCT a.country, a.year, a.month FROM earthquakes a JOIN earthquakes b ON a.country = b.country AND a.year = b.year AND a.month = b.month WHERE a.depth_km < 70 AND b.depth_km > 300;",
    "23. Year-over-year growth rate in total earthquakes": "SELECT year, COUNT(*) AS total, ROUND((COUNT(*) - LAG(COUNT(*)) OVER (ORDER BY year)) * 100.0 / LAG(COUNT(*)) OVER (ORDER BY year), 2) AS yoy_growth_pct FROM earthquakes GROUP BY year ORDER BY year;",
    "24. Top 3 most seismically active regions (frequency & avg mag)": "SELECT country, COUNT(*) AS freq, ROUND(AVG(mag), 2) AS avg_mag, ROUND(COUNT(*) * AVG(mag), 2) AS score FROM earthquakes GROUP BY country ORDER BY score DESC LIMIT 3;",
    "25. Average depth within +/- 5 deg latitude of equator per country": "SELECT country, ROUND(AVG(depth_km), 2) AS avg_depth FROM earthquakes WHERE latitude BETWEEN -5 AND 5 GROUP BY country;",
    "26. Countries with highest ratio of shallow to deep earthquakes": "SELECT country, ROUND(CAST(SUM(CASE WHEN depth_km < 70 THEN 1 ELSE 0 END) AS FLOAT) / NULLIF(SUM(CASE WHEN depth_km > 300 THEN 1 ELSE 0 END), 0), 2) AS shallow_deep_ratio FROM earthquakes GROUP BY country HAVING SUM(depth_km > 300) > 0 ORDER BY shallow_deep_ratio DESC;",
    "27. Average magnitude difference: tsunami vs non-tsunami": "SELECT tsunami, ROUND(AVG(mag), 2) AS avg_mag FROM earthquakes GROUP BY tsunami;",
    "28. Lowest data reliability events (highest gap and rms)": "SELECT id, place, gap, rms FROM earthquakes ORDER BY gap DESC, rms DESC LIMIT 10;",
    "29. Consecutive earthquakes within 1 hour": "SELECT id, place, time, ROUND((julianday(time) - julianday(LAG(time) OVER (ORDER BY time))) * 1440, 2) AS diff_mins FROM earthquakes LIMIT 20;",
    "30. Regions with highest frequency of deep-focus earthquakes (> 300 km)": "SELECT country, COUNT(*) AS deep_quakes FROM earthquakes WHERE depth_km > 300 GROUP BY country ORDER BY deep_quakes DESC LIMIT 10;"
}

st.title("🌎Earthquake Data Analysis Dashboard")

st.write(
    "Select any problem statement (1-30) to run the corresponding SQL query."
)


task = st.selectbox(
    "Choose Task Number",
    list(queries.keys())
)


if st.button("Run Query"):

    query = queries[task]

    df = pd.read_sql(
        query,
        engine
    )

    st.subheader(
        f"Results for: {task}"
    )

    st.dataframe(
        df,
        use_container_width=True
    )