from fastapi import APIRouter
import pandas as pd
import numpy as np

router = APIRouter()

def clean(df):
    return df.replace([np.inf, -np.inf], np.nan).fillna("")

@router.get("/companies/{ticker}/ratios")
def company_ratios(ticker: str):
    try:
        df = pd.read_csv("data/processed/financial_ratios.csv")
        df = clean(df)

        if "company_id" not in df.columns:
            return {"error": "company_id missing"}

        result = df[df["company_id"] == ticker]

        return result.to_dict(orient="records")

    except Exception as e:
        return {"error": str(e)}