import streamlit as st
import pandas as pd
import plotly.express as px

from utils.loader import (
    build_master_stock,
    calculate_consumption,
    stock_health
)

# ==========================================
# PAGE CONFIG
# ==========================================

st.set_page_config(
    page_title="Chemical Dashboard",
    page_icon="🧪",
    layout="wide"
)

# ==========================================
# LOAD DATA
# ==========================================

master = build_master_stock()

if master.empty:
    st.error(
        "No data found in data folder."
    )
    st.stop()

consumption = calculate_consumption()

# ==========================================
# TITLE
# ==========================================

st.title(
    "🧪 Chemical Consumption & Stock Dashboard"
)

# ==========================================
# FILTERS
# ==========================================

st.sidebar.header("Filters")

years = ["All"] + sorted(
    master["Year"]
    .dropna()
    .unique()
    .tolist()
)

selected_year = st.sidebar.selectbox(
    "Year",
    years
)

months = ["All"] + sorted(
    master["Month"]
    .dropna()
    .unique()
    .tolist()
)

selected_month = st.sidebar.selectbox(
    "Month",
    months
)

chemicals = ["All"] + sorted(
    master["Chemical"]
    .dropna()
    .unique()
    .tolist()
)

selected_chemical = st.sidebar.selectbox(
    "Chemical",
    chemicals
)

# ==========================================
# FILTER DATA
# ==========================================

inventory = master.copy()

if selected_year != "All":
    inventory = inventory[
        inventory["Year"] == selected_year
    ]

if selected_month != "All":
    inventory = inventory[
        inventory["Month"] == selected_month
    ]

if selected_chemical != "All":
    inventory = inventory[
        inventory["Chemical"]
        == selected_chemical
    ]

display = stock_health(
    inventory.copy()
)

# ==========================================
# MENU
# ==========================================

page = st.sidebar.radio(
    "Dashboard",
    [
        "Executive Dashboard",
        "Consumption Analysis",
        "Stock Status",
        "Procurement Planning"
    ]
)

# ==========================================
# EXECUTIVE DASHBOARD
# ==========================================

if page == "Executive Dashboard":

    st.header(
        "📊 Executive Dashboard"
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric(
            "Chemicals",
            display["Chemical"].nunique()
        )

    with c2:
        st.metric(
            "Stock",
            round(
                display["Available Stock"]
                .sum(),
                2
            )
        )

    with c3:
        st.metric(
            "Average Days",
            round(
                display["Available Days"]
                .mean(),
                1
            )
        )

    with c4:
        st.metric(
            "Vendors",
            display["Vendor"]
            .nunique()
        )

    st.divider()

    health = (
        display
        .groupby(
            "Status",
            as_index=False
        )
        .size()
    )

    fig = px.pie(
        health,
        names="Status",
        values="size",
        hole=.5
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# ==========================================
# CONSUMPTION
# ==========================================

elif page == "Consumption Analysis":

    st.header(
        "📈 Consumption Analysis"
    )

    cons = consumption.copy()

    if selected_year != "All":
        cons = cons[
            cons["Year"]
            == selected_year
        ]

    if selected_month != "All":
        cons = cons[
            cons["Month"]
            == selected_month
        ]

    if selected_chemical != "All":
        cons = cons[
            cons["Chemical"]
            == selected_chemical
        ]

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric(
            "Total Consumption",
            round(
                cons["Consumption"]
                .sum(),
                2
            )
        )

    with c2:
        st.metric(
            "Average",
            round(
                cons["Consumption"]
                .mean(),
                2
            )
        )

    with c3:
        st.metric(
            "Maximum",
            round(
                cons["Consumption"]
                .max(),
                2
            )
        )

    st.subheader(
        "Daily Trend"
    )

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
        "Chemical Consumption"
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

# ==========================================
# STOCK STATUS
# ==========================================

elif page == "Stock Status":

    st.header(
        "📦 Stock Status"
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

    st.dataframe(
        display,
        use_container_width=True
    )

# ==========================================
# PROCUREMENT
# ==========================================

elif page == "Procurement Planning":

    st.header(
        "🚚 Procurement Planning"
    )

    latest_date = display[
        "Date"
    ].max()

    latest = display[
        display["Date"]
        == latest_date
    ].copy()

    latest["Required Qty"] = (
        latest["3 Month Requirement"]
        - latest["Available Stock"]
    )

    latest["Required Qty"] = (
        latest["Required Qty"]
        .clip(lower=0)
    )

    st.dataframe(
        latest[
            [
                "Chemical",
                "Vendor",
                "Available Stock",
                "3 Month Requirement",
                "Required Qty"
            ]
        ],
        use_container_width=True
    )

    fig = px.bar(
        latest,
        x="Chemical",
        y="Required Qty",
        text="Required Qty"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )
