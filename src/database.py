import sqlite3
import pandas as pd
from pathlib import Path



BASE_DIR = Path(__file__).resolve().parent.parent

clean_file = BASE_DIR / 'data' / 'cleaned' / 'house_prices_clean.csv'
db_file = BASE_DIR / 'data' / 'house_prices.db'


df = pd.read_csv(clean_file)

conn = sqlite3.connect(db_file)

df.to_sql('house_prices',
          conn,
          if_exists='replace',
          index=False
)


conn.execute("""
    CREATE INDEX IF NOT EXISTS idx_house_prices_region_date
    ON house_prices (RegionName, Date)
""")

conn.commit()

conn.close()

print('Database created')
print(df.shape)





