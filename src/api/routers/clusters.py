from fastapi import APIRouter
import pandas as pd
import numpy as np

router = APIRouter()


# GET ALL CLUSTERS
@router.get("/clusters")
def get_clusters():
    try:
        df = pd.read_csv("output/cluster_labels.csv")

        # Select required columns only
        cols = ["company_id", "cluster_id", "cluster_name"]
        cols = [c for c in cols if c in df.columns]
        df = df[cols]

        df = df.replace([np.nan, np.inf, -np.inf], None)
        df = df.where(pd.notnull(df), None)

        return df.to_dict(orient="records")

    except Exception as e:
        return {"error": str(e)}


# GET CLUSTER PROFILE (ADVANCED)
@router.get("/clusters/profile")
def cluster_profile():
    try:
        df = pd.read_csv("output/cluster_labels.csv")

        # Select numeric columns
        numeric_cols = df.select_dtypes(include=["float64", "int64"]).columns

        # Group by cluster
        profile = df.groupby("cluster_name")[numeric_cols].mean().reset_index()

        profile = profile.replace([np.nan, np.inf, -np.inf], None)
        profile = profile.where(pd.notnull(profile), None)

        return profile.to_dict(orient="records")

    except Exception as e:
        return {"error": str(e)}