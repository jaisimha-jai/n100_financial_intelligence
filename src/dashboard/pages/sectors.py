import streamlit as st
import pandas as pd
import plotly.express as px
from utils.db import get_ratios


def run():

    st.title("Sector Analysis")

    df = get_ratios().copy()

    if df.empty:
        st.warning("No data available")
        st.stop()

    # -----------------------------
    # CLEAN DATA
    # -----------------------------
    cols = [
        "revenue",
        "roe",
        "market_cap",
        "de_ratio",
        "revenue_cagr_5yr",
        "pat_cagr_5yr"
    ]

    for col in cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df["sector"] = df.get("sector", "Unknown").fillna("Unknown")

    # -----------------------------
    # SIDEBAR FILTER
    # -----------------------------
    st.sidebar.header("Sector Filter")

    sectors = sorted(df["sector"].dropna().unique())

    selected_sector = st.sidebar.selectbox(
        "Select Sector",
        ["All"] + sectors
    )

    if selected_sector != "All":
        df = df[df["sector"] == selected_sector]

    # latest year per company
    df_latest = (
        df.sort_values("year")
        .groupby("company_name")
        .tail(1)
    )

    if df_latest.empty:
        st.warning("No data available")
        st.stop()

    # -----------------------------
    # BUBBLE CHART
    # -----------------------------
    st.subheader("Revenue vs ROE (Bubble Chart)")

    # fallback if missing columns
    if "revenue" not in df_latest.columns:
        df_latest["revenue"] = 0

    if "market_cap" not in df_latest.columns:
        df_latest["market_cap"] = 1

    fig = px.scatter(
        df_latest,
        x="revenue",
        y="roe",
        size="market_cap",
        color="sector",
        hover_name="company_name",
        title="Revenue vs ROE",
    )

    st.plotly_chart(fig, width="stretch")

    # -----------------------------
    # SECTOR KPI BAR CHART
    # -----------------------------
    st.subheader("Sector Median KPIs")

    sector_kpi = (
        df_latest.groupby("sector")[
            ["roe", "de_ratio", "revenue_cagr_5yr"]
        ]
        .median()
        .reset_index()
    )

    sector_kpi_melt = sector_kpi.melt(
        id_vars="sector",
        var_name="metric",
        value_name="value"
    )

    fig_bar = px.bar(
        sector_kpi_melt,
        x="sector",
        y="value",
        color="metric",
        barmode="group",
        title="Sector Median Comparison"
    )

    st.plotly_chart(fig_bar, width="stretch")