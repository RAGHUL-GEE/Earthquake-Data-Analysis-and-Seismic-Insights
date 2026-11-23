import pandas as pd
import streamlit as st
from sqlalchemy import create_engine

st.set_page_config(page_title="Global Seismic Trends", page_icon="🌍", layout="wide")
st.title("🌍 Global Seismic Trends Dashboard")


sample_df = pd.DataFrame({
    "place": ["120km E of Miyako, Japan", "45km W of Ovalle, Chile", "80km S of Adak, Alaska", "15km N of Hualien, Taiwan", "90km SE of Sarangani, Philippines"],
    "country": ["Japan", "Chile", "Alaska", "Taiwan", "Philippines"],
    "mag": [7.8, 6.9, 6.2, 7.1, 6.5],
    "depth_km": [35.0, 110.5, 42.0, 22.4, 340.0],
    "tsunami": [1, 0, 0, 1, 0],
    "latitude": [39.6, -30.6, 51.1, 24.1, 4.8],
    "longitude": [143.4, -71.7, -176.6, 121.6, 126.1],
})


use_mysql = st.sidebar.checkbox("Connect to MySQL Database")
if use_mysql:
    db_url = st.sidebar.text_input("MySQL URL", "mysql+pymysql://root:password@localhost:3306/earthquake_db")
    try:
        df = pd.read_sql("SELECT * FROM earthquakes LIMIT 5000;", create_engine(db_url))
    except Exception as e:
        st.sidebar.error(f"Using sample data ({e})")
        df = sample_df
else:
    df = sample_df

min_mag = st.sidebar.slider("Minimum Magnitude", 0.0, 9.0, 5.0, 0.1)
filtered = df[df["mag"] >= min_mag]


c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Quakes", len(filtered))
c2.metric("Max Magnitude", f"{filtered['mag'].max():.1f}" if not filtered.empty else "0")
c3.metric("Avg Depth (km)", f"{filtered['depth_km'].mean():.1f}" if not filtered.empty else "0")
c4.metric("Tsunami Alerts", int(filtered["tsunami"].sum()) if "tsunami" in filtered else 0)


col1, col2 = st.columns(2)
with col1:
    st.subheader("🗺️ Epicenter Map")
    st.map(filtered[["latitude", "longitude"]].dropna())
with col2:
    st.subheader("📊 Magnitude by Location")
    st.bar_chart(filtered.set_index("place")["mag"])


st.subheader("📋 Earthquake Records")
st.dataframe(filtered, use_container_width=True, hide_index=True)