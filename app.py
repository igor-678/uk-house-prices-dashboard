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
        params=(region_name,)
    )

    conn.close()

    return prices


st.title("UK House Prices Dashboard")

regions = get_regions()


region_col1, region_col2 = st.columns(2)

with region_col1:
    selected_region = st.selectbox(
        "Select First Region",
        regions,
        index= regions.index("London")
    )

with region_col2:
    comparison_region = st.selectbox(
        "Select Second Region",
        regions,
        index= 1
    )

prices = get_region_prices(selected_region)
prices["Date"] = pd.to_datetime(prices["Date"])

comparison_prices = get_region_prices(comparison_region)
comparison_prices["Date"] = pd.to_datetime(
    comparison_prices["Date"]
)


years = sorted(prices["Date"].dt.year.unique())

start_year = st.selectbox(
    "Start Year",
    years,
    index=0
)


comparison_prices = comparison_prices[
    comparison_prices["Date"].dt.year >= start_year
]


first_region_data = prices[
    ["Date", "AveragePrice"]
].copy()

first_region_data = first_region_data.rename(
    columns={"AveragePrice": selected_region}
)


second_region_data = comparison_prices[
    ["Date", "AveragePrice"]
].copy()

second_region_data = second_region_data.rename(
    columns={"AveragePrice": comparison_region}
)


chart_data = first_region_data.merge(
    second_region_data,
    on="Date",
    how="inner"
)

st.line_chart(
    chart_data.set_index("Date")
)


current_price = prices["AveragePrice"].iloc[-1]
first_price = prices["AveragePrice"].iloc[0]
highest_price = prices["AveragePrice"].max()
average_price = prices["AveragePrice"].mean()

growth_percent = (
    (current_price - first_price)
    / first_price
) * 100

if len(prices) >= 13:
    price_12_months_ago = prices["AveragePrice"].iloc[-13]

    last_year_growth_percent = (
        (current_price - price_12_months_ago)
        / price_12_months_ago
    ) * 100
else:
    last_year_growth_percent = None

col1, col2, col3, col4, col5, col6 = st.columns(6)

col1.metric(
    "First Price",
    f"£{first_price:,.0f}"
)

col2.metric(
    "Current Price",
    f"£{current_price:,.0f}"
)

col3.metric(
    "Highest Price",
    f"£{highest_price:,.0f}"
)

col4.metric(
    "Growth Since Start",
    f"{growth_percent:.1f}%"
)

if last_year_growth_percent is not None:
    col5.metric(
        "Last 12 Months",
        f"{last_year_growth_percent:.1f}%"
    )
else:
    col5.metric(
        "Last 12 Months",
        "Not enough data"
    )

col6.metric(
    "Average Price",
    f"£{average_price:,.0f}"
)

st.write(
    "Interactive dashboard for exploring UK house prices by region."
)


