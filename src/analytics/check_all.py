import pandas as pd

files = {
    "companies": "data/processed/companies.csv",
    "profit_loss": "data/processed/profit_loss.csv",
    "balance_sheet": "data/processed/balance_sheet.csv",
    "cash_flow": "data/processed/cash_flow.csv",
    "ratios": "data/processed/financial_ratios.csv"
}

for name, path in files.items():
    print("\n==========", name.upper(), "==========")

    try:
        df = pd.read_csv(path)
        print("Columns:", list(df.columns))
        print("Rows:", len(df))
    except Exception as e:
        print("ERROR:", e)