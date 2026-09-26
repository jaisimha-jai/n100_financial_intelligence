import streamlit as st

st.set_page_config(
    page_title="Nifty 100 Analytics",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("Nifty 100 Dashboard")

st.sidebar.title("Navigation")

page = st.sidebar.radio(
    "Go to",
    [
        "Home",
        "Profile",
        "Screener",
        "Peers",
        "Trends",
        "Sectors",
        "Capital",
        "Reports"
    ]
)

if page == "Home":
    import pages.home as home
    home.run()

elif page == "Profile":
    import pages.profile as profile
    profile.run()

elif page == "Screener":
    import pages.screener as screener
    screener.run()

elif page == "Peers":
    import pages.peers as peers
    peers.run()

elif page == "Trends":
    import pages.trends as trends
    trends.run()

elif page == "Sectors":
    import pages.sectors as sectors
    sectors.run()

elif page == "Capital":
    import pages.capital as capital
    capital.run()

elif page == "Reports":
    import pages.reports as reports
    reports.run()