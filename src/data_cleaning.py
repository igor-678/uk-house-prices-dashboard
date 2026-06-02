import pandas as pd
from pathlib import Path


def clean_data():

    BASE_DIR = Path(__file__).resolve().parent.parent

    raw_file = BASE_DIR / "data" / "raw" / "uk_hpi.csv"
    clean_file = BASE_DIR / "data" / "cleaned" / "house_prices_clean.csv"

    df = pd.read_csv(raw_file)

    df['Date'] = pd.to_datetime(
        df['Date'],
        dayfirst = True,
        errors = 'coerce'
)

    df = df[df['Date'] >= '1995-01-01']

    columns = [
        'Date',
        'RegionName',
        'AveragePrice',
        "SalesVolume",
        "DetachedPrice",
        "SemiDetachedPrice",
        "TerracedPrice",
        "FlatPrice"
    ]

    clean_df = df[columns].copy()

    clean_df = clean_df.dropna(subset=['Date', 'RegionName', 'AveragePrice'])

    clean_df.to_csv(
        clean_file,
        index=False
    )

    print('Data cleaning completed')
    print(clean_df.shape)
    print(clean_df.head())

if __name__ == '__main__':
    clean_data()

