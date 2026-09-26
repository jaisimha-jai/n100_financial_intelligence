import pandas as pd
import sqlite3
import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
DB_PATH = os.path.join(BASE_DIR, "db", "nifty100.db")

OUTPUT_DIR = os.path.join(BASE_DIR, "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)


# ---------------- AUTO TABLE DETECTION ----------------
def get_cashflow_table(conn):
    tables = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table';", conn)
    table_list = tables["name"].str.lower().tolist()

    for t in table_list:
        if "cash" in t:
            return t

    raise Exception(" No cashflow table found")


# ---------------- LOAD DATA ----------------
def load_data():
    conn = sqlite3.connect(DB_PATH)

    table_name = get_cashflow_table(conn)
    print(f" Using table: {table_name}")

    query = f"""
        SELECT cf.*, c.company_name, c.sector
        FROM {table_name} cf
        LEFT JOIN companies c
        ON cf.company_id = c.id
    """

    df = pd.read_sql(query, conn)
    conn.close()

    return df


# ---------------- CLASSIFY ----------------
def classify(row):
    if row["cash_from_operating_activity"] > 0 and row["cash_from_investing_activity"] < 0:
        return "Reinvestor"
    elif row["cash_from_operating_activity"] > 0 and row["cash_from_financing_activity"] < 0:
        return "Shareholder Return"
    elif row["cash_from_operating_activity"] < 0:
        return "Distress Signal"
    else:
        return "Neutral"


# ---------------- MAIN ----------------
def generate():

    df = load_data()

    if df.empty:
        print("No data")
        return

    # -------- CLEAN --------
    df.columns = df.columns.str.lower().str.strip()

    rename_map = {
        "cfo": "cash_from_operating_activity",
        "operating_cash_flow": "cash_from_operating_activity",

        "cfi": "cash_from_investing_activity",
        "investing_cash_flow": "cash_from_investing_activity",

        "cff": "cash_from_financing_activity",
        "financing_cash_flow": "cash_from_financing_activity"
    }

    df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns}, inplace=True)

    cols = [
        "cash_from_operating_activity",
        "cash_from_investing_activity",
        "cash_from_financing_activity"
    ]

    for col in cols:
        if col not in df.columns:
            df[col] = 0

        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    df = df.sort_values(["company_id", "year"])

    # -------- CLASSIFY --------
    df["capital_allocation"] = df.apply(classify, axis=1)

    # -------- PATTERN CHANGES --------
    changes = []

    for cid, g in df.groupby("company_id"):
        g = g.sort_values("year")

        prev = None

        for _, row in g.iterrows():
            curr = row["capital_allocation"]

            if prev and prev != curr:
                changes.append({
                    "company_id": cid,
                    "year": row["year"],
                    "from": prev,
                    "to": curr
                })

            prev = curr

    changes_df = pd.DataFrame(changes)

    # -------- LATEST YEAR SUMMARY --------
    latest_year = df["year"].max()
    latest_df = df[df["year"] == latest_year]

    summary = latest_df["capital_allocation"].value_counts().reset_index()
    summary.columns = ["pattern", "count"]

    # -------- SAVE --------
    changes_path = os.path.join(OUTPUT_DIR, "pattern_changes.csv")
    summary_path = os.path.join(OUTPUT_DIR, "allocation_summary.csv")

    changes_df.to_csv(changes_path, index=False)
    summary.to_csv(summary_path, index=False)

    print("pattern_changes.csv created")
    print("allocation_summary.csv created")


# ---------------- RUN ----------------
if __name__ == "__main__":
    generate()