import pandas as pd
import sqlite3
import os
import re
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

# ---------------- PATHS ----------------
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
DB_PATH = os.path.join(BASE_DIR, "db", "nifty100.db")
OUTPUT_DIR = os.path.join(BASE_DIR, "reports", "sector")

os.makedirs(OUTPUT_DIR, exist_ok=True)

styles = getSampleStyleSheet()

# ---------------- EXPECTED SECTORS (FOR SPRINT REQUIREMENT) ----------------
EXPECTED_SECTORS = [
    "IT", "Banking", "Finance", "FMCG", "Pharma",
    "Auto", "Energy", "Cement", "Metals", "Telecom", "Infra"
]


# ---------------- SAFE COLUMN FETCH ----------------
def get_col(df, names):
    for n in names:
        if n in df.columns:
            return pd.to_numeric(df[n], errors="coerce")
    return pd.Series([0] * len(df))


# ---------------- CLEAN FILE NAME ----------------
def clean_filename(name):
    name = str(name)
    name = re.sub(r'[\\/*?:"<>|&\n]', '', name)
    name = name.replace(" ", "_")
    return name.strip()


# ---------------- LOAD DATA ----------------
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


# ---------------- MAIN ----------------
def generate():

    df = load_data()

    if df.empty:
        print("No data found")
        return

    # -------- CLEAN SECTORS --------
    df["sector"] = df["sector"].fillna("Unknown")

    sector_map = {
        "Financials": "Finance",
        "Banks": "Banking",
        "Healthcare": "Pharma",
        "Pharmaceuticals": "Pharma",
        "Consumer Goods": "FMCG",
        "Information Technology": "IT",
    }

    df["sector"] = df["sector"].replace(sector_map)

    # -------- SAFE METRICS --------
    df["roe"] = get_col(df, ["roe", "roe_ratio", "return_on_equity"])
    df["pe"] = get_col(df, ["pe_ratio", "pe"])
    df["de"] = get_col(df, ["de_ratio", "debt_to_equity"])

    # -------- LATEST YEAR --------
    df = df.sort_values("year", ascending=False)
    df = df.drop_duplicates(subset="company_name")

    total = 0

    # -------- LOOP ALL EXPECTED SECTORS --------
    for sector in EXPECTED_SECTORS:
        try:
            sdf = df[df["sector"] == sector]

            filename = clean_filename(sector) + "_report.pdf"
            path = os.path.join(OUTPUT_DIR, filename)

            doc = SimpleDocTemplate(path)
            elements = []

            # -------- TITLE --------
            elements.append(Paragraph(f"<b>{sector} Sector Report</b>", styles["Title"]))
            elements.append(Spacer(1, 12))

            if sdf.empty:
                # Handle empty sector
                elements.append(Paragraph("No companies available in this sector.", styles["Normal"]))
                doc.build(elements)
                print(f"⚠ Created EMPTY: {sector}")
                total += 1
                continue

            # -------- MEDIANS --------
            med_roe = round(sdf["roe"].median(), 2)
            med_pe = round(sdf["pe"].median(), 2)
            med_de = round(sdf["de"].median(), 2)

            elements.append(Paragraph(f"Median ROE: {med_roe}", styles["Normal"]))
            elements.append(Paragraph(f"Median P/E: {med_pe}", styles["Normal"]))
            elements.append(Paragraph(f"Median D/E: {med_de}", styles["Normal"]))
            elements.append(Spacer(1, 12))

            # -------- TABLE --------
            table_data = [["Company", "ROE", "P/E", "D/E"]]

            for _, row in sdf.iterrows():
                table_data.append([
                    str(row.get("company_name", "")),
                    round(row.get("roe", 0), 2),
                    round(row.get("pe", 0), 2),
                    round(row.get("de", 0), 2),
                ])

            table = Table(table_data, repeatRows=1)

            table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("WORDWRAP", (0, 0), (-1, -1), None),
            ]))

            elements.append(table)

            doc.build(elements)

            print(f"Created: {sector}")
            total += 1

        except Exception as e:
            print(f"Error: {sector} -> {e}")

    print(f"\n🎯 Total sector reports generated: {total}")


# ---------------- RUN ----------------
if __name__ == "__main__":
    generate()