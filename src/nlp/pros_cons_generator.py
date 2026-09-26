import pandas as pd
import sqlite3
import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
DB_PATH = os.path.join(BASE_DIR, "db", "nifty100.db")
OUTPUT_PATH = os.path.join(BASE_DIR, "output", "pros_cons_generated.csv")


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


def generate():

    df = load_data()

    # ---------------- CLEAN COLUMN NAMES ----------------
    df.columns = df.columns.str.lower().str.strip()

    print("Columns Found:", df.columns.tolist())

    # ---------------- RENAME COMMON VARIANTS ----------------
    rename_map = {
        "roe_percent": "roe",
        "return_on_equity": "roe",
        "roe_ratio": "roe",

        "de": "de_ratio",
        "debt_equity": "de_ratio",

        "revenue_cagr": "revenue_cagr_5yr",
        "pat_cagr": "pat_cagr_5yr",

        "profit_after_tax": "net_profit"
    }

    df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns}, inplace=True)

    # ---------------- REQUIRED COLUMNS ----------------
    required_cols = [
        "roe", "de_ratio", "revenue_cagr_5yr",
        "pat_cagr_5yr", "net_profit",
        "free_cash_flow", "opm",
        "interest_coverage_ratio", "dividend_yield",
        "eps", "roce", "revenue"
    ]

    for col in required_cols:
        if col not in df.columns:
            df[col] = 0

    # Convert numeric safely
    for col in required_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    # ---------------- SORT DATA ----------------
    df = df.sort_values("year")
    grouped = df.groupby("company_id")

    results = []

    # ---------------- LOOP PER COMPANY ----------------
    for cid, g in grouped:

        g = g.sort_values("year")
        latest = g.iloc[-1]

        # ---------------- PRO RULES ----------------

        if (g["roe"] > 20).tail(3).all():
            results.append((cid, "pro", "P1", "High ROE above 20%", 90))

        if (g["free_cash_flow"] > 0).tail(5).all():
            results.append((cid, "pro", "P2", "Strong free cash flow over 5 years", 85))

        if latest["de_ratio"] == 0:
            results.append((cid, "pro", "P3", "Debt-free company", 95))

        if latest["revenue_cagr_5yr"] > 15:
            results.append((cid, "pro", "P4", "Revenue CAGR above 15%", 80))

        if latest["opm"] > 25:
            results.append((cid, "pro", "P5", "High operating margin", 80))

        if latest["pat_cagr_5yr"] > 20:
            results.append((cid, "pro", "P6", "Strong profit growth", 85))

        if latest["interest_coverage_ratio"] > 10:
            results.append((cid, "pro", "P7", "Strong interest coverage", 85))

        if latest["dividend_yield"] > 2:
            results.append((cid, "pro", "P8", "Good dividend yield", 75))

        if (g["eps"] > 0).tail(5).all():
            results.append((cid, "pro", "P9", "Consistent EPS growth", 80))

        if len(g) >= 3 and list(g["roe"].tail(3)) == sorted(g["roe"].tail(3)):
            results.append((cid, "pro", "P10", "Improving ROE trend", 75))

        if latest["revenue_cagr_5yr"] < latest["pat_cagr_5yr"]:
            results.append((cid, "pro", "P11", "Operating leverage improving", 70))

        if latest["de_ratio"] < 0.5:
            results.append((cid, "pro", "P12", "Low leverage supports growth", 70))

        # ---------------- CON RULES ----------------

        if latest["de_ratio"] > 2:
            results.append((cid, "con", "C1", "High debt levels", 85))

        if (g["free_cash_flow"] < 0).tail(3).all():
            results.append((cid, "con", "C2", "Negative cash flow for 3 years", 90))

        if len(g) >= 3 and list(g["opm"].tail(3)) == sorted(g["opm"].tail(3), reverse=True):
            results.append((cid, "con", "C3", "Declining margins", 80))

        if latest["net_profit"] < 0:
            results.append((cid, "con", "C4", "Company is loss-making", 90))

        if len(g) >= 2 and g["revenue"].tail(2).iloc[-1] < g["revenue"].tail(2).iloc[0]:
            results.append((cid, "con", "C5", "Revenue declining", 75))

        if latest["interest_coverage_ratio"] < 1.5:
            results.append((cid, "con", "C6", "Weak interest coverage", 85))

        if latest.get("dividend_payout", 0) > 100:
            results.append((cid, "con", "C7", "Unsustainable dividend payout", 80))

        if len(g) >= 3 and list(g["de_ratio"].tail(3)) == sorted(g["de_ratio"].tail(3)):
            results.append((cid, "con", "C8", "Increasing debt trend", 75))

        if len(g) >= 3 and list(g["eps"].tail(3)) == sorted(g["eps"].tail(3), reverse=True):
            results.append((cid, "con", "C9", "Declining EPS", 80))

        if latest["roce"] < 10:
            results.append((cid, "con", "C10", "Low capital efficiency", 80))

        if latest.get("net_debt_to_ebitda", 0) > 3:
            results.append((cid, "con", "C11", "High leverage risk", 85))

        if latest["revenue_cagr_5yr"] < 5:
            results.append((cid, "con", "C12", "Weak growth (<5%)", 75))

    # ---------------- FINAL OUTPUT ----------------

    out = pd.DataFrame(results, columns=[
        "company_id", "type", "rule_id", "text", "confidence_pct"
    ])

    out = out[out["confidence_pct"] > 60]

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    out.to_csv(OUTPUT_PATH, index=False)

    print(" pros_cons_generated.csv created successfully")


if __name__ == "__main__":
    generate()