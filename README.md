# UK House Prices Dashboard

An interactive dashboard for exploring UK house prices from 1995 onwards, built with Python, SQLite, Streamlit and Plotly.

## What it does

- **Geography level selector** – switch between countries, regions and local authorities. Every chart and ranking compares like with like, so a whole region is never ranked next to a single borough.
- **Compare two areas** – pick any two areas and a year range to see their average prices side by side, with hover tooltips.
- **Key figures** – first, current, highest and average price, growth since the start and growth over the last 12 months.
- **Rankings** – the most expensive and fastest-growing areas for the chosen level and years.

## Tech stack

- Python
- Pandas
- SQLite
- Streamlit
- Plotly

## Data

The data is the **UK House Price Index (UK HPI)**, published by HM Land Registry together with the ONS, Registers of Scotland and Land & Property Services Northern Ireland. It covers 405 areas from 1995 to February 2023, with about 132,000 monthly records.

Prices are average prices **before inflation**, so growth figures are nominal and not adjusted to today's money.

### Geography levels

Each row in the raw data has an ONS area code. The first three characters show what kind of place it is, and `data_cleaning.py` uses that prefix to add a `GeographyLevel` column:

| GeographyLevel | Examples |
|---|---|
| `UK_Aggregate` | United Kingdom, Great Britain |
| `Country` | England, Scotland, Wales, Northern Ireland |
| `Region` | London, North West, South East |
| `LocalAuthority` | Barnet, Aberdeenshire, Belfast |

## Project structure

```
app.py                  Streamlit dashboard
requirements.txt        Python dependencies
src/
  data_cleaning.py      raw CSV -> cleaned CSV (adds GeographyLevel)
  database.py           cleaned CSV -> SQLite database
  analysis.py           early query helpers
data/                   NOT in git - generated locally (see below)
  raw/uk_hpi.csv
  cleaned/house_prices_clean.csv
  house_prices.db
```

## How to run

The `data/` folder is not stored in the repository, because every file in it can be rebuilt from the raw download. After cloning, you need to create it:

1. **Install the dependencies** (a virtual environment is recommended):

   ```
   python -m pip install -r requirements.txt
   ```

2. **Create the data folders:**

   ```
   mkdir data\raw
   mkdir data\cleaned
   ```

3. **Download the raw data.** From [UK House Price Index: data downloads February 2023](https://www.gov.uk/government/statistical-data-sets/uk-house-price-index-data-downloads-february-2023), download the full CSV file and save it as `data/raw/uk_hpi.csv`. This is the release that ends in February 2023, which is what the dashboard was built on. Newer monthly releases exist, but their layout may differ, so check the column names before using them.

4. **Run the pipeline, in order:**

   ```
   python src/data_cleaning.py
   python src/database.py
   ```

   The first command should print the number of rows per geography level. The second should end with `(132006, 10)`.

5. **Start the dashboard:**

   ```
   python -m streamlit run app.py
   ```

   It opens in your browser at `http://localhost:8501`.

## Current status

### Done

- Data cleaning and date filtering (1995 onwards)
- Geography classification from ONS area codes
- SQLite database with parameterised SQL queries
- Interactive dashboard with a geography level selector
- Plotly charts for price comparison and rankings

### Ideas for next steps

- Property-type comparison (detached, semi-detached, terraced, flats)
- Sales volume trends
- Inflation-adjusted prices
- Deploying the dashboard online