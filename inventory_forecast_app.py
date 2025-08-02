import streamlit as st
import pandas as pd
from supabase import create_client, Client
import os





# --------------------------
# Supabase credentials
# --------------------------
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")



# --------------------------
# Connect to Supabase
# --------------------------
@st.cache_resource
def connect_to_supabase():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase: Client = connect_to_supabase()

# --------------------------
# Load data
# --------------------------
@st.cache_data
def load_forecast_data():
    response = supabase.table("inventory_forecast_metrics").select("*").execute()
    return pd.DataFrame(response.data)

df = load_forecast_data()

# --------------------------
# Streamlit Interface
# --------------------------
st.set_page_config(page_title="Inventory Forecast Dashboard", layout="wide")
st.title("📦 Inventory Forecast Dashboard")

if df.empty:
    st.warning("No data available.")
else:
    # Convert dates
    df["forecast_date"] = pd.to_datetime(df["forecast_date"])

    # Sidebar filters
    with st.sidebar:
        st.header("🔍 Filters")

        # Product ID filter
        product_ids = sorted(df["product_id"].unique())
        selected_product = st.selectbox("Select Product ID", options=product_ids)

        # Date range filter
        min_date, max_date = df["forecast_date"].min(), df["forecast_date"].max()
        start_date, end_date = st.date_input("Select Forecast Date Range", (min_date, max_date))

    # Apply filters
    filtered_df = df[
        (df["product_id"] == selected_product) &
        (df["forecast_date"] >= pd.to_datetime(start_date)) &
        (df["forecast_date"] <= pd.to_datetime(end_date))
    ]

    # Display table
    st.subheader("📋 Forecast Data")
    st.dataframe(filtered_df.sort_values("forecast_date"), use_container_width=True)

    # Plot forecast quantity
    st.subheader("📈 Forecast Quantity Over Time")
    st.line_chart(
        data=filtered_df.set_index("forecast_date")[["forecast_quantity"]],
        use_container_width=True
    )
