from fastapi import APIRouter
import pandas as pd
import numpy as np

router = APIRouter()


@router.get("/market-cap")
def market_cap():
    try:
        # Load data
        companies = pd.read_csv("data/processed/companies.csv")
        bs = pd.read_csv("data/processed/balance_sheet.csv")

        # Fix types
        companies["id"] = companies["id"].astype(str)
        bs["company_id"] = bs["company_id"].astype(str)

        # Latest year per company
        bs = bs.sort_values("year").drop_duplicates("company_id", keep="last")

        # Merge (SAFE)
        df = pd.merge(
            companies,
            bs,
            left_on="id",
            right_on="company_id",
            how="inner",
            suffixes=("", "_bs")   
        )

        if "id" not in df.columns:
            df["id"] = df["company_id"]

        # Compute market cap proxy
        if "book_value" in df.columns and "equity_capital" in df.columns:
            df["market_cap"] = pd.to_numeric(df["book_value"], errors="coerce") * \
                               pd.to_numeric(df["equity_capital"], errors="coerce")
        else:
            df["market_cap"] = None

        # Rank
        df["rank"] = df["market_cap"].rank(ascending=False, method="dense")

        # Select columns safely
        cols = ["id", "company_name", "market_cap", "rank"]
        cols = [c for c in cols if c in df.columns]

        result = df[cols]

        # Clean JSON
        result = result.replace([np.nan, np.inf, -np.inf], None)
        result = result.where(pd.notnull(result), None)

        return result.sort_values("rank").to_dict(orient="records")

    except Exception as e:
        return {"error": str(e)}