import streamlit as st
import pandas as pd
import plotly.express as px

from utils.loader import (
    build_master_stock,
    get_latest_stock,
    dashboard_summary,
    stock_health,
    calculate_consumption,
    get_years,
    get_months,
    get_weeks,
    get_chemicals
)

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="Chemical Dashboard",
    page_icon="🧪",
    layout="wide"
)

# =====================================================
# LOAD DATA
# =====================================================

master = build_master_stock()
consumption = calculate_consumption()

if master.empty:
    st.error("No Excel data found inside data folder.")
    st.stop()

summary = dashboard_summary()

# =====================================================
# TITLE
# =====================================================

st.title("🧪 Chemical Stock & Consumption Dashboard")
st.caption("Water Management Division")

# =====================================================
# SIDEBAR
# =====================================================

st.sidebar.header("Filters")

years = ["All"] + list(get_years())
selected_year = st.sidebar.selectbox(
    "Year",
    years
)

months = ["All"] + list(get_months(selected_year))
selected_month = st.sidebar.selectbox(
    "Month",
    months
)

weeks = ["All"] + list(
    get_weeks(
        selected_year,
        selected_month
    )
)

selected_week = st.sidebar.selectbox(
    "Week",
    weeks
)

chemicals = ["All"] + list(
    get_chemicals()
)

selected_chemical = st.sidebar.selectbox(
    "Chemical",
    chemicals
)

# =====================================================
# FILTERS
# =====================================================

inventory = master.copy()

if selected_year != "All":
    inventory = inventory[
        inventory["Year"] == selected_year
    ]

if selected_month != "All":
    inventory = inventory[
        inventory["Month"] == selected_month
    ]

if selected_week != "All":
    inventory = inventory[
        inventory["Week"] == selected_week
    ]

if selected_chemical != "All":
    inventory = inventory[
        inventory["Chemical"] == selected_chemical
    ]

inventory = stock_health(inventory)

cons = consumption.copy()

if selected_year != "All":
    cons = cons[
        cons["Year"] == selected_year
    ]

if selected_month != "All":
    cons = cons[
        cons["Month"] == selected_month
    ]

if selected_week != "All":
    cons = cons[
        cons["Week"] == selected_week
    ]

if selected_chemical != "All":
    cons = cons[
        cons["Chemical"] == selected_chemical
    ]

# =====================================================
# MENU
# =====================================================

page = st.sidebar.radio(
    "Menu",
    [
        "Executive Dashboard",
        "Consumption Analysis",
        "Stock Status",
        "Procurement Planning",
        "Reports"
    ]
)

# =====================================================
# EXECUTIVE DASHBOARD
# =====================================================

if page == "Executive Dashboard":

    st.header("📊 Executive Dashboard")

    latest_date, latest_stock = get_latest_stock()

    latest_stock = stock_health(
        latest_stock
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric(
            "Total Chemicals",
            summary["Total Chemicals"]
        )

    with c2:
        st.metric(
            "Total Stock",
            round(summary["Total Stock"], 2)
        )

    with c3:
        st.metric(
            "Daily Requirement",
            round(summary["Daily Requirement"], 2)
        )

    with c4:
        st.metric(
            "Monthly Requirement",
            round(summary["Monthly Requirement"], 2)
        )

    st.subheader(
        f"Latest Stock Position : {latest_date}"
    )

    status = (
        latest_stock
        .groupby(
            "Status",
            as_index=False
        )
        .size()
    )

    fig = px.pie(
        status,
        names="Status",
        values="size",
        hole=0.5
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    fig = px.bar(
        latest_stock,
        x="Chemical",
        y="Available Stock",
        color="Status",
        text="Available Stock"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.dataframe(
        latest_stock,
        use_container_width=True
    )

# =====================================================
# CONSUMPTION ANALYSIS
# =====================================================

elif page == "Consumption Analysis":

    st.header("📈 Consumption Analysis")

    if cons.empty:
        st.warning(
            "No data found."
        )
        st.stop()

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric(
            "Total Consumption",
            round(
                cons["Consumption"].sum(),
                2
            )
        )

    with c2:
        st.metric(
            "Average Consumption",
            round(
                cons["Consumption"].mean(),
                2
            )
        )

    with c3:
        st.metric(
            "Maximum Consumption",
            round(
                cons["Consumption"].max(),
                2
            )
        )

    with c4:
        st.metric(
            "Chemicals",
            cons["Chemical"].nunique()
        )

    st.subheader("Daily Consumption")

    daily = (
        cons.groupby(
            "Date",
            as_index=False
        )["Consumption"]
        .sum()
    )

    fig = px.line(
        daily,
        x="Date",
        y="Consumption",
        markers=True
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.subheader(
        "Chemical Wise Consumption"
    )

    chemical = (
        cons.groupby(
            "Chemical",
            as_index=False
        )["Consumption"]
        .sum()
    )

    fig = px.bar(
        chemical,
        x="Chemical",
        y="Consumption",
        color="Chemical",
        text="Consumption"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.subheader(
        "Monthly Consumption"
    )

    monthly = (
        cons.groupby(
            ["Year", "Month"],
            as_index=False
        )["Consumption"]
        .sum()
    )

    fig = px.bar(
        monthly,
        x="Month",
        y="Consumption",
        color="Year"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.subheader(
        "Yearly Consumption"
    )

    yearly = (
        cons.groupby(
            "Year",
            as_index=False
        )["Consumption"]
        .sum()
    )

    fig = px.line(
        yearly,
        x="Year",
        y="Consumption",
        markers=True
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# =====================================================
# STOCK STATUS
# =====================================================

elif page == "Stock Status":

    st.header("📦 Stock Status")

    display = stock_health(
        inventory.copy()
    )

    fig = px.bar(
        display,
        x="Chemical",
        y="Available Days",
        color="Status",
        text="Available Days"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    critical = display[
        display["Status"] == "Critical"
    ]

    if not critical.empty:

        st.error(
            f"{len(critical)} critical chemicals found."
        )

        st.dataframe(
            critical,
            use_container_width=True
        )

    st.dataframe(
        display,
        use_container_width=True
    )

# =====================================================
# PROCUREMENT
# =====================================================

elif page == "Procurement Planning":

    st.header(
        "🚚 Procurement Planning"
    )

    latest_date, latest = get_latest_stock()

    latest["Required Qty"] = (
        latest["3 Month Requirement"]
        - latest["Available Stock"]
    )

    latest["Required Qty"] = (
        latest["Required Qty"]
        .clip(lower=0)
    )

    procurement = latest[
        [
            "Chemical",
            "Vendor",
            "Available Stock",
            "3 Month Requirement",
            "Required Qty"
        ]
    ]

    st.dataframe(
        procurement,
        use_container_width=True
    )

    fig = px.bar(
        procurement,
        x="Chemical",
        y="Required Qty",
        text="Required Qty"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# =====================================================
# REPORTS
# =====================================================

elif page == "Reports":

    st.header("📄 Reports")

    csv = inventory.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        "Download Stock Report",
        csv,
        "Stock_Report.csv",
        "text/csv"
    )

    csv2 = cons.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        "Download Consumption Report",
        csv2,
        "Consumption_Report.csv",
        "text/csv"
    )
