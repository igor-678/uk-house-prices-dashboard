import pandas as pd
from pathlib import Path


def clean_data():

    BASE_DIR = Path(__file__).resolve().parent.parent

    raw_file = BASE_DIR / "data" / "raw" / "uk_hpi.csv"
    clean_file = BASE_DIR / "data" / "cleaned" / "house_prices_clean.csv"

    df = pd.read_csv(raw_file)

    # Map each ONS AreaCode prefix to geography lvl
    level_map = {
        "K02": "UK_Aggregate",
        "K03": "UK_Aggregate",
        "K04": "UK_Aggregate",
        "E92": "Country",
        "S92": "Country",
        "W92": "Country",
        "N92": "Country",
        "E12": "Region",
        "E13": "Region",
        "E06": "LocalAuthority",
        "E07": "LocalAuthority",
        "E08": "LocalAuthority",
        "E09": "LocalAuthority",
        "E10": "LocalAuthority",
        "E11": "LocalAuthority",
        "N09": "LocalAuthority",
        "S12": "LocalAuthority",
        "W06": "LocalAuthority"
    }

    df['prefix'] = df['AreaCode'].str[:3]
    df['GeographyLevel'] = df['prefix'].map(level_map)

    #check if any prefixes didnt account for
    unmapped = df[df['GeographyLevel'].isna()]
    if not unmapped.empty:
        print('Warning: unmapped AreaCode prefixes found:')
        print(unmapped['prefix'].unique())

    df['Date'] = pd.to_datetime(
        df['Date'],
        dayfirst = True,
        errors = 'coerce'
    )

    df = df[df['Date'] >= '1995-01-01']

    columns = [
        'Date',
        'RegionName',
        'AreaCode',
        'GeographyLevel',
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
    print(clean_df['GeographyLevel'].value_counts())

if __name__ == '__main__':
    clean_data()

