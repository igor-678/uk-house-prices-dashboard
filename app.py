from zoneinfo import available_timezones

import streamlit as st
import sqlite3
import pandas as pd
from pathlib import Path

from streamlit import query_params, columns

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

def get_top_expensive_regions(end_year):
    conn = sqlite3.connect(db_file)

    query = """
            SELECT
                RegionName,
                AveragePrice,
                Date
            FROM house_prices
            WHERE strftime('%Y', Date) = ?
            AND Date = (
                SELECT MAX(hp2.Date)
                FROM house_prices AS hp2
                WHERE hp2.RegionName = house_prices.RegionName
                AND strftime('%Y', hp2.Date) = ?
            )
            ORDER BY AveragePrice DESC
            LIMIT 10
        """

    top_regions = pd.read_sql_query(
        query,
        conn,
        params=(str(end_year),str(end_year))
    )

    conn.close()

    return top_regions


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

year_col1, year_col2 = st.columns(2)

with year_col1:
      start_year = st.selectbox(
        "Start Year",
        years,
        index= 0
    )

available_end_years = [
    year for year in years
    if year >= start_year
]

with year_col2:
    end_year = st.selectbox(
        "End Year",
        available_end_years,
        index=len(available_end_years) -1
    )


if start_year > end_year:
    st.error("Start Year must be smaller than End Year.")
    st.stop()


prices = prices[
    (prices["Date"].dt.year >= start_year)
    & (prices["Date"].dt.year <= end_year)
]

comparison_prices = comparison_prices[
    (comparison_prices["Date"].dt.year >= start_year)
    & (comparison_prices["Date"].dt.year <= end_year)
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


top_regions = get_top_expensive_regions(end_year)

top_regions = top_regions.copy()

top_regions["AveragePrice"] = top_regions["AveragePrice"].map(
    lambda price: f"£{price:,.0f}"
)

top_regions = top_regions.rename(
    columns={
        "RegionName": "Region",
        "AveragePrice": "AveragePrice",
        "Date": "Date"
    }
)

st.subheader(f"Top 10 Most Expensive Regions in {end_year}")

st.dataframe(
    top_regions,
    hide_index=True,
    use_container_width=True
)



st.write(
    "Interactive dashboard for exploring UK house prices by region."
)


