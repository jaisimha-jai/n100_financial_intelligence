import sqlite3
import pandas as pd
import streamlit as st
import os


def enrich_data(df):
    if "roe_percentage" not in df.columns:
        df["roe_percentage"] = None
    return df


def add_sector_mapping(df):
    try:
        BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
        path = os.path.join(BASE_DIR, "data", "nifty100_sectors.csv")

        sector_map = pd.read_csv(path)

        df = df.merge(
            sector_map,
            on="company_name",
            how="left",
            suffixes=("", "_map")
        )

        df["sector"] = df["sector_map"].combine_first(df["sector"])
        df.drop(columns=["sector_map"], inplace=True)

    except:
        pass

    df["sector"] = df.get("sector", "Unknown").fillna("Unknown")
    return df


@st.cache_data(ttl=600)
def get_ratios():
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
    DB_PATH = os.path.join(BASE_DIR, "db", "nifty100.db")

    conn = sqlite3.connect(DB_PATH)

    df = pd.read_sql("""
        SELECT fr.*, c.company_name, c.sector
        FROM financial_ratios fr
        LEFT JOIN companies c
        ON fr.company_id = c.id
    """, conn)

    conn.close()

    df = enrich_data(df)
    df = add_sector_mapping(df)

    if "roe_percentage" in df.columns and not df["roe_percentage"].isnull().all():
        df["roe"] = df["roe_percentage"]
    else:
        df["roe"] = (df["net_profit"] / (df["net_profit"].abs().max() + 1)) * 100

    df["roe"] = df["roe"].fillna(0)

    if "de_ratio" not in df.columns:
        df["de_ratio"] = 0

    if "sector" not in df.columns:
        df["sector"] = "Unknown"

    df["sector"] = df["sector"].fillna("Unknown")

    return df