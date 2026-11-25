import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
import streamlit as st

st.set_page_config(
    page_title="Earthquake Data Analysis Dashboard",
    page_icon="🌎",
    layout="wide",
)


@st.cache_resource
def get_engine():
  return create_engine(
      "mysql+pymysql://root:Aishwaryaraghul0514@localhost:3306/EARTH_DATABASE"
  )


engine = get_engine()

st.title("🌎 Global Seismic Trends: Earthquake Data Analysis")
st.write(
    "Select any analytical task below to run the SQL query against"
    " `EARTH_DATABASE.earth_data` and explore the results."
)

queries = {
    "1. Top 10 Strongest Earthquakes": """
        SELECT id, time, place, mag, magType, depth_km, latitude, longitude, tsunami, status
        FROM earth_data
        WHERE mag IS NOT NULL
        ORDER BY mag DESC
        LIMIT 10;
    """,
    "2. Top 10 Deepest Earthquakes": """
        SELECT id, time, place, depth_km, mag, magType, latitude, longitude, status
        FROM earth_data
        WHERE depth_km IS NOT NULL
        ORDER BY depth_km DESC
        LIMIT 10;
    """,
    "3. Shallow Earthquakes (< 50 km) and Magnitude > 7.5": """
        SELECT id, time, place, mag, depth_km, magType, latitude, longitude, tsunami
        FROM earth_data
        WHERE depth_km < 50 AND mag > 7.5
        ORDER BY mag DESC;
    """,
    "4. Average Magnitude per Magnitude Type (magType)": """
        SELECT
            magType,
            ROUND(AVG(mag), 3) AS average_magnitude,
            COUNT(*) AS earthquake_count
        FROM earth_data
        WHERE mag IS NOT NULL AND magType IS NOT NULL
        GROUP BY magType
        ORDER BY average_magnitude DESC;
    """,
    "5. Year with Most Earthquakes": """
        SELECT
            YEAR(time) AS earthquake_year,
            COUNT(*) AS earthquake_count
        FROM earth_data
        WHERE time IS NOT NULL
        GROUP BY YEAR(time)
        ORDER BY earthquake_count DESC;
    """,
    "6. Month with Highest Number of Earthquakes": """
        SELECT
            MONTH(time) AS month_number,
            MONTHNAME(time) AS month_name,
            COUNT(*) AS earthquake_count
        FROM earth_data
        WHERE time IS NOT NULL
        GROUP BY MONTH(time), MONTHNAME(time)
        ORDER BY earthquake_count DESC;
    """,
    "7. Day of Week with Most Earthquakes": """
        SELECT
            DAYOFWEEK(time) AS day_number,
            DAYNAME(time) AS day_name,
            COUNT(*) AS earthquake_count
        FROM earth_data
        WHERE time IS NOT NULL
        GROUP BY DAYOFWEEK(time), DAYNAME(time)
        ORDER BY earthquake_count DESC;
    """,
    "8. Count of Earthquakes per Hour of Day": """
        SELECT
            HOUR(time) AS hour_of_day,
            COUNT(*) AS earthquake_count
        FROM earth_data
        WHERE time IS NOT NULL
        GROUP BY HOUR(time)
        ORDER BY hour_of_day;
    """,
    "9. Most Active Reporting Network (Top 1)": """
        SELECT
            net,
            COUNT(*) AS earthquake_count
        FROM earth_data
        WHERE net IS NOT NULL
        GROUP BY net
        ORDER BY earthquake_count DESC
        LIMIT 1;
    """,
    "10. All Reporting Networks Ranked by Activity": """
        SELECT
            net,
            COUNT(*) AS earthquake_count
        FROM earth_data
        WHERE net IS NOT NULL
        GROUP BY net
        ORDER BY earthquake_count DESC;
    """,
    "14. Reviewed vs Automatic Earthquakes": """
        SELECT
            status,
            COUNT(*) AS earthquake_count
        FROM earth_data
        WHERE status IS NOT NULL
        GROUP BY status
        ORDER BY earthquake_count DESC;
    """,
    "15. Count by Seismic Event Type": """
        SELECT
            type,
            COUNT(*) AS earthquake_count
        FROM earth_data
        WHERE type IS NOT NULL
        GROUP BY type
        ORDER BY earthquake_count DESC;
    """,
    "16. Top 20 Earthquakes by Associated Data Types": """
        SELECT
            types,
            COUNT(*) AS earthquake_count
        FROM earth_data
        WHERE types IS NOT NULL
        GROUP BY types
        ORDER BY earthquake_count DESC
        LIMIT 20;
    """,
    "18. Events with High Station Coverage (nst > 100)": """
        SELECT
            id, time, place, mag, nst
        FROM earth_data
        WHERE nst > 100
        ORDER BY nst DESC
        LIMIT 500;
    """,
    "19. Number of Tsunamis Triggered per Year": """
        SELECT
            YEAR(time) AS earthquake_year,
            COUNT(*) AS tsunami_count
        FROM earth_data
        WHERE tsunami = 1 AND time IS NOT NULL
        GROUP BY YEAR(time)
        ORDER BY earthquake_year;
    """,
    "20. Count Earthquakes by Alert Level": """
        SELECT
            alert,
            COUNT(*) AS earthquake_count
        FROM earth_data
        WHERE alert IS NOT NULL
        GROUP BY alert
        ORDER BY earthquake_count DESC;
    """,
    "21. Top 5 Places with Highest Average Magnitude (Past 5 Years)": """
        SELECT
            place,
            ROUND(AVG(mag), 2) AS average_magnitude
        FROM earth_data
        WHERE place IS NOT NULL
          AND mag IS NOT NULL
          AND time >= DATE_SUB(CURDATE(), INTERVAL 5 YEAR)
        GROUP BY place
        ORDER BY average_magnitude DESC
        LIMIT 5;
    """,
    "22. Places with Both Shallow (<70km) and Deep (>300km) Quakes in Same Month": """
        SELECT
            place,
            YEAR(time) AS year,
            MONTH(time) AS month,
            MIN(depth_km) AS minimum_depth,
            MAX(depth_km) AS maximum_depth
        FROM earth_data
        WHERE place IS NOT NULL AND depth_km IS NOT NULL
        GROUP BY place, YEAR(time), MONTH(time)
        HAVING MIN(depth_km) < 70 AND MAX(depth_km) > 300
        ORDER BY place, year, month;
    """,
    "23. Year-over-Year Earthquake Growth Rate": """
        WITH yearly_counts AS (
            SELECT
                YEAR(time) AS earthquake_year,
                COUNT(*) AS earthquake_count
            FROM earth_data
            WHERE time IS NOT NULL
            GROUP BY YEAR(time)
        )
        SELECT
            earthquake_year,
            earthquake_count,
            LAG(earthquake_count) OVER (ORDER BY earthquake_year) AS previous_year_count,
            ROUND(
                ((earthquake_count - LAG(earthquake_count) OVER (ORDER BY earthquake_year))
                / NULLIF(LAG(earthquake_count) OVER (ORDER BY earthquake_year), 0)) * 100,
                2
            ) AS yoy_growth_percent
        FROM yearly_counts
        ORDER BY earthquake_year;
    """,
    "24. Top 3 Most Seismically Active Regions": """
        SELECT
            place,
            COUNT(*) AS earthquake_frequency,
            ROUND(AVG(mag), 3) AS average_magnitude,
            ROUND(COUNT(*) * AVG(mag), 2) AS seismic_activity_score
        FROM earth_data
        WHERE place IS NOT NULL AND mag IS NOT NULL
        GROUP BY place
        ORDER BY seismic_activity_score DESC
        LIMIT 3;
    """,
    "25. Average Depth Within ±5° Latitude of Equator (Top 50)": """
        SELECT
            place,
            ROUND(AVG(depth_km), 2) AS average_depth,
            COUNT(*) AS event_count
        FROM earth_data
        WHERE place IS NOT NULL
          AND latitude BETWEEN -5 AND 5
          AND depth_km IS NOT NULL
        GROUP BY place
        ORDER BY average_depth DESC
        LIMIT 50;
    """,
    "26. Top 10 Places with Highest Shallow-to-Deep Earthquake Ratio": """
        SELECT
            place,
            SUM(CASE WHEN depth_km < 70 THEN 1 ELSE 0 END) AS shallow_count,
            SUM(CASE WHEN depth_km > 300 THEN 1 ELSE 0 END) AS deep_count,
            ROUND(
                SUM(CASE WHEN depth_km < 70 THEN 1 ELSE 0 END) /
                NULLIF(SUM(CASE WHEN depth_km > 300 THEN 1 ELSE 0 END), 0),
                2
            ) AS shallow_deep_ratio
        FROM earth_data
        WHERE place IS NOT NULL
        GROUP BY place
        HAVING deep_count > 0
        ORDER BY shallow_deep_ratio DESC
        LIMIT 10;
    """,
    "27. Average Magnitude Difference: Tsunami vs Non-Tsunami": """
        SELECT
            ROUND(AVG(CASE WHEN tsunami = 1 THEN mag END), 4) AS avg_tsunami_magnitude,
            ROUND(AVG(CASE WHEN tsunami = 0 THEN mag END), 4) AS avg_non_tsunami_magnitude,
            ROUND(
                AVG(CASE WHEN tsunami = 1 THEN mag END) -
                AVG(CASE WHEN tsunami = 0 THEN mag END),
                4
            ) AS magnitude_difference
        FROM earth_data
        WHERE mag IS NOT NULL;
    """,
    "28. Top 10 Lowest Data Reliability Events (Highest RMS + Gap)": """
        SELECT
            id,
            time,
            place,
            mag,
            rms,
            gap,
            ROUND((rms + gap), 2) AS error_score
        FROM earth_data
        WHERE rms IS NOT NULL AND gap IS NOT NULL
        ORDER BY error_score DESC
        LIMIT 10;
    """,
    "30. Top 10 Regions with Highest Frequency of Deep-Focus Earthquakes (>300 km)": """
        SELECT
            place,
            COUNT(*) AS deep_earthquake_count,
            ROUND(AVG(depth_km), 2) AS average_depth
        FROM earth_data
        WHERE depth_km > 300 AND place IS NOT NULL
        GROUP BY place
        ORDER BY deep_earthquake_count DESC
        LIMIT 10;
    """,
}

task = st.selectbox("Choose Task Number", list(queries.keys()))

with st.expander("View SQL Query"):
  st.code(queries[task].strip(), language="sql")

if st.button("Run Query", type="primary"):
  try:
    df = pd.read_sql(queries[task], engine)
    st.subheader(f"Results for: {task}")

    col1, col2 = st.columns([1.3, 1])

    with col1:
      st.dataframe(df, use_container_width=True)

    with col2:
      if len(df) > 1 and len(df.columns) >= 2:
        x_col = df.columns[0]
        numeric_cols = df.select_dtypes(include="number").columns.tolist()
        y_cols = [c for c in numeric_cols if c != x_col]

        if y_cols:
          y_col = y_cols[0]
          if "hour" in x_col or "year" in x_col:
            fig = px.line(
                df,
                x=x_col,
                y=y_col,
                markers=True,
                title=f"{y_col} by {x_col}",
            )
          else:
            fig = px.bar(
                df.head(15), x=x_col, y=y_col, title=f"{y_col} by {x_col}"
            )
          st.plotly_chart(fig, use_container_width=True)
      elif "latitude" in df.columns and "longitude" in df.columns:
        st.map(df[["latitude", "longitude"]].dropna())

  except Exception as e:
    st.error(f"Database query error: {e}")