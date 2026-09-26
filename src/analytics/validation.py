import pandas as pd
import sqlite3

conn = sqlite3.connect("db/nifty100.db")

df = pd.read_sql("SELECT * FROM financial_ratios", conn)
issues_df = []

for col in df.columns:
    missing = df[col].isnull().sum()
    if missing > 0:
        issues_df.append({"issue": "Missing values", "column": col, "count": missing})

if (df["net_profit"] < 0).any():
    issues_df.append({"issue": "Negative values", "column": "net_profit"})

if df.duplicated().any():
    issues_df.append({"issue": "Duplicate rows", "column": "ALL"})

# save
pd.DataFrame(issues_df).to_csv("output/validation_issues.csv", index=False)