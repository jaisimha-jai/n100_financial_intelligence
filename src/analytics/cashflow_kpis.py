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

    raise Exception(" No cashflow table found in DB")


# ---------------- LOAD DATA ----------------
def load_data():
    conn = sqlite3.connect(DB_PATH)

    table_name = get_cashflow_table(conn)
    print(f"Using table: {table_name}")

    query = f"""
        SELECT cf.*, c.company_name, c.sector
        FROM {table_name} cf
        LEFT JOIN companies c
        ON cf.company_id = c.id
    """

    df = pd.read_sql(query, conn)

    conn.close()
    return df


# ---------------- MAIN COMPUTE ----------------
def compute():

    df = load_data()

    if df.empty:
        print("No data found")
        return

    # ---------------- CLEAN ----------------
    df.columns = df.columns.str.lower().str.strip()

    rename_map = {
        "cfo": "cash_from_operating_activity",
        "operating_cash_flow": "cash_from_operating_activity",

        "cfi": "cash_from_investing_activity",
        "investing_cash_flow": "cash_from_investing_activity",

        "cff": "cash_from_financing_activity",
        "financing_cash_flow": "cash_from_financing_activity",

        "sales": "revenue"
    }

    df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns}, inplace=True)

    required_cols = [
        "cash_from_operating_activity",
        "cash_from_investing_activity",
        "cash_from_financing_activity",
        "net_profit",
        "revenue"
    ]

    for col in required_cols:
        if col not in df.columns:
            df[col] = 0

        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    df = df.sort_values("year")

    grouped = df.groupby("company_id")

    results = []
    distress_rows = []

    # ---------------- LOOP ----------------
    for cid, g in grouped:

        g = g.sort_values("year")
        latest = g.iloc[-1]

        # ---------------- CFO QUALITY ----------------
        g["cfo_pat"] = g["cash_from_operating_activity"] / (g["net_profit"].replace(0, 1))
        avg_ratio = g["cfo_pat"].tail(5).mean()

        if avg_ratio > 1:
            quality_label = "High Quality"
        elif avg_ratio > 0.5:
            quality_label = "Moderate"
        else:
            quality_label = "Accrual Risk"

        # ---------------- CAPEX ----------------
        capex = abs(g["cash_from_investing_activity"])
        capex_pct = (capex / (g["revenue"] + 1)) * 100
        capex_avg = capex_pct.tail(5).mean()

        if capex_avg < 3:
            capex_label = "Asset Light"
        elif capex_avg < 8:
            capex_label = "Moderate"
        else:
            capex_label = "Capital Intensive"

        # ---------------- FCF ----------------
        g["fcf"] = g["cash_from_operating_activity"] + g["cash_from_investing_activity"]

        fcf_cagr = 0
        if len(g) >= 5:
            start = g["fcf"].iloc[-5]
            end = g["fcf"].iloc[-1]

            if start > 0:
                fcf_cagr = ((end / start) ** (1/5) - 1) * 100

        fcf_conversion = (
            g["fcf"].tail(5).mean() /
            (g["net_profit"].tail(5).mean() + 1)
        ) * 100

        # ---------------- DISTRESS ----------------
        distress_flag = False
        if latest["cash_from_operating_activity"] < 0 and latest["cash_from_financing_activity"] > 0:
            distress_flag = True

            distress_rows.append({
                "company_id": cid,
                "cfo": latest["cash_from_operating_activity"],
                "cff": latest["cash_from_financing_activity"],
                "net_profit": latest["net_profit"]
            })

        # ---------------- DELEVERAGING ----------------
        deleveraging_flag = latest["cash_from_financing_activity"] < 0

        # ---------------- CAPITAL ALLOCATION ----------------
        if latest["cash_from_operating_activity"] > 0 and latest["cash_from_investing_activity"] < 0:
            allocation = "Reinvestor"
        elif latest["cash_from_operating_activity"] > 0 and latest["cash_from_financing_activity"] < 0:
            allocation = "Shareholder Return"
        elif latest["cash_from_operating_activity"] < 0:
            allocation = "Distress Signal"
        else:
            allocation = "Neutral"

        results.append({
            "company_id": cid,
            "sector": latest.get("sector", "Unknown"),
            "cfo_quality_score": round(avg_ratio, 2),
            "cfo_quality_label": quality_label,
            "capex_intensity_pct": round(capex_avg, 2),
            "capex_label": capex_label,
            "fcf_cagr_5yr": round(fcf_cagr, 2),
            "fcf_conversion_pct": round(fcf_conversion, 2),
            "distress_flag": distress_flag,
            "deleveraging_flag": deleveraging_flag,
            "capital_allocation_label": allocation
        })

    # ---------------- SAVE ----------------
    output_df = pd.DataFrame(results)

    excel_path = os.path.join(OUTPUT_DIR, "cashflow_intelligence.xlsx")
    csv_path = os.path.join(OUTPUT_DIR, "distress_alerts.csv")

    output_df.to_excel(excel_path, index=False)
    pd.DataFrame(distress_rows).to_csv(csv_path, index=False)

    print("cashflow_intelligence.xlsx created")
    print("distress_alerts.csv created")


# ---------------- RUN ----------------
if __name__ == "__main__":
    compute()