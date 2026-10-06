import streamlit as st
import pandas as pd
import mysql.connector
import plotly.express as px

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="Earthquake Data Analysis",
    page_icon="🌍",
    layout="wide"
)

st.title("🌍 Earthquake Data Analysis Dashboard")
st.write("Interactive Earthquake Data Analysis using Python, MySQL and Streamlit")

# =========================================================
# MYSQL CONNECTION
# =========================================================
@st.cache_resource
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="YOUR_PASSWORD",
        database="YOUR_DATABASE"
    )


try:
    connection = get_connection()
except Exception as e:
    st.error(f"Database connection failed: {e}")
    st.stop()


# =========================================================
# LOAD DATA
# =========================================================
@st.cache_data
def load_data():

    query = "SELECT * FROM earth_data"

    data = pd.read_sql(query, connection)

    return data


try:
    df = load_data()
except Exception as e:
    st.error(f"Error loading earthquake data: {e}")
    st.stop()


# =========================================================
# CLEAN COLUMN NAMES
# =========================================================
df.columns = df.columns.str.strip()


# Convert time column
if "time" in df.columns:
    df["time"] = pd.to_datetime(
        df["time"],
        errors="coerce"
    )


# =========================================================
# SIDEBAR
# =========================================================
st.sidebar.header("🔎 Filters")


# Magnitude filter
if "mag" in df.columns:

    valid_mag = df["mag"].dropna()

    if len(valid_mag) > 0:

        min_mag = float(valid_mag.min())
        max_mag = float(valid_mag.max())

        magnitude_range = st.sidebar.slider(
            "Magnitude Range",
            min_value=min_mag,
            max_value=max_mag,
            value=(min_mag, max_mag)
        )

        df = df[
            (df["mag"] >= magnitude_range[0]) &
            (df["mag"] <= magnitude_range[1])
        ]


# Alert filter
if "alert" in df.columns:

    alert_values = (
        df["alert"]
        .dropna()
        .unique()
        .tolist()
    )

    if alert_values:

        selected_alerts = st.sidebar.multiselect(
            "Alert Level",
            options=alert_values,
            default=alert_values
        )

        if selected_alerts:
            df = df[
                df["alert"].isin(selected_alerts)
            ]


# =========================================================
# KEY STATISTICS
# =========================================================
st.subheader("📊 Key Statistics")

col1, col2, col3, col4 = st.columns(4)


# Total earthquakes
with col1:

    st.metric(
        "Total Earthquakes",
        f"{len(df):,}"
    )


# Average magnitude
with col2:

    if "mag" in df.columns:

        average_mag = df["mag"].mean()

        st.metric(
            "Average Magnitude",
            f"{average_mag:.2f}"
        )

    else:
        st.metric("Average Magnitude", "N/A")


# Maximum magnitude
with col3:

    if "mag" in df.columns:

        maximum_mag = df["mag"].max()

        st.metric(
            "Maximum Magnitude",
            f"{maximum_mag:.2f}"
        )

    else:
        st.metric("Maximum Magnitude", "N/A")


# Average depth
with col4:

    if "depth_km" in df.columns:

        average_depth = df["depth_km"].mean()

        st.metric(
            "Average Depth",
            f"{average_depth:.2f} km"
        )

    else:
        st.metric("Average Depth", "N/A")


st.divider()


# =========================================================
# MAGNITUDE DISTRIBUTION
# =========================================================
if "mag" in df.columns:

    st.subheader("📈 Magnitude Distribution")

    fig = px.histogram(
        df,
        x="mag",
        nbins=30,
        title="Earthquake Magnitude Distribution"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# =========================================================
# DEPTH DISTRIBUTION
# =========================================================
if "depth_km" in df.columns:

    st.subheader("🌊 Depth Distribution")

    fig = px.histogram(
        df,
        x="depth_km",
        nbins=30,
        title="Earthquake Depth Distribution"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# =========================================================
# ALERT LEVEL ANALYSIS
# =========================================================
if "alert" in df.columns:

    st.subheader("🚨 Earthquakes by Alert Level")

    alert_data = (
        df["alert"]
        .dropna()
        .value_counts()
        .reset_index()
    )

    alert_data.columns = [
        "alert",
        "count"
    ]

    fig = px.bar(
        alert_data,
        x="alert",
        y="count",
        text="count",
        title="Earthquake Count by Alert Level"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# =========================================================
# EARTHQUAKE TYPE
# =========================================================
if "type" in df.columns:

    st.subheader("🌋 Earthquake Type Analysis")

    type_data = (
        df["type"]
        .dropna()
        .value_counts()
        .reset_index()
    )

    type_data.columns = [
        "type",
        "count"
    ]

    fig = px.bar(
        type_data,
        x="type",
        y="count",
        text="count",
        title="Earthquake Count by Type"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# =========================================================
# TSUNAMI ANALYSIS
# =========================================================
if "tsunami" in df.columns:

    st.subheader("🌊 Tsunami Analysis")

    tsunami_data = (
        df["tsunami"]
        .dropna()
        .value_counts()
        .reset_index()
    )

    tsunami_data.columns = [
        "tsunami",
        "count"
    ]

    tsunami_data["tsunami"] = tsunami_data[
        "tsunami"
    ].map({
        0: "No Tsunami",
        1: "Tsunami"
    }).fillna("Unknown")

    fig = px.pie(
        tsunami_data,
        names="tsunami",
        values="count",
        title="Tsunami vs Non-Tsunami Earthquakes"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# =========================================================
# YEARLY EARTHQUAKE TREND
# =========================================================
if "time" in df.columns:

    yearly_data = (
        df.dropna(subset=["time"])
        .groupby(df["time"].dt.year)
        .size()
        .reset_index(name="count")
    )

    yearly_data.columns = [
        "year",
        "count"
    ]

    if len(yearly_data) > 0:

        st.subheader("📅 Yearly Earthquake Trend")

        fig = px.line(
            yearly_data,
            x="year",
            y="count",
            markers=True,
            title="Number of Earthquakes per Year"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


# =========================================================
# MAGNITUDE VS DEPTH
# =========================================================
if (
    "mag" in df.columns
    and "depth_km" in df.columns
):

    st.subheader("📍 Magnitude vs Depth")

    scatter_data = df.dropna(
        subset=[
            "mag",
            "depth_km"
        ]
    )

    hover_columns = []

    if "place" in df.columns:
        hover_columns.append("place")

    fig = px.scatter(
        scatter_data,
        x="depth_km",
        y="mag",
        hover_data=hover_columns,
        title="Earthquake Magnitude vs Depth"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# =========================================================
# TOP 5 PLACES
# =========================================================
if (
    "place" in df.columns
    and "mag" in df.columns
):

    st.subheader("🏆 Top 5 Places by Average Magnitude")

    top_places = (
        df.dropna(
            subset=[
                "place",
                "mag"
            ]
        )
        .groupby("place")["mag"]
        .mean()
        .sort_values(
            ascending=False
        )
        .head(5)
        .reset_index()
    )

    top_places.columns = [
        "place",
        "average_magnitude"
    ]

    st.dataframe(
        top_places,
        use_container_width=True
    )


# =========================================================
# CASUALTIES
# =========================================================
if (
    "casualties" in df.columns
    and "place" in df.columns
):

    st.subheader("🚑 Casualties Analysis")

    casualty_data = (
        df.dropna(
            subset=[
                "place",
                "casualties"
            ]
        )
        .groupby("place")["casualties"]
        .sum()
        .sort_values(
            ascending=False
        )
        .head(5)
        .reset_index()
    )

    casualty_data.columns = [
        "place",
        "total_casualties"
    ]

    fig = px.bar(
        casualty_data,
        x="place",
        y="total_casualties",
        text="total_casualties",
        title="Top 5 Places with Highest Casualties"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# =========================================================
# ECONOMIC LOSS
# =========================================================
if "economic_loss" in df.columns:

    st.subheader("💰 Economic Loss Analysis")

    if "continent" in df.columns:

        economic_data = (
            df.dropna(
                subset=[
                    "continent",
                    "economic_loss"
                ]
            )
            .groupby("continent")["economic_loss"]
            .sum()
            .sort_values(
                ascending=False
            )
            .reset_index()
        )

        if len(economic_data) > 0:

            fig = px.bar(
                economic_data,
                x="continent",
                y="economic_loss",
                text="economic_loss",
                title="Total Estimated Economic Loss by Continent"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        else:

            st.info(
                "No economic-loss data is available."
            )

    else:

        st.warning(
            "The 'continent' column is not available "
            "in your earth_data table."
        )


# =========================================================
# COMPLETE DATA
# =========================================================
st.subheader("📋 Earthquake Data")

st.dataframe(
    df,
    use_container_width=True,
    height=450
)


# =========================================================
# DATABASE COLUMNS
# =========================================================
with st.expander("🔧 Available Database Columns"):

    st.write(
        "These are the columns currently available "
        "in your earth_data table:"
    )

    st.write(
        list(df.columns)
    )


# =========================================================
# FOOTER
# =========================================================
st.divider()

st.caption(
    "Earthquake Data Analysis Project | "
    "Python • MySQL • Pandas • Streamlit • Plotly"
)