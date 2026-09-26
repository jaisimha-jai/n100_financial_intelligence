import streamlit as st
import pandas as pd
from utils.db import get_ratios


def run():

    st.title("Stock Screener")

    df = get_ratios().copy()

    if df.empty:
        st.warning("No data available")
        st.stop()

    # -----------------------------
    # CLEAN DATA
    # -----------------------------
    cols = [
        "roe", "de_ratio", "revenue_cagr_5yr",
        "pat_cagr_5yr", "pe_ratio", "pb_ratio",
        "div_yield", "icr", "net_profit"
    ]

    for col in cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df["roe"] = df.get("roe", 0).fillna(0)
    df["de_ratio"] = df.get("de_ratio", 0).fillna(0)
    df["sector"] = df.get("sector", "Unknown").fillna("Unknown")

    # -----------------------------
    # SIDEBAR FILTERS
    # -----------------------------
    st.sidebar.header("Filters")

    roe_min = st.sidebar.slider("Min ROE", 0, 50, 0)
    de_max = st.sidebar.slider("Max D/E", 0.0, 5.0, 5.0)
    rev_min = st.sidebar.slider("Min Revenue CAGR", -50, 50, 0)
    pat_min = st.sidebar.slider("Min PAT CAGR", -50, 50, 0)
    pe_max = st.sidebar.slider("Max P/E", 0, 100, 100)
    pb_max = st.sidebar.slider("Max P/B", 0, 20, 20)
    div_min = st.sidebar.slider("Min Dividend Yield", 0.0, 10.0, 0.0)
    icr_min = st.sidebar.slider("Min ICR", 0, 20, 0)

    # -----------------------------
    # PRESETS (IMPORTANT)
    # -----------------------------
    st.sidebar.subheader("Presets")

    if st.sidebar.button("Quality"):
        roe_min = 15
        de_max = 1

    if st.sidebar.button("Value"):
        pe_max = 20
        pb_max = 3

    if st.sidebar.button("Growth"):
        rev_min = 15
        pat_min = 15

    if st.sidebar.button("Debt-Free"):
        de_max = 0.1

    if st.sidebar.button("Dividend"):
        div_min = 3

    # -----------------------------
    # APPLY FILTERS
    # -----------------------------
    df_filtered = df.copy()

    df_filtered = df_filtered[df_filtered["roe"] >= roe_min]
    df_filtered = df_filtered[df_filtered["de_ratio"] <= de_max]

    if "revenue_cagr_5yr" in df_filtered.columns:
        df_filtered = df_filtered[df_filtered["revenue_cagr_5yr"] >= rev_min]

    if "pat_cagr_5yr" in df_filtered.columns:
        df_filtered = df_filtered[df_filtered["pat_cagr_5yr"] >= pat_min]

    if "pe_ratio" in df_filtered.columns:
        df_filtered = df_filtered[df_filtered["pe_ratio"] <= pe_max]

    if "pb_ratio" in df_filtered.columns:
        df_filtered = df_filtered[df_filtered["pb_ratio"] <= pb_max]

    if "div_yield" in df_filtered.columns:
        df_filtered = df_filtered[df_filtered["div_yield"] >= div_min]

    if "icr" in df_filtered.columns:
        df_filtered = df_filtered[df_filtered["icr"] >= icr_min]

    # -----------------------------
    # RESULT COUNT
    # -----------------------------
    st.subheader(f"{len(df_filtered)} Companies Match Your Filters")

    if df_filtered.empty:
        st.warning("No companies match the filters")
        st.stop()

    # -----------------------------
    # SCORE CALCULATION
    # -----------------------------
    score_df = df_filtered.copy()

    score_df["roe_score"] = score_df["roe"] / (score_df["roe"].max() + 1)
    score_df["de_score"] = 1 - (score_df["de_ratio"] / (score_df["de_ratio"].max() + 1))

    if "revenue_cagr_5yr" in score_df.columns:
        score_df["growth_score"] = score_df["revenue_cagr_5yr"] / (
            score_df["revenue_cagr_5yr"].max() + 1
        )
    else:
        score_df["growth_score"] = 0

    score_df["score"] = (
        0.4 * score_df["roe_score"] +
        0.3 * score_df["de_score"] +
        0.3 * score_df["growth_score"]
    )

    score_df["score"] = score_df["score"].fillna(0)

    # -----------------------------
    # DISPLAY TABLE
    # -----------------------------
    display_cols = [
        "company_name", "sector", "roe", "de_ratio",
        "revenue_cagr_5yr", "pat_cagr_5yr", "score"
    ]

    display_cols = [c for c in display_cols if c in score_df.columns]

    st.dataframe(
        score_df.sort_values("score", ascending=False)[display_cols]
    )

    # -----------------------------
    # CSV DOWNLOAD 
    # -----------------------------
    csv = score_df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Download CSV",
        data=csv,
        file_name="screener_results.csv",
        mime="text/csv"
    )