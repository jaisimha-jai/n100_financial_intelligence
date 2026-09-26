import pandas as pd
import sqlite3

conn = sqlite3.connect("db/nifty100.db")

df = pd.read_sql("SELECT * FROM financial_ratios", conn)
companies = pd.read_sql("SELECT id, company_name FROM companies", conn)

df = df.merge(companies, left_on="company_id", right_on="id", how="left")

def assign_sector(name):
    name = str(name).lower()

    if "bank" in name:
        return "Banking"
    elif "pharma" in name or "lab" in name:
        return "Pharma"
    elif "tech" in name or "info" in name:
        return "IT"
    elif "cement" in name:
        return "Cement"
    elif "energy" in name or "power" in name:
        return "Energy"
    elif "auto" in name or "motor" in name:
        return "Auto"
    else:
        return "Others"

df["peer_group"] = df["company_name"].apply(assign_sector)

print("\nPeer Group Distribution:")
print(df["peer_group"].value_counts())

metrics = [
    "net_profit",
    "revenue_cagr_5yr",
    "pat_cagr_5yr",
    "eps_cagr_5yr",
    "free_cash_flow",
    "de_ratio",
    "interest_coverage"
]

for col in metrics:
    df[col + "_pct"] = df.groupby("peer_group")[col].rank(pct=True) * 100

print("\nData with Percentiles:")
print(df.head())

results = []

for metric in metrics:

    temp = df.copy()

    # invert DE ratio (lower is better)
    if metric == "de_ratio":
        temp["value"] = 1 / (temp[metric] + 1e-9)
    else:
        temp["value"] = temp[metric]

    temp["percentile"] = temp.groupby("peer_group")["value"].rank(pct=True)
    temp["metric"] = metric

    results.append(
        temp[["company_id", "peer_group", "metric", "value", "percentile", "year"]]
    )

final_df = pd.concat(results)

final_df.to_sql("peer_percentiles", conn, if_exists="replace", index=False)

print("\nPeer percentile table created!")
print(final_df.head())
print("\nFinal Peer Group Distribution:")
print(df["peer_group"].value_counts())