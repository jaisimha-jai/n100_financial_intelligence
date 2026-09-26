from fastapi import APIRouter
import pandas as pd
import numpy as np

router = APIRouter()


@router.get("/portfolio/stats")
def portfolio_stats():
    try:
        df = pd.read_csv("data/processed/ratios.csv")

        kpis = [
            "roe",
            "debt_to_equity",
            "operating_profit_margin",
            "asset_turnover",
            "revenue"
        ]

        kpis = [k for k in kpis if k in df.columns]

        stats = []

        for col in kpis:
            series = pd.to_numeric(df[col], errors="coerce")

            stat = {
                "metric": col,
                "P10": series.quantile(0.10),
                "P25": series.quantile(0.25),
                "P50": series.quantile(0.50),
                "P75": series.quantile(0.75),
                "P90": series.quantile(0.90),
                "mean": series.mean(),
                "std": series.std()
            }

            stats.append(stat)

        result = pd.DataFrame(stats)

        result = result.replace([np.nan, np.inf, -np.inf], None)
        result = result.where(pd.notnull(result), None)

        return result.to_dict(orient="records")

    except Exception as e:
        return {"error": str(e)}