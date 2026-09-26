import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np


def run_analysis():

    df = pd.read_csv("data/processed/final_ratios.csv")
    clusters = pd.read_csv("data/processed/cluster_labels.csv")

    # MERGE
    df["company_id"] = df["company_id"].astype(str)
    clusters["company_id"] = clusters["company_id"].astype(str)

    df = df.merge(clusters, on="company_id", how="inner")

    # =========================
    # 1. CLUSTER PROFILE
    # =========================
    features = [
        "roe",
        "debt_to_equity",
        "operating_profit_margin",
        "asset_turnover"
    ]

    profile = df.groupby("cluster_name")[features].agg(["mean", "median"])
    profile.to_csv("data/processed/cluster_profile.csv")

    print("Cluster profile saved")

    # =========================
    # 2. CORRELATION HEATMAP
    # =========================
    corr = df[features].corr()

    plt.figure(figsize=(8,6))
    sns.heatmap(corr, annot=True, cmap="coolwarm")
    plt.title("Correlation Heatmap")

    plt.savefig("reports/correlation_heatmap.png")
    plt.close()

    print("Heatmap saved")

    # =========================
    # 3. OUTLIER DETECTION (Z-score)
    # =========================
    outliers = []

    for col in features:
        mean = df[col].mean()
        std = df[col].std()

        df["z"] = (df[col] - mean) / std

        temp = df[np.abs(df["z"]) > 3][["company_id", col, "z"]]
        temp["metric"] = col

        outliers.append(temp)

    outlier_df = pd.concat(outliers, ignore_index=True)
    outlier_df.to_csv("data/processed/outliers.csv", index=False)

    print("Outliers saved")

    # =========================
    # 4. PORTFOLIO STATS
    # =========================
    stats = {}

    for col in features:
        stats[col] = {
            "P10": df[col].quantile(0.10),
            "P25": df[col].quantile(0.25),
            "P50": df[col].quantile(0.50),
            "P75": df[col].quantile(0.75),
            "P90": df[col].quantile(0.90),
            "Mean": df[col].mean(),
            "Std": df[col].std()
        }

    stats_df = pd.DataFrame(stats).T
    stats_df.to_csv("data/processed/portfolio_stats.csv")

    print("Portfolio stats saved")


if __name__ == "__main__":
    run_analysis()