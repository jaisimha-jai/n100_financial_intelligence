from fastapi import APIRouter, HTTPException
import pandas as pd
import numpy as np

router = APIRouter()


@router.get("/documents/{ticker}")
def get_documents(ticker: str):
    try:
        df = pd.read_csv("data/processed/companies.csv")

        # Ensure string type
        df["id"] = df["id"].astype(str)

        # Filter company
        result = df[df["id"] == ticker]

        if result.empty:
            raise HTTPException(status_code=404, detail="Company not found")

        row = result.iloc[0]

        # Build response
        data = {
            "company_id": row.get("id"),
            "company_name": row.get("company_name"),
            "website": row.get("website"),
            "nse_profile": row.get("nse_profile"),
            "bse_profile": row.get("bse_profile"),
            "chart_link": row.get("chart_link"),
            "about_company": row.get("about_company")
        }

        # Clean JSON
        data = {
            k: (None if pd.isna(v) else v)
            for k, v in data.items()
        }

        return data

    except Exception as e:
        return {"error": str(e)}