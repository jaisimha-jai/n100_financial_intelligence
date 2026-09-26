import streamlit as st
import pandas as pd
import plotly.express as px
from utils.db import get_ratios


def safe_median(series):
    if series is None or series.isnull().all():
        return "N/A"
    return round(series.median(), 2)


def run():

    st.title("Nifty 100 Dashboard")

    df = get_ratios().copy()

    if df.empty:
        st.warning("No data available")
        st.stop()

    # -----------------------------
    # CLEAN DATA
    # -----------------------------
    cols = [
        "roe", "de_ratio", "revenue_cagr_5yr",
        "pat_cagr_5yr", "net_profit", "pe_ratio"
    ]

    for col in cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df["roe"] = df.get("roe", 0).fillna(0)
    df["de_ratio"] = df.get("de_ratio", 0).fillna(0)
    df["sector"] = df.get("sector", "Unknown").fillna("Unknown")

    # -----------------------------
    # SIDEBAR FILTER
    # -----------------------------
    st.sidebar.header("Filters")

    years = sorted(df["year"].dropna().astype(str).unique(), reverse=True)
    year = st.sidebar.selectbox("Select Year", ["All"] + years)

    if year != "All":
        df = df[df["year"].astype(str) == year]

    if df.empty:
        st.warning("No data after filter")
        st.stop()

    # -----------------------------
    # KPI SECTION
    # -----------------------------
    c1, c2, c3, c4, c5, c6 = st.columns(6)

    c1.metric("Avg ROE", round(df["roe"].mean(), 2))

    # FIXED P/E
    if "pe_ratio" in df.columns:
        pe_val = safe_median(df["pe_ratio"])
    else:
        pe_val = "N/A"

    c2.metric("Median P/E", pe_val)

    c3.metric("Median D/E", safe_median(df["de_ratio"]))
    c4.metric("Companies", df["company_name"].nunique())
    c5.metric("Median Rev CAGR", safe_median(df["revenue_cagr_5yr"]))
    c6.metric("Debt-Free", int((df["de_ratio"] < 0.1).sum()))

    # -----------------------------
    # ROW 1 → HISTOGRAM + BAR
    # -----------------------------
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("ROE Distribution")

        hist_df = df[df["roe"] < 50]

        fig_hist = px.histogram(
            hist_df,
            x="roe",
            nbins=30,
            title="ROE Distribution"
        )

        st.plotly_chart(fig_hist, width='stretch')

    with col2:
        st.subheader("Top Revenue Growth Companies")

        if "revenue_cagr_5yr" in df.columns:

            top_rev = (
                df.sort_values("revenue_cagr_5yr", ascending=False)
                .drop_duplicates("company_name")
                .head(10)
            )

            fig_bar = px.bar(
                top_rev,
                x="revenue_cagr_5yr",
                y="company_name",
                orientation="h",
                title="Top 10 Revenue Growth"
            )

            fig_bar.update_layout(yaxis={'categoryorder': 'total ascending'})

            st.plotly_chart(fig_bar, width='stretch')
        else:
            st.info("Revenue CAGR data not available")

    # -----------------------------
    # ROW 2 → PIE
    # -----------------------------
    st.subheader("Sector Distribution")

    sector_counts = df["sector"].value_counts().reset_index()
    sector_counts.columns = ["sector", "count"]

    fig_pie = px.pie(
        sector_counts,
        names="sector",
        values="count",
        hole=0.5
    )

    st.plotly_chart(fig_pie, width='stretch')

    # -----------------------------
    # TOP QUALITY COMPANIES
    # -----------------------------
    st.subheader("Top Quality Companies")

    score_df = df.copy()

    score_df["roe_score"] = score_df["roe"] / (score_df["roe"].max() + 1)
    score_df["de_score"] = 1 - (
        score_df["de_ratio"] / (score_df["de_ratio"].max() + 1)
    )
    score_df["growth_score"] = (
        score_df["revenue_cagr_5yr"] /
        (score_df["revenue_cagr_5yr"].max() + 1)
    )

    score_df["total_score"] = (
        0.4 * score_df["roe_score"]
        + 0.3 * score_df["de_score"]
        + 0.3 * score_df["growth_score"]
    )

    score_df["total_score"] = score_df["total_score"].fillna(0)

    top_quality = (
        score_df.sort_values("total_score", ascending=False)
        .drop_duplicates("company_name")
        .head(10)
    )

    st.dataframe(
        top_quality[
            [
                "company_name",
                "sector",
                "roe",
                "de_ratio",
                "revenue_cagr_5yr",
                "total_score"
            ]
        ]
    )