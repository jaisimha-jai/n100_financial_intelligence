import pandas as pd
import sqlite3
import os
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
DB_PATH = os.path.join(BASE_DIR, "db", "nifty100.db")
OUTPUT_PATH = os.path.join(BASE_DIR, "reports", "portfolio", "portfolio_summary.pdf")

os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)


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


def trend_arrow(latest, prev):
    if pd.isna(latest) or pd.isna(prev):
        return "→"

    if abs(latest - prev) / (abs(prev) + 1) <= 0.02:
        return "→"
    elif latest > prev:
        return "↑"
    else:
        return "↓"


def generate():
    df = load_data()

    if df.empty:
        print("No data found")
        return

    df = df.sort_values(["company_name", "year"])

    styles = getSampleStyleSheet()
    elements = []

    companies = sorted(df["company_name"].dropna().unique())

    for company in companies:
        g = df[df["company_name"] == company].sort_values("year")

        if len(g) < 2:
            continue

        latest = g.iloc[-1]
        prev = g.iloc[-2]

        sector = latest.get("sector", "Unknown")

        def safe(col):
            return pd.to_numeric(g[col], errors="coerce") if col in g.columns else pd.Series()

        revenue = safe("sales")
        profit = safe("net_profit")
        roe = safe("roe")
        roce = safe("roce")
        de = safe("de_ratio")
        fcf = safe("free_cash_flow")

        kpis = [
            ("Revenue", revenue.iloc[-1] if not revenue.empty else None,
             trend_arrow(revenue.iloc[-1], revenue.iloc[-2]) if len(revenue) > 1 else "→"),

            ("Net Profit", profit.iloc[-1] if not profit.empty else None,
             trend_arrow(profit.iloc[-1], profit.iloc[-2]) if len(profit) > 1 else "→"),

            ("ROE", roe.iloc[-1] if not roe.empty else None,
             trend_arrow(roe.iloc[-1], roe.iloc[-2]) if len(roe) > 1 else "→"),

            ("ROCE", roce.iloc[-1] if not roce.empty else None,
             trend_arrow(roce.iloc[-1], roce.iloc[-2]) if len(roce) > 1 else "→"),

            ("Debt/Equity", de.iloc[-1] if not de.empty else None,
             trend_arrow(de.iloc[-1], de.iloc[-2]) if len(de) > 1 else "→"),

            ("FCF", fcf.iloc[-1] if not fcf.empty else None,
             trend_arrow(fcf.iloc[-1], fcf.iloc[-2]) if len(fcf) > 1 else "→"),
        ]

        # ---- PAGE CONTENT ----
        elements.append(Paragraph(f"<b>{company}</b>", styles["Title"]))
        elements.append(Paragraph(f"Sector: {sector}", styles["Normal"]))
        elements.append(Spacer(1, 12))

        for name, value, arrow in kpis:
            if value is None or pd.isna(value):
                val_str = "N/A"
            else:
                val_str = f"{round(value, 2)}"

            elements.append(
                Paragraph(f"{name}: {val_str} {arrow}", styles["Normal"])
            )

        elements.append(PageBreak())

    doc = SimpleDocTemplate(OUTPUT_PATH, pagesize=A4)
    doc.build(elements)

    print("portfolio_summary.pdf generated successfully")


if __name__ == "__main__":
    generate()