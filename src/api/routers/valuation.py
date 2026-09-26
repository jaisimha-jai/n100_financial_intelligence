from fastapi import APIRouter
import pandas as pd

router = APIRouter()

@router.get("/market-cap/{company_id}")
def get_valuation(company_id: str):
    try:
        df = pd.read_csv("data/processed/market_cap.csv")

        df["company_id"] = df["company_id"].astype(str)

        df = df[df["company_id"] == company_id]

        if df.empty:
            return {"error": "Company not found"}

        return df.to_dict(orient="records")

    except Exception as e:
        return {"error": str(e)}