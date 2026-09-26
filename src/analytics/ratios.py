from fastapi import APIRouter, HTTPException
import pandas as pd
import numpy as np

router = APIRouter()


@router.get("/companies/{ticker}/ratios")
def get_ratios(ticker: str, year: int = None):
    try:
        # Load data
        df = pd.read_csv("data/processed/ratios.csv")

        # Ensure correct types
        df["company_id"] = df["company_id"].astype(str)

        # Filter by company
        df = df[df["company_id"] == ticker]

        if df.empty:
            raise HTTPException(status_code=404, detail="No ratio data found")

        # Optional year filter
        if year is not None:
            df = df[df["year"] == year]

        # Select important columns only
        cols = [
            "company_id",
            "year",
            "revenue",
            "roe",
            "debt_to_equity",
            "operating_profit_margin",
            "asset_turnover"
        ]

        cols = [c for c in cols if c in df.columns]
        df = df[cols]

        df = df.replace([np.nan, np.inf, -np.inf], None)
        df = df.where(pd.notnull(df), None)

        return df.to_dict(orient="records")

    except Exception as e:
        return {"error": str(e)}