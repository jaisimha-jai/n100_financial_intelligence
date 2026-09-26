import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils.db import get_ratios


def run():

    st.title("Company Profile")

    df = get_ratios().copy()

    if df.empty:
        st.warning("No data available")
        st.stop()

    # -----------------------------
    # CLEAN DATA
    # -----------------------------
    cols = [
        "roe", "roce", "de_ratio",
        "revenue", "net_profit",
        "revenue_cagr_5yr", "pat_cagr_5yr"
    ]

    for col in cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df["sector"] = df.get("sector", "Unknown").fillna("Unknown")

    # -----------------------------
    # SEARCH BOX
    # -----------------------------
    st.sidebar.header("Search Company")

    companies = sorted(df["company_name"].dropna().unique())

    selected = st.sidebar.selectbox(
        "Select Company",
        ["None"] + companies
    )

    if selected == "None":
        st.info("Please select a company")
        st.stop()

    comp_df = df[df["company_name"] == selected].sort_values("year")

    if comp_df.empty:
        st.warning("Ticker not found — please try another")
        st.stop()

    st.subheader(selected)

    # -----------------------------
    # KPI CARDS
    # -----------------------------
    latest = comp_df.sort_values("year", ascending=False).iloc[0]

    c1, c2, c3, c4, c5, c6 = st.columns(6)

    c1.metric("ROE", round(latest.get("roe", 0), 2))
    c2.metric("ROCE", round(latest.get("roce", 0), 2))
    c3.metric("D/E", round(latest.get("de_ratio", 0), 2))
    c4.metric("Revenue CAGR", round(latest.get("revenue_cagr_5yr", 0), 2))
    c5.metric("PAT CAGR", round(latest.get("pat_cagr_5yr", 0), 2))
    c6.metric("Sector", latest.get("sector", "N/A"))

    # -----------------------------
    # REVENUE & PROFIT BAR CHART
    # -----------------------------
    st.subheader("Revenue & Profit (10 Years)")

    if "year" in comp_df.columns:

        fig_bar = go.Figure()

        if "revenue" in comp_df.columns:
            fig_bar.add_bar(
                x=comp_df["year"],
                y=comp_df["revenue"],
                name="Revenue"
            )

        if "net_profit" in comp_df.columns:
            fig_bar.add_bar(
                x=comp_df["year"],
                y=comp_df["net_profit"],
                name="Net Profit"
            )

        fig_bar.update_layout(
            barmode="group",
            xaxis_title="Year",
            yaxis_title="Amount"
        )

        st.plotly_chart(fig_bar, width='stretch')

    # -----------------------------
    # 🔥 DUAL AXIS ROE vs ROCE
    # -----------------------------
    st.subheader("ROE vs ROCE (Trend)")

    fig = go.Figure()

    # ROE Line
    if "roe" in comp_df.columns:
        fig.add_trace(go.Scatter(
            x=comp_df["year"],
            y=comp_df["roe"],
            mode='lines+markers',
            name='ROE',
            yaxis='y1'
        ))

    # ROCE Line (SECOND AXIS)
    if "roce" in comp_df.columns:
        fig.add_trace(go.Scatter(
            x=comp_df["year"],
            y=comp_df["roce"],
            mode='lines+markers',
            name='ROCE',
            yaxis='y2'
        ))

    fig.update_layout(
        xaxis=dict(title="Year"),
        yaxis=dict(
            title="ROE",
            side="left"
        ),
        yaxis2=dict(
            title="ROCE",
            overlaying="y",
            side="right"
        ),
        legend=dict(x=0, y=1.1, orientation="h")
    )

    st.plotly_chart(fig, width='stretch')

    # -----------------------------
    # RAW DATA TABLE
    # -----------------------------
    st.subheader("Financial Data")

    st.dataframe(comp_df.sort_values("year", ascending=False))