import streamlit as st
import pandas as pd
import plotly.express as px

from utils.loader import (
    load_stock_master,
    load_consumption_master,
    load_po_tracker,
    load_chemical_master,
    stock_health
)

st.set_page_config(
    page_title="Chemical Dashboard",
    page_icon="🧪",
    layout="wide"
)

stock = load_stock_master()
cons = load_consumption_master()
po = load_po_tracker()
chem = load_chemical_master()

if stock.empty:
    st.error("Stock Master not found.")
    st.stop()

stock = stock_health(stock)

st.title("🧪 Chemical Stock & Consumption Dashboard")

# =====================================================
# SIDEBAR
# =====================================================

page = st.sidebar.radio(
    "Dashboard",
    [
        "Executive Dashboard",
        "Consumption Analysis",
        "Location Analysis",
        "Shift Analysis",
        "Inventory Health",
        "Procurement Planning",
        "PO Tracker"
    ]
)

chemicals = ["All"] + sorted(
    stock["Chemical"].dropna().unique().tolist()
)

selected_chemical = st.sidebar.selectbox(
    "Chemical",
    chemicals
)

# =====================================================
# EXECUTIVE
# =====================================================

if page == "Executive Dashboard":

    latest = (
        stock
        .sort_values("Date")
        .groupby("Chemical")
        .tail(1)
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric(
            "Chemicals",
            latest["Chemical"].nunique()
        )

    with c2:
        st.metric(
            "Stock Qty",
            round(
                latest["Available Stock"].sum(),
                2
            )
        )

    with c3:
        st.metric(
            "Open POs",
            len(
                po[
                    po["Status"] == "Open"
                ]
            )
        )

    with c4:
        st.metric(
            "Today's Consumption",
            round(
                cons["Consumption"].sum(),
                2
            )
            if not cons.empty
            else 0
        )

    st.subheader("Current Stock")

    fig = px.bar(
        latest,
        x="Chemical",
        y="Available Stock",
        color="Status"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# =====================================================
# CONSUMPTION
# =====================================================

elif page == "Consumption Analysis":

    if cons.empty:
        st.warning("No Consumption Data")
        st.stop()

    data = cons.copy()

    if selected_chemical != "All":
        data = data[
            data["Chemical"]
            == selected_chemical
        ]

    st.subheader("Daily Consumption")

    daily = (
        data.groupby("Date")
        ["Consumption"]
        .sum()
        .reset_index()
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

    st.subheader("Chemical Wise Consumption")

    chemical = (
        data.groupby("Chemical")
        ["Consumption"]
        .sum()
        .reset_index()
    )

    fig = px.bar(
        chemical,
        x="Chemical",
        y="Consumption"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# =====================================================
# LOCATION
# =====================================================

elif page == "Location Analysis":

    if cons.empty:
        st.stop()

    location = (
        cons.groupby("Location")
        ["Consumption"]
        .sum()
        .reset_index()
    )

    fig = px.bar(
        location,
        x="Location",
        y="Consumption",
        color="Location"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# =====================================================
# SHIFT
# =====================================================

elif page == "Shift Analysis":

    if cons.empty:
        st.stop()

    shift = (
        cons.groupby("Shift")
        ["Consumption"]
        .sum()
        .reset_index()
    )

    fig = px.pie(
        shift,
        names="Shift",
        values="Consumption",
        hole=0.5
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# =====================================================
# INVENTORY
# =====================================================

elif page == "Inventory Health":

    latest = (
        stock
        .sort_values("Date")
        .groupby("Chemical")
        .tail(1)
    )

    st.subheader("Inventory Status")

    fig = px.bar(
        latest,
        x="Chemical",
        y="Available Days",
        color="Status"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.dataframe(
        latest,
        use_container_width=True
    )

# =====================================================
# PROCUREMENT
# =====================================================

elif page == "Procurement Planning":

    latest = (
        stock
        .sort_values("Date")
        .groupby("Chemical")
        .tail(1)
    )

    latest["Required Qty"] = (
        latest["3 Month Requirement"]
        -
        latest["Available Stock"]
    )

    latest["Required Qty"] = (
        latest["Required Qty"]
        .clip(lower=0)
    )

    fig = px.bar(
        latest,
        x="Chemical",
        y="Required Qty",
        color="Vendor"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
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

# =====================================================
# PO TRACKER
# =====================================================

elif page == "PO Tracker":

    open_po = po[
        po["Status"] == "Open"
    ]

    c1, c2 = st.columns(2)

    with c1:
        st.metric(
            "Open PO",
            len(open_po)
        )

    with c2:
        st.metric(
            "Pending Qty",
            round(
                po["Pending Qty"].sum(),
                2
            )
        )

    fig = px.bar(
        po,
        x="PO Number",
        y="Pending Qty",
        color="Vendor"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.dataframe(
        po,
        use_container_width=True
    )
