import sqlite3
import pandas as pd
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
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

    return regions


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




if __name__ == "__main__":

    london = get_region_prices("London")

    print(london.head())
    print()
    print(london.shape)







