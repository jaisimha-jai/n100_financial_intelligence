import streamlit as st
import pandas as pd
import plotly.express as px
from utils.db import get_ratios


def run():

    st.title("Capital Allocation Map")

    df = get_ratios().copy()

    if df.empty:
        st.warning("No data available")
        st.stop()

    # -----------------------------
    # CLEAN DATA
    # -----------------------------
    cols = [
        "roe", "de_ratio",
        "revenue_cagr_5yr", "pat_cagr_5yr",
        "market_cap"
    ]

    for col in cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df["roe"] = df.get("roe", 0).fillna(0)
    df["de_ratio"] = df.get("de_ratio", 0).fillna(0)
    df["revenue_cagr_5yr"] = df.get("revenue_cagr_5yr", 0).fillna(0)
    df["pat_cagr_5yr"] = df.get("pat_cagr_5yr", 0).fillna(0)

    df["sector"] = df.get("sector", "Unknown").fillna("Unknown")

    # -----------------------------
    # LATEST DATA PER COMPANY
    # -----------------------------
    df_latest = (
        df.sort_values("year")
        .groupby("company_name")
        .tail(1)
    )

    if df_latest.empty:
        st.warning("No data available")
        st.stop()

    # -----------------------------
    # CREATE PATTERNS
    # -----------------------------
    def classify(row):

        if row["revenue_cagr_5yr"] > 15:
            return "High Growth"

        elif row["roe"] > 15 and row["de_ratio"] < 1:
            return "Efficient"

        elif row["de_ratio"] > 2:
            return "Debt Heavy"

        elif row["pat_cagr_5yr"] > 15:
            return "Turnaround"

        else:
            return "Stable"

    df_latest["pattern"] = df_latest.apply(classify, axis=1)

    # fallback market cap
    if "market_cap" not in df_latest.columns:
        df_latest["market_cap"] = 1

    # -----------------------------
    # TREEMAP
    # -----------------------------
    st.subheader("Capital Allocation Treemap")

    fig = px.treemap(
        df_latest,
        path=["pattern", "company_name"],
        values="market_cap",
        color="pattern",
        title="Capital Allocation Patterns"
    )

    st.plotly_chart(fig, width="stretch")

    # -----------------------------
    # SHOW COMPANIES BY PATTERN
    # -----------------------------
    st.subheader("View Companies by Pattern")

    patterns = df_latest["pattern"].unique()

    selected_pattern = st.selectbox(
        "Select Pattern",
        patterns
    )

    filtered = df_latest[df_latest["pattern"] == selected_pattern]

    st.dataframe(
        filtered[
            [
                "company_name",
                "sector",
                "roe",
                "de_ratio",
                "revenue_cagr_5yr",
                "pat_cagr_5yr"
            ]
        ],
        width="stretch"
    )