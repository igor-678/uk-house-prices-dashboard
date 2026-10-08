import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(
    page_title="UK House Prices",
    layout="wide"
)


BASE_DIR = Path(__file__).resolve().parent
db_file = BASE_DIR / "data" / "house_prices.db"


def get_regions(level):
    conn = sqlite3.connect(db_file)

    query = """
        SELECT DISTINCT RegionName
        FROM house_prices
        WHERE GeographyLevel = ?
        ORDER BY RegionName
    """

    regions = pd.read_sql_query(query, conn, params=(level,))

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

def get_top_expensive_regions(end_year, level):
    conn = sqlite3.connect(db_file)

    start_date = f"{end_year}-01-01"
    next_year_date = f"{end_year + 1}-01-01"

    query = """
           WITH ranked_prices AS (
               SELECT
                   RegionName,
                   AveragePrice,
                   Date,
                   ROW_NUMBER() OVER (
                       PARTITION BY RegionName
                       ORDER BY Date DESC
                   ) AS row_number
               FROM house_prices
               WHERE Date >= ?
                 AND Date < ?
                 AND GeographyLevel = ?
           )
           SELECT
               RegionName,
               AveragePrice,
               Date
           FROM ranked_prices
           WHERE row_number = 1
           ORDER BY AveragePrice DESC
           LIMIT 10
       """

    top_regions = pd.read_sql_query(
        query,
        conn,
        params=(start_date, next_year_date, level)
    )

    conn.close()

    return top_regions


def get_top_growth_regions(start_year, end_year, level):
    conn = sqlite3.connect(db_file)
    query = """
        SELECT
            RegionName,
            Date,
            AveragePrice
        FROM house_prices
        WHERE strftime('%Y', Date) IN (?, ?)
          AND GeographyLevel = ?
        ORDER BY RegionName, Date
    """

    data = pd.read_sql_query(
        query,
        conn,
        params=(str(start_year), str(end_year), level)
    )

    conn.close()

    data["Date"] = pd.to_datetime(data["Date"])

    start_prices = data[
        data["Date"].dt.year == start_year
    ].groupby("RegionName").first()


    end_prices = data[
        data["Date"].dt.year == end_year
    ].groupby("RegionName").last()

    growth_data = start_prices[
        ["AveragePrice"]
    ].join(
        end_prices[["AveragePrice"]],
        lsuffix="_Start",
        rsuffix="_End"
    )

    growth_data["GrowthPercent"] = (
        (
            growth_data["AveragePrice_End"]
            - growth_data["AveragePrice_Start"]
        )
        / growth_data["AveragePrice_Start"]
    ) * 100

    growth_data = growth_data.sort_values(
        "GrowthPercent",
        ascending=False
    ).head(10)

    return growth_data



def make_ranking_chart(data, value_column, label_column,
                       axis_title, tick_prefix="", tick_suffix="",
                       decimals=0):
    """Horizontal bar chart for a 'top 10' style ranking.

    Horizontal bars are used because area names like
    "Kensington and Chelsea" are long and would be cut off or
    rotated on a vertical chart. The data is already sorted from
    highest to lowest, so we reverse the y axis to put the highest
    bar at the top.
    """
    fig = px.bar(
        data,
        x=value_column,
        y=label_column,
        orientation="h"
    )

    fig.update_yaxes(autorange="reversed", title=None)

    fig.update_xaxes(
        title=axis_title,
        tickprefix=tick_prefix,
        ticksuffix=tick_suffix
    )

    # What the user sees when hovering over a bar
    fig.update_traces(
        hovertemplate=(
            f"%{{y}}<br>{tick_prefix}%{{x:,.{decimals}f}}{tick_suffix}"
            "<extra></extra>"
        )
    )

    fig.update_layout(
        height=400,
        margin=dict(l=0, r=0, t=10, b=0)
    )

    return fig


st.title("UK House Prices Dashboard")

level_labels = {
    "Region": ("Region", "Regions"),
    "Country": ("Country", "Countries"),
    "LocalAuthority": ("Local Authority", "Local Authorities"),
}

selected_level = st.selectbox(
    "Geography level",
    list(level_labels.keys()),
    format_func=lambda level: level_labels[level][0]
)

level_singular, level_plural = level_labels[selected_level]

regions = get_regions(selected_level)

default_index = regions.index("London") if "London" in regions else 0


region_col1, region_col2 = st.columns(2)

with region_col1:
    selected_region = st.selectbox(
        f"Select First {level_singular}",
        regions,
        index=default_index
    )

with region_col2:
    comparison_region = st.selectbox(
        f"Select Second {level_singular}",
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
first_region_data["Area"] = selected_region

second_region_data = comparison_prices[
    ["Date", "AveragePrice"]
].copy()
second_region_data["Area"] = comparison_region

# "Long" format: one row per area per date, with an Area column that
# Plotly uses to draw one line per area and colour them.
if selected_region == comparison_region:
    st.info(
        f"Both selections are {selected_region}. "
        "Pick a different second area to compare."
    )
    chart_data = first_region_data
else:
    chart_data = pd.concat(
        [first_region_data, second_region_data],
        ignore_index=True
    )

price_fig = px.line(
    chart_data,
    x="Date",
    y="AveragePrice",
    color="Area"
)

price_fig.update_traces(hovertemplate="£%{y:,.0f}")

price_fig.update_layout(
    hovermode="x unified",
    xaxis_title=None,
    yaxis_title="Average price",
    yaxis_tickprefix="£",
    yaxis_tickformat=",.0f",
    legend_title_text="",
    legend=dict(orientation="h", y=1.1, x=0),
    margin=dict(l=0, r=0, t=10, b=0)
)

st.plotly_chart(price_fig)


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

st.subheader(f"{selected_region}: {start_year} to {end_year}")

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


top_regions = get_top_expensive_regions(end_year, selected_level)

top_regions_table = top_regions.copy()

top_regions_table["AveragePrice"] = top_regions_table[
    "AveragePrice"
].map(
    lambda price: f"£{price:,.0f}"
)

top_regions_table = top_regions_table.rename(
    columns={
        "RegionName": level_singular,
        "AveragePrice": "Average Price",
    }
)


st.subheader(f"Most Expensive {level_plural} in {end_year}")

st.plotly_chart(
    make_ranking_chart(
        top_regions,
        value_column="AveragePrice",
        label_column="RegionName",
        axis_title="Average price",
        tick_prefix="£"
    )
)


st.dataframe(
    top_regions_table,
    hide_index=True,
    width="stretch"
)


top_growth_regions = get_top_growth_regions(
    start_year,
    end_year,
    selected_level
)

# The region names are the table's index, so reset_index() turns them
# back into a normal column that charts and tables can use.
growth_table = top_growth_regions.reset_index().rename(
    columns={
        "RegionName": level_singular,
        "AveragePrice_Start": f"Price {start_year}",
        "AveragePrice_End": f"Price {end_year}",
        "GrowthPercent": "Growth (%)",
    }
)

st.subheader(
    f"Fastest Growing {level_plural} from {start_year} to {end_year}"
)

st.plotly_chart(
    make_ranking_chart(
        growth_table,
        value_column="Growth (%)",
        label_column=level_singular,
        axis_title="Price growth (before inflation)",
        tick_suffix="%",
        decimals=1
    )
)

st.dataframe(
    growth_table,
    hide_index=True,
    width="stretch",
    column_config={
        f"Price {start_year}": st.column_config.NumberColumn(
            format="£%.0f"
        ),
        f"Price {end_year}": st.column_config.NumberColumn(
            format="£%.0f"
        ),
        "Growth (%)": st.column_config.NumberColumn(
            format="%.1f"
        ),
    }
)



st.write(
    "Interactive dashboard for exploring UK house prices by region."
)