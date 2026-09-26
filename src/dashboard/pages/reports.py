import streamlit as st
import pandas as pd
from utils.db import get_ratios


def run():

    st.title("Annual Reports")

    df = get_ratios().copy()

    if df.empty:
        st.warning("No data available")
        st.stop()

    # -----------------------------
    # SIDEBAR SEARCH
    # -----------------------------
    st.sidebar.header("Search Company")

    companies = sorted(df["company_name"].dropna().unique())

    selected_company = st.sidebar.selectbox(
        "Select Company",
        companies
    )

    # -----------------------------
    # FILTER COMPANY DATA
    # -----------------------------
    comp_df = df[df["company_name"] == selected_company]

    if comp_df.empty:
        st.warning("No data found")
        st.stop()

    # -----------------------------
    # YEARS AVAILABLE
    # -----------------------------
    years = sorted(comp_df["year"].dropna().astype(int).unique(), reverse=True)

    st.subheader(f"{selected_company} - Reports")

    # -----------------------------
    # SHOW REPORT LINKS
    # -----------------------------
    for year in years:

        # 🔹 FAKE LINK (for demo purpose)
        fake_url = f"https://www.bseindia.com/xml-data/corpfiling/AttachHis/{selected_company}_{year}.pdf"

        col1, col2 = st.columns([2, 1])

        with col1:
            st.write(f"📄 Annual Report {year}")

        with col2:
            # Simulate missing reports randomly
            if year % 2 == 0:
                st.markdown(f"[Open Report]({fake_url})")
            else:
                st.error("Report unavailable")