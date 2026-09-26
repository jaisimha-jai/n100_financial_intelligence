from fastapi import APIRouter
import pandas as pd
import os
import time

router = APIRouter()

START_TIME = time.time()

@router.get("/health")
def health():
    try:
        counts = {}

        files = {
            "companies": "data/processed/companies.csv",
            "ratios": "output/financial_ratios.csv",
            "clusters": "output/cluster_labels.csv"
        }

        for name, path in files.items():
            if os.path.exists(path):
                df = pd.read_csv(path)
                counts[name] = len(df)
            else:
                counts[name] = 0

        return {
            "status": "ok",
            "db_row_counts": counts,
            "uptime_seconds": int(time.time() - START_TIME),
            "version": "1.0"
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}