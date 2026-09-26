from fastapi import APIRouter, HTTPException
import pandas as pd
import numpy as np

router = APIRouter()


@router.get("/screener")
def screener(
    min_roe: float = None,
    max_de: float = None,
):
    try:
        # Load data
        ratios = pd.read_csv("data/processed/ratios.csv")
        companies = pd.read_csv("data/processed/companies.csv")

        ratios = ratios.loc[:, ~ratios.columns.duplicated()]

        df = pd.merge(
            ratios,
            companies,
            left_on="company_id",
            right_on="id",
            how="left"
        )

        if "roe" not in df.columns:
            df["roe"] = df.get("roe_percentage", 0)

        if "debt_to_equity" not in df.columns:
            df["debt_to_equity"] = 0

        df["roe"] = pd.to_numeric(df["roe"], errors="coerce")
        df["debt_to_equity"] = pd.to_numeric(df["debt_to_equity"], errors="coerce")

        if min_roe is not None:
            df = df[df["roe"] >= min_roe]

        if max_de is not None:
            df = df[df["debt_to_equity"] <= max_de]

        cols = [
            "company_id",
            "company_name",
            "roe",
            "debt_to_equity"
        ]

        cols = [c for c in cols if c in df.columns]
        df = df[cols]

        df = df.replace([np.nan, np.inf, -np.inf], None)

        return df.to_dict(orient="records")

    except Exception as e:
        return {"error": str(e)}