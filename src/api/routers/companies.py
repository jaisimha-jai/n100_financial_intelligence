from fastapi import APIRouter, HTTPException
import pandas as pd

router = APIRouter()


# GET ALL COMPANIES
@router.get("/companies")
def get_companies():
    try:
        df = pd.read_csv("data/processed/companies.csv")
        df = df.fillna("")
        return df.to_dict(orient="records")
    except Exception as e:
        return {"error": str(e)}


# GET COMPANY PROFILE
@router.get("/companies/{ticker}")
def get_company(ticker: str):
    try:
        df = pd.read_csv("data/processed/companies.csv")
        df["id"] = df["id"].astype(str)

        result = df[df["id"] == ticker]

        if result.empty:
            raise HTTPException(status_code=404, detail="Company not found")

        return result.fillna("").to_dict(orient="records")[0]

    except Exception as e:
        return {"error": str(e)}


# PROFIT & LOSS
@router.get("/companies/{ticker}/pl")
def get_pl(ticker: str):
    try:
        df = pd.read_csv("data/processed/profit_loss.csv")
        df["company_id"] = df["company_id"].astype(str)

        result = df[df["company_id"] == ticker]

        if result.empty:
            raise HTTPException(status_code=404, detail="No PL data")

        return result.fillna(0).to_dict(orient="records")

    except Exception as e:
        return {"error": str(e)}


# BALANCE SHEET
@router.get("/companies/{ticker}/bs")
def get_bs(ticker: str):
    try:
        df = pd.read_csv("data/processed/balance_sheet.csv")
        df["company_id"] = df["company_id"].astype(str)

        result = df[df["company_id"] == ticker]

        if result.empty:
            raise HTTPException(status_code=404, detail="No BS data")

        return result.fillna(0).to_dict(orient="records")

    except Exception as e:
        return {"error": str(e)}


# CASH FLOW
@router.get("/companies/{ticker}/cashflow")
def get_cf(ticker: str):
    try:
        df = pd.read_csv("data/processed/cash_flow.csv")
        df["company_id"] = df["company_id"].astype(str)

        result = df[df["company_id"] == ticker]

        if result.empty:
            raise HTTPException(status_code=404, detail="No Cashflow data")

        return result.fillna(0).to_dict(orient="records")

    except Exception as e:
        return {"error": str(e)}