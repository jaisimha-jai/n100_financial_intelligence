import pandas as pd

def compute_ratios():
    pl = pd.read_csv("data/processed/profit_loss.csv")
    bs = pd.read_csv("data/processed/balance_sheet.csv")
    cf = pd.read_csv("data/processed/cash_flow.csv")

    pl["company_id"] = pl["company_id"].astype(str)
    bs["company_id"] = bs["company_id"].astype(str)
    cf["company_id"] = cf["company_id"].astype(str)

    # CLEAN MERGE (NO DUPLICATES)
    df = pl.merge(bs, on=["company_id", "year"], how="inner", suffixes=("", "_bs"))
    df = df.merge(cf, on=["company_id", "year"], how="inner", suffixes=("", "_cf"))

    # CREATE METRICS
    df["total_equity"] = df["equity_capital"] + df["reserves"]
    df["revenue"] = df["sales"]

    df["roe"] = df["net_profit"] / df["total_equity"]
    df["debt_to_equity"] = df["borrowings"] / df["total_equity"]
    df["operating_profit_margin"] = df["operating_profit"] / df["revenue"]
    df["asset_turnover"] = df["revenue"] / df["total_assets"]

    # CLEAN VALUES
    df.replace([float("inf"), -float("inf")], None, inplace=True)
    df = df.where(pd.notnull(df), None)

    df.to_csv("data/processed/final_ratios.csv", index=False)
    print("final_ratios.csv recreated CLEAN")

if __name__ == "__main__":
    compute_ratios()