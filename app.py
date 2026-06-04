import streamlit as st
import sqlite3
import pandas as pd
from pathlib import Path


st.set_page_config(
    page_title="UK House Prices",
    layout="wide"
)


BASE_DIR = Path(__file__).resolve().parent

db_file = BASE_DIR / "data" / "house_prices.db"



def get_regions():

    conn = sqlite3.connect(db_file)

    query = """
        SELECT DISTINCT RegionName
        FROM house_prices
        ORDER BY RegionName
    """

    regions = pd.read_sql_query(query, conn)

    conn.close()
    return regions["RegionName"].tolist()



def get_region_prices(region_name):

    conn = sqlite3.connect(db_file)

    query = """
        SELECT
            Date,
            AveragePrice
        FROM house_prices
        WHERE RegionName = ?
        ORDER BY Date
    """

    prices = pd.read_sql_query(
        query,
        conn,
    params=(region_name, )
    )

    conn.close()
    return prices



st.title("UK House Prices Dashboard")

regions = get_regions()

selected_region = st.selectbox(
    "Select Region",
        regions
)


prices = get_region_prices(selected_region)

prices["Date"] = pd.to_datetime(prices["Date"])

st.line_chart(
    prices.set_index("Date") ["AveragePrice"])



current_price = prices["AveragePrice"].iloc[-1]
first_price = prices["AveragePrice"].iloc[0]
highest_price = prices["AveragePrice"].max()

growth_percent = (
    (current_price - first_price) / first_price) * 100



col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "first price",
    f"£{first_price:,.0f}",
)

col2.metric(
    "current price",
    f"£{current_price:,.0f}",
)

col3.metric(
    "highest price",
    f"£{highest_price:,.0f}",
)

col4.metric(
    "Growth Since Start",
    f"{growth_percent:.1f}%",
)



st.write("Interactive Dashboard for exploring UK House Prices by region.")




