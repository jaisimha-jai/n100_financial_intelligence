import pandas as pd
import sqlite3
from pathlib import Path

conn = sqlite3.connect("db/nifty100.db")

PROCESSED_PATH = Path("data/processed")

for file in PROCESSED_PATH.glob("*.csv"):
    table_name = file.stem
    print(f"Loading: {table_name}")

    df = pd.read_csv(file)
    df.to_sql(table_name, conn, if_exists="replace", index=False)

print("All data loaded into DB")
conn.close()