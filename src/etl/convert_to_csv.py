import pandas as pd
import os

RAW_PATH = "data/raw"
PROCESSED_PATH = "data/processed"

os.makedirs(PROCESSED_PATH, exist_ok=True)

FILES = ["profit_loss.xlsx", "balance_sheet.xlsx", "cash_flow.xlsx", "companies.xlsx"]


def clean_file(file):
    try:
        path = os.path.join(RAW_PATH, file)

        df = pd.read_excel(path, skiprows=1)

        # remove unnamed junk columns
        df = df.loc[:, ~df.columns.str.contains("^Unnamed")]

        # normalize column names
        df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

        # REQUIRED FIX
        if "company" in df.columns:
            df = df.rename(columns={"company": "company_id"})

        if "year" not in df.columns:
            df["year"] = 2023

        df.to_csv(os.path.join(PROCESSED_PATH, file.replace(".xlsx", ".csv")), index=False)

        print(f"Converted {file}")

    except Exception as e:
        print(f" Failed {file}: {e}")


for f in FILES:
    clean_file(f)