import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils.db import get_ratios


def run():

    st.title("Peer Comparison")

    df = get_ratios().copy()

    if df.empty:
        st.warning("No data available")
        st.stop()

    # -----------------------------
    # CLEAN DATA
    # -----------------------------
    cols = [
        "roe", "roce", "de_ratio",
        "revenue_cagr_5yr", "pat_cagr_5yr"
    ]

    for col in cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df["sector"] = df.get("sector", "Unknown").fillna("Unknown")

    # -----------------------------
    # SIDEBAR SELECTION
    # -----------------------------
    st.sidebar.header("Peer Filters")

    sectors = sorted(df["sector"].dropna().unique())

    selected_sector = st.sidebar.selectbox(
        "Select Sector",
        sectors
    )

    sector_df = df[df["sector"] == selected_sector]

    companies = sorted(sector_df["company_name"].dropna().unique())

    selected_company = st.sidebar.selectbox(
        "Select Company",
        companies
    )

    if sector_df.empty:
        st.warning("No companies in this sector")
        st.stop()

    # -----------------------------
    # SELECT DATA
    # -----------------------------
    latest_df = sector_df.sort_values("year").groupby("company_name").tail(1)

    company_row = latest_df[latest_df["company_name"] == selected_company]

    if company_row.empty:
        st.warning("Company not found")
        st.stop()

    # -----------------------------
    # METRICS FOR RADAR
    # -----------------------------
    metrics = [
        "roe",
        "roce",
        "de_ratio",
        "revenue_cagr_5yr",
        "pat_cagr_5yr"
    ]

    metrics = [m for m in metrics if m in latest_df.columns]

    # fill NaN
    latest_df[metrics] = latest_df[metrics].fillna(0)

    peer_avg = latest_df[metrics].mean()

    company_values = company_row[metrics].iloc[0]

    # -----------------------------
    # RADAR CHART
    # -----------------------------
    st.subheader(f"{selected_company} vs Sector Average")

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=company_values.values,
        theta=metrics,
        fill='toself',
        name=selected_company
    ))

    fig.add_trace(go.Scatterpolar(
        r=peer_avg.values,
        theta=metrics,
        fill='toself',
        name="Sector Avg"
    ))

    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True)),
        showlegend=True
    )

    st.plotly_chart(fig, width='stretch')

    # -----------------------------
    # COMPARISON TABLE
    # -----------------------------
    st.subheader("Peer Comparison Table")

    display_cols = ["company_name"] + metrics

    table_df = latest_df[display_cols].copy()

    # highlight selected company
    def highlight_row(row):
        if row["company_name"] == selected_company:
            return ['background-color: lightgreen'] * len(row)
        return [''] * len(row)

    st.dataframe(
        table_df.style.apply(highlight_row, axis=1),
        width='stretch'
    )