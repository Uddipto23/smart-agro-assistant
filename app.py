import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import re
import os

# ------------------------
# 1. App Title & Sidebar
# ------------------------
st.set_page_config(page_title="Smart Agro Assistant Dashboard", layout="wide")
st.title("🌾 Smart Agro Assistant Dashboard")
st.sidebar.title("📊 Navigation")
section = st.sidebar.radio("Go to:", ["Land Use", "Temperature", "Emissions", "Crops", "Livestock"])

# ------------------------
# 2. Dataset Loader
# ------------------------
def safe_read_csv(file_path):
    for delim in [",", ";", "\t"]:
        try:
            df = pd.read_csv(file_path, delimiter=delim)
            if df.shape[1] > 1:
                return df
        except:
            continue
    return None

# Adjust this path if running locally
dataset_path = "Dataset"

landuse = safe_read_csv(os.path.join(dataset_path, "Faostat Landuse Data (2000-2023).csv"))
temp = safe_read_csv(os.path.join(dataset_path, "Faostat Temperature Change on Land (2000-2023).csv"))
emissions = safe_read_csv(os.path.join(dataset_path, "Faostat Emissions Total (2000-2022).csv"))
crops = safe_read_csv(os.path.join(dataset_path, "Faostat Corps and Livstock (2000-2023).csv"))

# ------------------------
# 3. Melt + Clean Function
# ------------------------
def melt_and_clean_data(df, id_vars, value_name='Value'):
    if df is None:
        return None
    year_cols = [col for col in df.columns if re.match(r'Y\d{4}', col)]
    if not year_cols:
        return None
    df_melted = df.melt(id_vars=id_vars, value_vars=year_cols, var_name='Year_Col', value_name=value_name)
    df_melted['Year'] = df_melted['Year_Col'].str.extract(r'Y(\d{4})').astype(int)
    df_melted['Value'] = pd.to_numeric(df_melted['Value'], errors='coerce')
    return df_melted

# Melt data
landuse_melted = melt_and_clean_data(landuse, id_vars=['Area Code', 'Area Code (M49)', 'Area', 'Item Code', 'Item', 'Element Code', 'Element', 'Unit'])
temp_melted = melt_and_clean_data(temp, id_vars=['Area Code', 'Area Code (M49)', 'Area', 'Months Code', 'Months', 'Element Code', 'Element', 'Unit'])
emissions_melted = melt_and_clean_data(emissions, id_vars=['Area Code', 'Area Code (M49)', 'Area', 'Item Code', 'Item', 'Element Code', 'Element', 'Source Code', 'Source', 'Unit'])
crops_melted = melt_and_clean_data(crops, id_vars=['Area Code', 'Area Code (M49)', 'Area', 'Item Code', 'Item Code (CPC)', 'Item', 'Element Code', 'Element', 'Unit'])

# ------------------------
# 4. Section: Land Use
# ------------------------
if section == "Land Use":
    st.subheader("🌱 Land Use Trends")
    if landuse_melted is not None:
        fig, ax = plt.subplots(figsize=(8,5))
        landuse_melted.groupby("Year")["Value"].sum().plot(kind="line", marker="o", ax=ax)
        ax.set_title("Land Use (2000–2023)")
        ax.set_xlabel("Year")
        ax.set_ylabel("Total Landuse")
        st.pyplot(fig)
    else:
        st.warning("Landuse dataset not available.")

# ------------------------
# 5. Section: Temperature
# ------------------------
elif section == "Temperature":
    st.subheader("🌡️ Temperature Change on Land")
    if temp_melted is not None:
        fig, ax = plt.subplots(figsize=(8,5))
        temp_melted.groupby("Year")["Value"].mean().plot(kind="line", color="orange", marker="o", ax=ax)
        ax.set_title("Temperature Change (2000–2023)")
        ax.set_xlabel("Year")
        ax.set_ylabel("Avg Temperature Change (°C)")
        st.pyplot(fig)
    else:
        st.warning("Temperature dataset not available.")

# ------------------------
# 6. Section: Emissions
# ------------------------
elif section == "Emissions":
    st.subheader("💨 Emissions Over Time")
    if emissions_melted is not None:
        fig, ax = plt.subplots(figsize=(8,5))
        emissions_melted.groupby("Year")["Value"].sum().plot(kind="bar", ax=ax)
        ax.set_title("Total Emissions (2000–2022)")
        ax.set_xlabel("Year")
        ax.set_ylabel("Emissions")
        st.pyplot(fig)
    else:
        st.warning("Emissions dataset not available.")

# ------------------------
# 7. Section: Crops
# ------------------------
elif section == "Crops":
    st.subheader("🌾 Top Crops by Production")
    if crops_melted is not None:
        top_crops = crops_melted.groupby("Item")["Value"].sum().sort_values(ascending=False).head(10)
        fig, ax = plt.subplots(figsize=(8,5))
        top_crops.plot(kind="bar", ax=ax)
        ax.set_title("Top 10 Crops")
        ax.set_xlabel("Crop")
        ax.set_ylabel("Production")
        st.pyplot(fig)
    else:
        st.warning("Crops dataset not available.")

# ------------------------
# 8. Section: Livestock
# ------------------------
elif section == "Livestock":
    st.subheader("🐄 Livestock Trends")
    if crops_melted is not None:
        livestock_items = crops_melted[crops_melted['Item'].str.contains(
            "cattle|goat|sheep|pig|buffalo|chicken|poultry|milk|meat|egg", case=False, na=False
        )]
        top_livestock = livestock_items.groupby("Item")["Value"].sum().sort_values(ascending=False).head(10)
        fig, ax = plt.subplots(figsize=(8,5))
        top_livestock.plot(kind="bar", color="green", ax=ax)
        ax.set_title("Top 10 Livestock Products")
        ax.set_xlabel("Livestock")
        ax.set_ylabel("Production")
        st.pyplot(fig)
    else:
        st.warning("Livestock dataset not available.")
