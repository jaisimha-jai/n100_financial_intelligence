import pandas as pd

def save_ratios():
    # Load data
    pl = pd.read_csv("data/processed/profit_loss.csv")
    bs = pd.read_csv("data/processed/balance_sheet.csv")
    cf = pd.read_csv("data/processed/cash_flow.csv")

    pl = pl.drop(columns=["id"], errors="ignore")
    bs = bs.drop(columns=["id"], errors="ignore")
    cf = cf.drop(columns=["id"], errors="ignore")

    df = pd.merge(pl, bs, on=["company_id", "year"], how="left")
    df = pd.merge(df, cf, on=["company_id", "year"], how="left")

    df["revenue"] = df["sales"]

    df["total_equity"] = df["equity_capital"] + df["reserves"]

    df["roe"] = df["net_profit"] / df["total_equity"]

    df["debt_to_equity"] = df["borrowings"] / df["total_equity"]

    df["operating_profit_margin"] = df["operating_profit"] / df["revenue"]

    df["asset_turnover"] = df["revenue"] / df["total_assets"]

    df = df.replace([float("inf"), float("-inf")], 0)
    df = df.fillna(0)

    df.to_csv("data/processed/ratios.csv", index=False)

    print(" ratios.csv created successfully")


if __name__ == "__main__":
    save_ratios()