from fastapi import APIRouter
import pandas as pd
import numpy as np

router = APIRouter()


# GET ALL SECTORS
@router.get("/sectors")
def get_sectors():
    try:
        df = pd.read_csv("data/processed/companies.csv")

        if "broad_sector" not in df.columns:
            df["broad_sector"] = "Unknown"

        df["broad_sector"] = df["broad_sector"].fillna("Unknown")

        result = df.groupby("broad_sector").size().reset_index(name="company_count")

        result = result.replace([np.nan, np.inf, -np.inf], None)

        return result.to_dict(orient="records")

    except Exception as e:
        return {"error": str(e)}


@router.get("/sectors/{sector}/companies")
def get_companies_by_sector(sector: str):
    try:
        df = pd.read_csv("data/processed/companies.csv")

        if "broad_sector" not in df.columns:
            df["broad_sector"] = "Unknown"

        df["broad_sector"] = df["broad_sector"].fillna("Unknown")

        result = df[df["broad_sector"].str.lower() == sector.lower()]

        if result.empty:
            return {"message": "No companies found for this sector"}

        result = result.replace([np.nan, np.inf, -np.inf], None)

        return result.to_dict(orient="records")

    except Exception as e:
        return {"error": str(e)}