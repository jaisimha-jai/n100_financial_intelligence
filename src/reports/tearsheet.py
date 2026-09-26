import os
import re
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
)
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet

# ---------------- PATHS ----------------
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
DB_PATH = os.path.join(BASE_DIR, "db", "nifty100.db")
OUTPUT_DIR = os.path.join(BASE_DIR, "reports", "tearsheets")
CHART_DIR = os.path.join(BASE_DIR, "temp_charts")

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(CHART_DIR, exist_ok=True)

styles = getSampleStyleSheet()


# ---------------- HELPERS ----------------
def safe(val):
    try:
        return round(float(val), 2)
    except:
        return "N/A"


def clean_filename(name):
    name = str(name)

    name = name.replace("\n", " ").replace("\r", " ").replace("\t", " ")
    name = re.sub(r'[<>:"/\\|?*&]', '', name)

    name = " ".join(name.split()[:5])
    name = name.strip().replace(" ", "_")

    return name


# ---------------- LOAD DATA ----------------
def load_data():
    conn = sqlite3.connect(DB_PATH)

    df = pd.read_sql("""
    SELECT fr.*, 
                TRIM(REPLACE(REPLACE(c.company_name, CHAR(10), ' '), CHAR(13), ' ')) as company_name,
                c.sector
        FROM financial_ratios fr
        LEFT JOIN companies c ON fr.company_id = c.id
    """, conn)

    conn.close()
    return df


# ---------------- KPI TABLE ----------------
def kpi_table(latest):
    data = [
        ["ROE", safe(latest.get("roe"))],
        ["D/E", safe(latest.get("de_ratio"))],
        ["Rev CAGR", safe(latest.get("revenue_cagr_5yr"))],
        ["PAT CAGR", safe(latest.get("pat_cagr_5yr"))],
        ["Net Profit", safe(latest.get("net_profit"))],
        ["Year", str(latest.get("year"))],
    ]

    table = Table(data, colWidths=[150, 150])
    table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightblue),
    ]))

    return table


# ---------------- CHARTS ----------------
def create_rev_profit_chart(df, name):
    df = df.sort_values("year")

    if "revenue" not in df.columns:
        return None

    plt.figure()
    plt.plot(df["year"], df["revenue"], label="Revenue")
    plt.plot(df["year"], df["net_profit"], label="Net Profit")
    plt.xticks(rotation=45)
    plt.legend()

    path = os.path.join(CHART_DIR, clean_filename(name) + "_rev.png")
    plt.savefig(path, bbox_inches="tight")
    plt.close()

    return path


def create_roe_chart(df, name):
    df = df.sort_values("year")

    if "roe" not in df.columns:
        return None

    plt.figure()
    plt.plot(df["year"], df["roe"])
    plt.xticks(rotation=45)

    path = os.path.join(CHART_DIR, clean_filename(name) + "_roe.png")
    plt.savefig(path, bbox_inches="tight")
    plt.close()

    return path


# ---------------- PROS / CONS ----------------
def get_pros_cons(company_id):
    path = os.path.join(BASE_DIR, "output", "pros_cons_generated.csv")

    if not os.path.exists(path):
        return ["No pros"], ["No cons"]

    df = pd.read_csv(path)
    df = df[df["company_id"] == company_id]

    pros = df[df["type"] == "pro"]["text"].head(5).tolist()
    cons = df[df["type"] == "con"]["text"].head(5).tolist()

    return pros or ["No pros"], cons or ["No cons"]


# ---------------- PDF BUILDER ----------------
def build_pdf(company, group):
    name = company["company_name"]

    filename = clean_filename(name)[:60] + "_tearsheet.pdf"
    path = os.path.join(OUTPUT_DIR, filename)

    doc = SimpleDocTemplate(path, pagesize=letter)
    elements = []

    latest = group.sort_values("year").iloc[-1]

    # -------- PAGE 1 --------
    elements.append(Paragraph(f"<b>{name}</b>", styles["Title"]))
    elements.append(Paragraph(f"Sector: {company.get('sector', 'N/A')}", styles["Normal"]))
    elements.append(Spacer(1, 10))

    elements.append(Paragraph("<b>Key Metrics</b>", styles["Heading2"]))
    elements.append(kpi_table(latest))

    elements.append(Spacer(1, 15))

    # Charts
    rev_chart = create_rev_profit_chart(group, name)
    roe_chart = create_roe_chart(group, name)

    if rev_chart:
        elements.append(Paragraph("<b>Revenue & Profit Trend</b>", styles["Heading2"]))
        elements.append(Image(rev_chart, width=400, height=200))
        elements.append(Spacer(1, 10))

    if roe_chart:
        elements.append(Paragraph("<b>ROE Trend</b>", styles["Heading2"]))
        elements.append(Image(roe_chart, width=400, height=200))

    # -------- PAGE BREAK --------
    elements.append(PageBreak())

    # -------- PAGE 2 --------
    elements.append(Paragraph("<b>Pros</b>", styles["Heading2"]))

    pros, cons = get_pros_cons(company["company_id"])

    for p in pros:
        elements.append(Paragraph(f"• {p}", styles["Normal"]))

    elements.append(Spacer(1, 10))

    elements.append(Paragraph("<b>Cons</b>", styles["Heading2"]))

    for c in cons:
        elements.append(Paragraph(f"• {c}", styles["Normal"]))

    elements.append(Spacer(1, 10))

    elements.append(Paragraph(
        "<b>Note:</b> Auto-generated report based on financial data.",
        styles["Italic"]
    ))

    doc.build(elements)


# ---------------- MAIN ----------------
def generate():
    df = load_data()

    if df.empty:
        print("No data found")
        return

    generated = 0
    skipped = []

    for cid, group in df.groupby("company_id"):

        if pd.isna(group.iloc[0]["company_name"]):
            continue

        if len(group) < 3:
            skipped.append(cid)
            continue

        try:
            build_pdf(group.iloc[0], group)
            print("Created:", group.iloc[0]["company_name"])
            generated += 1
        except Exception as e:
            print("Error:", group.iloc[0]["company_name"], "->", e)
            skipped.append(cid)

    pd.DataFrame({"company_id": skipped}).to_csv(
        os.path.join(BASE_DIR, "output", "skipped_tearsheets.csv"),
        index=False
    )

    print("\nSUMMARY")
    print("Generated:", generated)
    print("Skipped:", len(skipped))


if __name__ == "__main__":
    generate()