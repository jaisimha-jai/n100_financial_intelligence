from fastapi import APIRouter
import pandas as pd
import numpy as np

router = APIRouter()

@router.get("/peers/{group_name}")
def get_peers(group_name: str):
    try:
        peers = pd.read_csv("data/processed/peer_groups.csv")
        companies = pd.read_csv("data/processed/companies.csv")
        ratios = pd.read_csv("data/processed/financial_ratios.csv")

        peers = peers[peers["group_name"].str.lower() == group_name.lower()]

        if peers.empty:
            return {"error": "Peer group not found"}

        companies["company_id"] = companies["id"].astype(str)
        ratios["company_id"] = ratios["company_id"].astype(str)

        ratios = ratios.sort_values("year").groupby("company_id").tail(1)

        df = pd.merge(peers, companies, on="company_id")
        df = pd.merge(df, ratios, on="company_id", how="left")

        df = df.replace([np.inf, -np.inf], np.nan).fillna(0)

        return df.to_dict(orient="records")

    except Exception as e:
        return {"error": str(e)}