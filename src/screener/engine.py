import pandas as pd
import sqlite3


conn = sqlite3.connect("db/nifty100.db")
df = pd.read_sql("SELECT * FROM financial_ratios", conn)
print("Loaded data:", df.shape)
companies = pd.read_sql("SELECT id as company_id, company_name FROM companies", conn)
df = df.merge(companies, on="company_id", how="left")

# FILTER ENGINE

def apply_filters(df, config):
    
    if config.get("roe_min"):
        df = df[df["roe"] >= config["roe_min"]]

    if config.get("de_max"):
        df = df[df["de_ratio"] <= config["de_max"]]

    if config.get("revenue_cagr_min"):
        df = df[df["revenue_cagr_5yr"] >= config["revenue_cagr_min"]]

    if config.get("pat_cagr_min"):
        df = df[df["pat_cagr_5yr"] >= config["pat_cagr_min"]]

    if config.get("fcf_positive"):
        df = df[df["free_cash_flow"] > 0]

    if config.get("icr_min"):
        df = df[df["interest_coverage"] >= config["icr_min"]]

    if config.get("eps_cagr_min"):
        df = df[df["eps_cagr_5yr"] >= config["eps_cagr_min"]]

    return df

config = {
    "de_max": 2,
    "revenue_cagr_min": 5,
    "pat_cagr_min": 5,
    "fcf_positive": True
}

result = apply_filters(df, config)
print("Filtered:", result.shape)
print(result.head())

# -----------------------------
# PRESET SCREENERS
# -----------------------------

def quality_compounder(df):
    config = {
        "de_max": 1,
        "revenue_cagr_min": 10,
        "pat_cagr_min": 10,
        "fcf_positive": True
    }
    return apply_filters(df, config)


def value_pick(df):
    config = {
        "de_max": 2,
        "fcf_positive": True
    }
    return apply_filters(df, config)


def growth_accelerator(df):
    config = {
        "revenue_cagr_min": 15,
        "pat_cagr_min": 20
    }
    return apply_filters(df, config)


def dividend_champion(df):
    config = {
        "fcf_positive": True
    }
    return apply_filters(df, config)


def debt_free_bluechip(df):
    df = df[df["de_ratio"] == 0]
    return df


def turnaround_watch(df):
    df = df[df["revenue_cagr_5yr"] > 10]
    return df

print("\n--- QUALITY COMPOUNDER ---")
print(quality_compounder(df).shape)
print("\n--- VALUE PICK ---")
print(value_pick(df).shape)
print("\n--- GROWTH ACCELERATOR ---")
print(growth_accelerator(df).shape)
print("\n--- DIVIDEND CHAMPION ---")
print(dividend_champion(df).shape)
print("\n--- DEBT FREE ---")
print(debt_free_bluechip(df).shape)
print("\n--- TURNAROUND ---")
print(turnaround_watch(df).shape)

# -----------------------------
# COMPOSITE SCORE
# -----------------------------
def compute_score(df):

    df = df.copy()

    def scale(series):
        if not isinstance(series, pd.Series):
            return pd.Series([0]*len(df))   # safe fallback
        
        return 100 * (series - series.min()) / (series.max() - series.min() + 1e-9)

    

    # PROFITABILITY
    npm_score = scale(df["net_profit"])

    # CASH
    fcf_score = scale(df["free_cash_flow"])
    cfo_score = scale(df["cfo_quality_score"])

    # GROWTH
    rev_score = scale(df["revenue_cagr_5yr"])
    pat_score = scale(df["pat_cagr_5yr"])

    # LEVERAGE
    de_score = 100 - scale(df["de_ratio"])
    icr_score = scale(df["interest_coverage"])

    df["composite_score"] = (
        0.35 * npm_score +
        0.30 * (0.6 * fcf_score + 0.4 * cfo_score) +
        0.20 * (0.5 * rev_score + 0.5 * pat_score) +
        0.15 * (0.5 * de_score + 0.5 * icr_score)
    )

    return df

qc = compute_score(quality_compounder(df))
vp = compute_score(value_pick(df))
ga = compute_score(growth_accelerator(df))
dc = compute_score(dividend_champion(df))
db = compute_score(debt_free_bluechip(df))
tw = compute_score(turnaround_watch(df))

# sort
qc = qc.sort_values("composite_score", ascending=False)
vp = vp.sort_values("composite_score", ascending=False)
ga = ga.sort_values("composite_score", ascending=False)
dc = dc.sort_values("composite_score", ascending=False)
db = db.sort_values("composite_score", ascending=False)
tw = tw.sort_values("composite_score", ascending=False)

print(qc[["company_id", "composite_score"]].head())

# EXPORT TO EXCEL
with pd.ExcelWriter("output/screener_output.xlsx") as writer:
    qc.to_excel(writer, sheet_name="Quality", index=False)
    vp.to_excel(writer, sheet_name="Value", index=False)
    ga.to_excel(writer, sheet_name="Growth", index=False)
    dc.to_excel(writer, sheet_name="Dividend", index=False)
    db.to_excel(writer, sheet_name="DebtFree", index=False)
    tw.to_excel(writer, sheet_name="Turnaround", index=False)

# -----------------------------
# DAY 21 VALIDATION
# -----------------------------

print("\n--- VALIDATION: SCREENER ---")
qc = quality_compounder(df)
print(qc[["company_id", "de_ratio", "revenue_cagr_5yr"]].head())


print("\n--- VALIDATION: PEER ---")
test = df.sort_values("net_profit", ascending=False)
print(test[["company_id", "net_profit"]].head())

peer = pd.read_sql("SELECT * FROM peer_percentiles", conn)
print(peer[peer["metric"] == "net_profit"]
      .sort_values("percentile", ascending=False)
      .head())

print("Excel file generated!")
print(df.columns)