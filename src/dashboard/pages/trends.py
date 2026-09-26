import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils.db import get_ratios


def run():

    st.title("Trend Analysis")

    df = get_ratios().copy()

    if df.empty:
        st.warning("No data available")
        st.stop()

    # -----------------------------
    # CLEAN DATA
    # -----------------------------
    metrics_all = [
        "revenue",
        "net_profit",
        "roe",
        "roce",
        "de_ratio",
        "revenue_cagr_5yr",
        "pat_cagr_5yr"
    ]

    for col in metrics_all:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # -----------------------------
    # SIDEBAR
    # -----------------------------
    st.sidebar.header("Trend Filters")

    companies = sorted(df["company_name"].dropna().unique())

    selected_company = st.sidebar.selectbox(
        "Select Company",
        companies
    )

    available_metrics = [m for m in metrics_all if m in df.columns]

    selected_metrics = st.sidebar.multiselect(
        "Select Metrics (max 3)",
        available_metrics,
        default=available_metrics[:2]
    )

    if len(selected_metrics) == 0:
        st.warning("Select at least 1 metric")
        st.stop()

    if len(selected_metrics) > 3:
        st.warning("Select maximum 3 metrics only")
        st.stop()

    # -----------------------------
    # FILTER COMPANY DATA
    # -----------------------------
    comp_df = df[df["company_name"] == selected_company].sort_values("year")

    if comp_df.empty:
        st.warning("No data for this company")
        st.stop()

    st.subheader(f"{selected_company} - Trends")

    # -----------------------------
    # LINE CHART
    # -----------------------------
    fig = go.Figure()

    for metric in selected_metrics:

        fig.add_trace(go.Scatter(
            x=comp_df["year"],
            y=comp_df[metric],
            mode="lines+markers",
            name=metric
        ))

    fig.update_layout(
        xaxis_title="Year",
        yaxis_title="Value",
        legend=dict(orientation="h", y=1.1)
    )

    st.plotly_chart(fig, width='stretch')

    # -----------------------------
    # YOY % CHANGE TABLE
    # -----------------------------
    st.subheader("YoY Growth (%)")

    yoy_df = comp_df[["year"] + selected_metrics].copy()

    for metric in selected_metrics:
        yoy_df[metric + "_YoY%"] = yoy_df[metric].pct_change() * 100

    yoy_df = yoy_df.round(2)

    st.dataframe(yoy_df, width='stretch')