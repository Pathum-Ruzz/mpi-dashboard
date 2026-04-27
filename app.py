import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt


# Page Setup

st.set_page_config(page_title="Global MPI Dashboard", layout="wide")


# Load the Dataset

@st.cache_data
def load_data():
    df = pd.read_csv("global_mpi.csv")

    numeric_cols = [
        "MPI",
        "Headcount Ratio",
        "Intensity of Deprivation",
        "Vulnerable to Poverty",
        "In Severe Poverty"
    ]

    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["Country ISO3"] = df["Country ISO3"].astype(str)
    df["Admin 1 Name"] = df["Admin 1 Name"].astype(str)

    return df

df = load_data()


# add Title

st.title("Global Multidimensional Poverty Index Dashboard")

st.write(
    "This dashboard explores multidimensional poverty using the Global MPI dataset. "
    "Users can analyse poverty indicators by country, region, and MPI range."
)


# Sidebar Filters

st.sidebar.header("Dashboard Filters")

countries = sorted(df["Country ISO3"].dropna().unique())
selected_country = st.sidebar.selectbox("Select Country", countries)

min_mpi = float(df["MPI"].min())
max_mpi = float(df["MPI"].max())

mpi_range = st.sidebar.slider(
    "Select MPI Range",
    min_value=min_mpi,
    max_value=max_mpi,
    value=(min_mpi, max_mpi)
)

country_df = df[
    (df["Country ISO3"] == selected_country) &
    (df["MPI"] >= mpi_range[0]) &
    (df["MPI"] <= mpi_range[1])
].copy()

country_df = country_df[
    country_df["Admin 1 Name"].notna() &
    (country_df["Admin 1 Name"].astype(str).str.lower() != "nan")
]

regions = sorted(country_df["Admin 1 Name"].dropna().unique())

if len(regions) == 0:
    st.warning("No data available for the selected filters.")
    st.stop()

selected_region = st.sidebar.selectbox("Select Region", regions)
filtered_df = country_df[country_df["Admin 1 Name"] == selected_region]


# Country Level Overview

st.subheader("Country-Level Overview")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Average Country MPI", round(country_df["MPI"].mean(), 3))

with col2:
    st.metric("Average Headcount Ratio", round(country_df["Headcount Ratio"].mean(), 1))

with col3:
    st.metric("Average Severe Poverty", round(country_df["In Severe Poverty"].mean(), 1))


# Selected Region Overview

st.subheader("Selected Region Overview")

mpi_value = filtered_df["MPI"].values[0]
headcount_value = filtered_df["Headcount Ratio"].values[0]
severe_value = filtered_df["In Severe Poverty"].values[0]

col4, col5, col6, col7 = st.columns(4)

with col4:
    st.metric("Country", selected_country)

with col5:
    st.metric("Selected Region MPI", round(mpi_value, 3))

with col6:
    st.metric("Headcount Ratio", round(headcount_value, 1))

with col7:
    st.metric("Severe Poverty", round(severe_value, 1))


# Data View

with st.expander("View Selected Region Data"):
    st.dataframe(filtered_df)

# Create charts

# Chart 1: Top 10 Regions by MPI

st.subheader("Top 10 Most Deprived Regions Based on MPI")

top_regions = country_df.dropna(subset=["MPI"]).copy()
top_regions = top_regions.sort_values(by="MPI", ascending=False).head(10)

fig1, ax1 = plt.subplots(figsize=(10, 6))
ax1.barh(top_regions["Admin 1 Name"].tolist(), top_regions["MPI"].tolist())
ax1.set_xlabel("MPI")
ax1.set_ylabel("Region")
ax1.set_title(f"Top 10 Regions by MPI in {selected_country}")
ax1.invert_yaxis()
st.pyplot(fig1)

# Chart 2: Poverty Indicators Bar Chart

st.subheader("Comparison of Key Poverty Indicators in Selected Region")

indicators = [
    "Headcount Ratio",
    "Intensity of Deprivation",
    "Vulnerable to Poverty",
    "In Severe Poverty"
]

selected_values = filtered_df[indicators].iloc[0].astype(float)

fig2, ax2 = plt.subplots(figsize=(10, 6))
ax2.bar(indicators, selected_values)
ax2.set_ylabel("Value")
ax2.set_title(f"Poverty Indicators in {selected_region}")
ax2.tick_params(axis="x", rotation=30)

for i, v in enumerate(selected_values):
    ax2.text(i, v + 1, f"{round(v, 1)}", ha="center")

st.pyplot(fig2)

# Chart 3: Scatter Plot

st.subheader("Relationship Between Headcount Ratio and MPI")

fig3, ax3 = plt.subplots(figsize=(10, 6))
ax3.scatter(
    country_df["Headcount Ratio"].astype(float),
    country_df["MPI"].astype(float),
    alpha=0.6
)
ax3.set_xlabel("Headcount Ratio")
ax3.set_ylabel("MPI")
ax3.set_title(f"Headcount Ratio vs MPI in {selected_country}")
st.pyplot(fig3)

# Chart 4: Histogram

st.subheader("Distribution of MPI Values")

fig4, ax4 = plt.subplots(figsize=(10, 6))
ax4.hist(country_df["MPI"].dropna(), bins=15)
ax4.set_xlabel("MPI")
ax4.set_ylabel("Number of Regions")
ax4.set_title(f"Distribution of MPI Values in {selected_country}")
st.pyplot(fig4)

# Chart 5: Pie Chart

st.subheader("Share of Poverty Indicators in Selected Region")

pie_values = selected_values[selected_values > 0]

fig5, ax5 = plt.subplots(figsize=(8, 8))
ax5.pie(
    pie_values,
    labels=pie_values.index,
    autopct="%1.1f%%",
    startangle=90
)
ax5.set_title(f"Poverty Indicator Share in {selected_region}")
st.pyplot(fig5)

# Key Insights

st.subheader("Key Insights")

st.write(f"""
- The selected country is **{selected_country}**.
- The selected region is **{selected_region}**, with an MPI value of **{round(mpi_value, 3)}**.
- The Top 10 chart identifies the most deprived regions within the selected country.
- The bar chart compares key poverty indicators for the selected region.
- The scatter plot shows the relationship between Headcount Ratio and MPI.
- The histogram shows how MPI values are distributed across regions in the selected country.
- The pie chart provides a visual summary of poverty indicator proportions for the selected region.
""")