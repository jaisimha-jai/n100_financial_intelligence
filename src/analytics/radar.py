import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import numpy as np
import os

# DB connection
conn = sqlite3.connect("db/nifty100.db")

# Load data
df = pd.read_sql("SELECT * FROM financial_ratios", conn)

# Choose metrics (adjust based on your columns)
metrics = [
    "roe_percentage",
    "roce_percentage",
    "net_profit",
    "de_ratio",
    "free_cash_flow",
    "pat_cagr_5yr",
    "revenue_cagr_5yr"
]

os.makedirs("reports/radar_charts", exist_ok=True)

def normalize(series):
    return 100 * (series - series.min()) / (series.max() - series.min() + 1e-9)

# normalize all metrics
for col in metrics:
    if col in df.columns:
        df[col] = normalize(df[col])
    else:
        df[col] = 0

companies = df["company_id"].unique()

for company in companies:

    company_df = df[df["company_id"] == company]
    
    # take latest row (important)
    company_row = company_df.iloc[-1]

    values = [company_row[m] for m in metrics]

    # peer avg (simple global avg for now)
    peer_avg = df[metrics].mean().values

    # angles
    angles = np.linspace(0, 2*np.pi, len(metrics), endpoint=False).tolist()
    
    values += values[:1]
    peer_avg = np.append(peer_avg, peer_avg[0])
    angles += angles[:1]

    # plot
    plt.figure(figsize=(6,6))
    ax = plt.subplot(111, polar=True)

    # company
    ax.plot(angles, values, linewidth=2)
    ax.fill(angles, values, alpha=0.25)

    # peer avg
    ax.plot(angles, peer_avg, linestyle='dashed')

    # labels
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(metrics)

    ax.set_title(company)
   # save
    plt.savefig(f"reports/radar_charts/{company}_radar.png")
    plt.close()

print("Radar charts generated")