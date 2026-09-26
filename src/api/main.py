from fastapi import FastAPI
import pandas as pd
import time

from src.api.routers import companies, clusters, ratios, screener, sectors
from src.api.routers import portfolio
from src.api.routers import market_cap
from src.api.routers import documents

app = FastAPI()

start_time = time.time()

app.include_router(companies.router, prefix="/api/v1")
app.include_router(clusters.router, prefix="/api/v1")
app.include_router(ratios.router, prefix="/api/v1")
app.include_router(screener.router, prefix="/api/v1")
app.include_router(sectors.router, prefix="/api/v1")
app.include_router(portfolio.router, prefix="/api/v1")
app.include_router(market_cap.router, prefix="/api/v1")
app.include_router(documents.router, prefix="/api/v1")


@app.get("/api/v1/health")
def health():
    try:
        # Load datasets
        companies_df = pd.read_csv("data/processed/companies.csv")
        pl_df = pd.read_csv("data/processed/profit_loss.csv")
        bs_df = pd.read_csv("data/processed/balance_sheet.csv")
        cf_df = pd.read_csv("data/processed/cash_flow.csv")
        ratios_df = pd.read_csv("data/processed/ratios.csv")

        # Row counts
        counts = {
            "companies": len(companies_df),
            "profit_loss": len(pl_df),
            "balance_sheet": len(bs_df),
            "cash_flow": len(cf_df),
            "ratios": len(ratios_df)
        }

        # Uptime
        uptime = int(time.time() - start_time)

        return {
            "status": "ok",
            "db_row_counts": counts,
            "uptime_seconds": uptime,
            "version": "1.0"
        }

    except Exception as e:
        return {"error": str(e)}