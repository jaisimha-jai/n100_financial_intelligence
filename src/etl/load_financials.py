import pandas as pd
import sqlite3
import os

DB_PATH = "data/database.db"

DATA_PATH = "data"  # where your CSV/Excel files are


def get_connection():
    return sqlite3.connect(DB_PATH)


def normalize_year(df):
    df["year"] = df["year"].astype(str).str.extract(r'(\d{4})')[0]
    df["year"] = df["year"].astype(int)
    return df


def load_profit_loss(conn):
    path = os.path.join(DATA_PATH, "profit_loss.csv")

    if not os.path.exists(path):
        print("❌ profit_loss.csv not found")
        return

    df = pd.read_csv(path)
    df = normalize_year(df)

    df.to_sql("profit_loss", conn, if_exists="replace", index=False)
    print("✅ profit_loss loaded")


def load_balance_sheet(conn):
    path = os.path.join(DATA_PATH, "balance_sheet.csv")

    if not os.path.exists(path):
        print("❌ balance_sheet.csv not found")
        return

    df = pd.read_csv(path)
    df = normalize_year(df)

    df.to_sql("balance_sheet", conn, if_exists="replace", index=False)
    print("✅ balance_sheet loaded")


def load_cash_flow(conn):
    path = os.path.join(DATA_PATH, "cash_flow.csv")

    if not os.path.exists(path):
        print("❌ cash_flow.csv not found")
        return

    df = pd.read_csv(path)
    df = normalize_year(df)

    df.to_sql("cash_flow", conn, if_exists="replace", index=False)
    print("✅ cash_flow loaded")


def run():
    conn = get_connection()

    load_profit_loss(conn)
    load_balance_sheet(conn)
    load_cash_flow(conn)

    conn.close()

    print("🎯 All financial tables loaded")


if __name__ == "__main__":
    run()