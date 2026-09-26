import pandas as pd
import sqlite3
import os

# -----------------------------
# PATH SETUP
# -----------------------------
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
DB_PATH = os.path.join(BASE_DIR, "db", "nifty100.db")

OUTPUT_DIR = os.path.join(BASE_DIR, "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)


# -----------------------------
# LOAD DATA
# -----------------------------
def load_data():
    conn = sqlite3.connect(DB_PATH)

    df = pd.read_sql("""
        SELECT fr.*, c.company_name, c.sector
        FROM financial_ratios fr
        LEFT JOIN companies c
        ON fr.company_id = c.id
    """, conn)

    conn.close()
    return df


# -----------------------------
# MAIN FUNCTION
# -----------------------------
def compute_valuation():

    df = load_data()

    if df.empty:
        print("❌ No data found")
        return

    # -----------------------------
    # CLEAN NUMERIC
    # -----------------------------
    num_cols = ["net_profit", "free_cash_flow"]

    for col in num_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df["sector"] = df.get("sector", "Unknown").fillna("Unknown")

    # -----------------------------
    # 🔥 CREATE PE RATIO (FIXED BUG)
    # -----------------------------
    if "pe_ratio" not in df.columns:
        df["pe_ratio"] = df["net_profit"]

    df["pe_ratio"] = pd.to_numeric(df["pe_ratio"], errors="coerce")
    df["pe_ratio"] = df["pe_ratio"].replace(0, 1).fillna(1)

    # -----------------------------
    # LATEST YEAR PER COMPANY
    # -----------------------------
    df = df.sort_values("year", ascending=False)
    df_latest = df.drop_duplicates(subset="company_name").copy()

    # -----------------------------
    # LOAD MARKET CAP
    # -----------------------------
    try:
        market_cap = pd.read_excel(
            os.path.join(BASE_DIR, "data", "market_cap.xlsx")
        )
    except:
        print("❌ market_cap.xlsx not found (put inside /data folder)")
        return

    df_latest = df_latest.merge(market_cap, on="company_name", how="left")

    df_latest["market_cap_crore"] = pd.to_numeric(
        df_latest.get("market_cap_crore", 1),
        errors="coerce"
    ).fillna(1)

    # -----------------------------
    # FCF YIELD
    # -----------------------------
    df_latest["free_cash_flow"] = df_latest.get("free_cash_flow", 0).fillna(0)

    df_latest["fcf_yield_pct"] = (
        df_latest["free_cash_flow"] /
        (df_latest["market_cap_crore"] + 1)
    ) * 100

    # -----------------------------
    # REAL PE CALCULATION
    # -----------------------------
    df_latest["pe_ratio"] = (
        df_latest["market_cap_crore"] /
        df_latest["net_profit"].replace(0, 1)
    )

    df_latest["pe_ratio"] = df_latest["pe_ratio"].fillna(0)

    # -----------------------------
    # 5 YEAR MEDIAN PE
    # -----------------------------
    pe_5yr = (
        df.groupby("company_name")["pe_ratio"]
        .median()
        .reset_index()
    )

    pe_5yr.columns = ["company_name", "median_pe_5yr"]

    df_latest = df_latest.merge(pe_5yr, on="company_name", how="left")

    # -----------------------------
    # SECTOR MEDIAN PE
    # -----------------------------
    sector_median = (
        df_latest.groupby("sector")["pe_ratio"]
        .median()
        .reset_index()
    )

    sector_median.columns = ["sector", "sector_median_pe"]

    df_latest = df_latest.merge(sector_median, on="sector", how="left")

    # -----------------------------
    # PE VS SECTOR %
    # -----------------------------
    df_latest["pe_vs_sector_pct"] = (
        df_latest["pe_ratio"] /
        (df_latest["sector_median_pe"] + 1)
    ) * 100

    # -----------------------------
    # FLAGS
    # -----------------------------
    def flag(row):
        if row["pe_ratio"] > row["sector_median_pe"] * 1.5:
            return "Caution"
        elif row["pe_ratio"] < row["sector_median_pe"] * 0.7:
            return "Discount"
        else:
            return "Fair"

    df_latest["flag"] = df_latest.apply(flag, axis=1)

    # -----------------------------
    # OPTIONAL METRICS (SAFE)
    # -----------------------------
    df_latest["pb_ratio"] = df_latest.get("pb_ratio", 0)
    df_latest["ev_ebitda"] = df_latest.get("ev_ebitda", 0)

    # -----------------------------
    # FINAL OUTPUT
    # -----------------------------
    final_cols = [
        "company_id",
        "company_name",
        "sector",
        "pe_ratio",
        "pb_ratio",
        "ev_ebitda",
        "fcf_yield_pct",
        "median_pe_5yr",
        "pe_vs_sector_pct",
        "flag"
    ]

    for col in final_cols:
        if col not in df_latest.columns:
            df_latest[col] = 0

    output_df = df_latest[final_cols].copy()

    # -----------------------------
    # SAVE FILES
    # -----------------------------
    excel_path = os.path.join(OUTPUT_DIR, "valuation_summary.xlsx")
    csv_path = os.path.join(OUTPUT_DIR, "valuation_flags.csv")

    output_df.to_excel(excel_path, index=False)

    flagged = output_df[
        output_df["flag"].isin(["Caution", "Discount"])
    ]

    flagged.to_csv(csv_path, index=False)

    print("valuation_summary.xlsx created")
    print("valuation_flags.csv created")


# -----------------------------
# RUN
# -----------------------------
if __name__ == "__main__":
    compute_valuation()