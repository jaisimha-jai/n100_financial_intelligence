import sqlite3
import pandas as pd

DB_PATH = "db/nifty100.db"

def generate_audit():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    tables = [
        "companies",
        "sectors",
        "peer_groups",
        "profitandloss",
        "balancesheet",
        "cashflow",
        "stock_prices",
        "analysis",
        "financial_ratios",
        "market_cap",
        "documents",
        "prosandcons"
    ]

    audit_data = []

    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]

        audit_data.append({
            "table_name": table,
            "row_count": count
        })

    df = pd.DataFrame(audit_data)
    df.to_csv("output/load_audit.csv", index=False)

    print("Load audit created successfully!")

    conn.close()


if __name__ == "__main__":
    generate_audit()