import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt


def run_clustering():

    df = pd.read_csv("data/processed/final_ratios.csv")

    # SELECT FEATURES
    features = [
        "roe",
        "debt_to_equity",
        "operating_profit_margin",
        "asset_turnover"
    ]

    df = df[["company_id"] + features]

    # HANDLE MISSING VALUES (median)
    df[features] = df[features].fillna(df[features].median())

    # SCALE DATA
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(df[features])

    # ELBOW METHOD
    inertia = []
    k_range = range(2, 10)

    for k in k_range:
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        kmeans.fit(scaled_data)
        inertia.append(kmeans.inertia_)

    # SAVE ELBOW PLOT
    plt.figure()
    plt.plot(k_range, inertia, marker="o")
    plt.xlabel("Number of clusters (k)")
    plt.ylabel("Inertia")
    plt.title("Elbow Method")
    plt.savefig("reports/elbow_plot.png")
    plt.close()

    # FINAL MODEL (k=5)
    kmeans = KMeans(n_clusters=5, random_state=42, n_init=10)
    df["cluster_id"] = kmeans.fit_predict(scaled_data)

    # DISTANCE FROM CENTROID
    distances = kmeans.transform(scaled_data)
    df["distance_from_centroid"] = distances.min(axis=1)

    # SIMPLE CLUSTER NAMES
    cluster_names = {
        0: "High Quality",
        1: "Growth",
        2: "Value",
        3: "Turnaround",
        4: "Stable"
    }

    df["cluster_name"] = df["cluster_id"].map(cluster_names)

    # SAVE OUTPUT
    output = df[[
        "company_id",
        "cluster_id",
        "cluster_name",
        "distance_from_centroid"
    ]]

    output.to_csv("data/processed/cluster_labels.csv", index=False)

    print("Clustering completed. cluster_labels.csv created")


if __name__ == "__main__":
    run_clustering()