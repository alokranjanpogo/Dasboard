# ==========================================================
# Chemical Consumption & Stock Management Dashboard
# ==========================================================

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from streamlit_option_menu import option_menu

from utils.loader import *

# ==========================================================
# Page Configuration
# ==========================================================

st.set_page_config(
    page_title="Chemical Consumption & Stock Dashboard",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================================
# Custom CSS
# ==========================================================

st.markdown("""
<style>

.block-container{
padding-top:1rem;
padding-bottom:1rem;
}

.main{
background:#f5f7fb;
}

.metric-card{
background:white;
padding:15px;
border-radius:12px;
box-shadow:0px 2px 8px rgba(0,0,0,0.10);
}

h1,h2,h3{
color:#003366;
}

</style>
""",unsafe_allow_html=True)

# ==========================================================
# Dashboard Title
# ==========================================================

st.title("🧪 Chemical Consumption & Stock Management Dashboard")

st.caption(
"Water Management Division | Chemical Inventory Analytics"
)

# ==========================================================
# Load Data
# ==========================================================

master_df = build_master_stock()

latest_date, latest_stock = get_latest_stock()

# ==========================================================
# Sidebar Filters
# ==========================================================

st.sidebar.title("Dashboard Filters")

years = ["All"] + list(get_years())

selected_year = st.sidebar.selectbox(
    "Select Year",
    years
)

if selected_year=="All":

    filtered = master_df.copy()

else:

    filtered = filter_stock(
        year=selected_year
    )

months=["All"]+sorted(
filtered["Month"].dropna().unique().tolist()
)

selected_month=st.sidebar.selectbox(
"Select Month",
months
)

if selected_month!="All":

    filtered=filtered[
    filtered["Month"]==selected_month
    ]

weeks=["All"]+sorted(
filtered["Week"].dropna().unique().tolist()
)

selected_week=st.sidebar.selectbox(
"Select Week",
weeks
)

if selected_week!="All":

    filtered=filtered[
    filtered["Week"]==selected_week
    ]

chemicals=["All"]+sorted(
filtered["Chemical"].dropna().unique().tolist()
)

selected_chemical=st.sidebar.selectbox(
"Select Chemical",
chemicals
)

if selected_chemical!="All":

    filtered=filtered[
    filtered["Chemical"]==selected_chemical
    ]

# ==========================================================
# Navigation
# ==========================================================

selected = option_menu(
menu_title=None,
options=[
"Executive Dashboard",
"Consumption Analysis",
"Stock Status",
"Procurement",
"Forecast",
"Reports"
],
icons=[
"speedometer2",
"graph-up",
"boxes",
"truck",
"bar-chart",
"file-earmark-pdf"
],
orientation="horizontal"
)
# ==========================================================
# Executive Dashboard
# ==========================================================

if selected == "Executive Dashboard":

    st.header("📊 Executive Dashboard")

    latest_date, latest_stock = get_latest_stock()

    st.success(f"Latest Stock Updated : {latest_date}")

    if filtered.empty:

        st.warning("⚠ No data available for selected filter.")

        st.stop()

    # ======================================================
    # Data Cleaning
    # ======================================================

    display = filtered.copy()

    numeric_cols = [
        "Daily Requirement",
        "Monthly Requirement",
        "3 Month Requirement",
        "Available Stock",
        "Available Days"
    ]

    for col in numeric_cols:

        display[col] = pd.to_numeric(
            display[col],
            errors="coerce"
        )

    display = display.dropna(subset=["Chemical"])

    display = display.fillna(0)

    # ======================================================
    # Stock Status
    # ======================================================

    def stock_status(days):

        if days >= 90:
            return "Healthy"

        elif days >= 30:
            return "Warning"

        else:
            return "Critical"

    display["Status"] = display["Available Days"].apply(stock_status)

    # ======================================================
    # KPI Calculation
    # ======================================================

    total_stock = round(
        display["Available Stock"].sum(),
        2
    )

    total_daily = round(
        display["Daily Requirement"].sum(),
        2
    )

    total_monthly = round(
        display["Monthly Requirement"].sum(),
        2
    )

    total_chemicals = display["Chemical"].nunique()

    healthy = len(
        display[
            display["Status"] == "Healthy"
        ]
    )

    warning = len(
        display[
            display["Status"] == "Warning"
        ]
    )

    critical = len(
        display[
            display["Status"] == "Critical"
        ]
    )

    # ======================================================
    # KPI Cards
    # ======================================================

    st.subheader("Executive Summary")

    c1, c2, c3, c4 = st.columns(4)

    with c1:

        st.metric(
            "Chemicals",
            total_chemicals
        )

    with c2:

        st.metric(
            "Available Stock",
            f"{total_stock:.2f} Ton"
        )

    with c3:

        st.metric(
            "Daily Requirement",
            f"{total_daily:.2f} Ton"
        )

    with c4:

        st.metric(
            "Monthly Requirement",
            f"{total_monthly:.2f} Ton"
        )

    st.divider()

    # ======================================================
    # Health Summary
    # ======================================================

    c1, c2, c3 = st.columns(3)

    with c1:

        st.success(f"🟢 Healthy : {healthy}")

    with c2:

        st.warning(f"🟡 Warning : {warning}")

    with c3:

        st.error(f"🔴 Critical : {critical}")

    st.divider()

    # ======================================================
    # Current Stock Table
    # ======================================================

    st.subheader("Current Chemical Stock")

    st.dataframe(
        display,
        use_container_width=True,
        hide_index=True,
        height=450
    )
    # ======================================================
    # Available Stock Chart
    # ======================================================

    st.subheader("📈 Available Stock by Chemical")

    fig = px.bar(
        display,
        x="Chemical",
        y="Available Stock",
        color="Status",
        text="Available Stock",
        height=500,
        color_discrete_map={
            "Healthy":"green",
            "Warning":"orange",
            "Critical":"red"
        }
    )

    fig.update_layout(
        xaxis_title="Chemical",
        yaxis_title="Available Stock (Ton)",
        legend_title="Stock Health",
        template="plotly_white"
    )

    fig.update_traces(
        textposition="outside"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # ======================================================
    # Available Days Chart
    # ======================================================

    st.subheader("📅 Available Days")

    fig = px.bar(
        display,
        x="Chemical",
        y="Available Days",
        color="Status",
        text="Available Days",
        height=500,
        color_discrete_map={
            "Healthy":"green",
            "Warning":"orange",
            "Critical":"red"
        }
    )

    fig.update_layout(
        xaxis_title="Chemical",
        yaxis_title="Available Days",
        template="plotly_white"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # ======================================================
    # Chemical Distribution
    # ======================================================

    st.subheader("🥧 Available Stock Distribution")

    fig = px.pie(
        display,
        names="Chemical",
        values="Available Stock",
        hole=0.55
    )

    fig.update_layout(
        template="plotly_white"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # ======================================================
    # Critical Chemicals
    # ======================================================

    st.subheader("🚨 Critical Chemicals")

    critical_df = display[
        display["Status"]=="Critical"
    ]

    if critical_df.empty:

        st.success(
            "✅ No critical chemicals available."
        )

    else:

        st.error(
            "Immediate procurement required."
        )

        st.dataframe(
            critical_df,
            use_container_width=True,
            hide_index=True
        )

    st.divider()

    # ======================================================
    # Vendor Summary
    # ======================================================

    st.subheader("🏭 Vendor Summary")

    vendor = (
        display.groupby("Vendor")
        .agg({
            "Available Stock":"sum",
            "Chemical":"count"
        })
        .reset_index()
    )

    vendor.columns=[
        "Vendor",
        "Total Stock",
        "Chemicals"
    ]

    st.dataframe(
        vendor,
        use_container_width=True,
        hide_index=True
    )

    # ======================================================
    # Executive Remarks
    # ======================================================

    st.subheader("📋 Executive Remarks")

    if critical > 0:

        st.error(
            f"{critical} chemicals require immediate procurement."
        )

    elif warning > 0:

        st.warning(
            f"{warning} chemicals should be reordered soon."
        )

    else:

        st.success(
            "Inventory level is healthy."
        )
        # ==========================================================
# Consumption Analysis
# ==========================================================

elif selected == "Consumption Analysis":

    st.header("📈 Chemical Consumption Analysis")

    if filtered.empty:

        st.warning("⚠ No data available for selected filters.")

        st.stop()

    consumption = filtered.copy()

    consumption["Available Stock"] = pd.to_numeric(
        consumption["Available Stock"],
        errors="coerce"
    )

    consumption["Daily Requirement"] = pd.to_numeric(
        consumption["Daily Requirement"],
        errors="coerce"
    )

    # ======================================================
    # KPI Cards
    # ======================================================

    st.subheader("Consumption Summary")

    c1, c2, c3, c4 = st.columns(4)

    with c1:

        st.metric(
            "Chemicals",
            consumption["Chemical"].nunique()
        )

    with c2:

        st.metric(
            "Total Available Stock",
            f"{consumption['Available Stock'].sum():.2f} Ton"
        )

    with c3:

        st.metric(
            "Daily Consumption",
            f"{consumption['Daily Requirement'].sum():.2f} Ton"
        )

    with c4:

        if consumption["Daily Requirement"].sum() > 0:

            days = consumption["Available Stock"].sum() / consumption["Daily Requirement"].sum()

        else:

            days = 0

        st.metric(
            "Estimated Days",
            f"{days:.1f}"
        )

    st.divider()

    # ======================================================
    # Chemical Consumption
    # ======================================================

    st.subheader("🧪 Chemical-wise Daily Consumption")

    fig = px.bar(
        consumption,
        x="Chemical",
        y="Daily Requirement",
        text="Daily Requirement",
        color="Chemical",
        height=500
    )

    fig.update_layout(
        xaxis_title="Chemical",
        yaxis_title="Daily Consumption (Ton)",
        showlegend=False,
        template="plotly_white"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # ======================================================
    # Available Stock
    # ======================================================

    st.subheader("📦 Available Stock")

    fig = px.bar(
        consumption,
        x="Chemical",
        y="Available Stock",
        color="Chemical",
        text="Available Stock",
        height=500
    )

    fig.update_layout(
        template="plotly_white",
        showlegend=False
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # ======================================================
    # Pie Chart
    # ======================================================

    st.subheader("🥧 Consumption Distribution")

    fig = px.pie(
        consumption,
        names="Chemical",
        values="Daily Requirement",
        hole=0.55
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # ======================================================
    # Trend Analysis
    # ======================================================

    st.subheader("📈 Daily Requirement Trend")

    trend = consumption.groupby(
        "Date",
        as_index=False
    )["Daily Requirement"].sum()

    fig = px.line(
        trend,
        x="Date",
        y="Daily Requirement",
        markers=True
    )

    fig.update_layout(
        template="plotly_white"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # ======================================================
    # Monthly Consumption
    # ======================================================

    st.subheader("📅 Monthly Consumption")

    monthly = consumption.groupby(
        "Month",
        as_index=False
    )["Daily Requirement"].sum()

    fig = px.bar(
        monthly,
        x="Month",
        y="Daily Requirement",
        text="Daily Requirement"
    )

    fig.update_layout(
        template="plotly_white"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # ======================================================
    # Consumption Table
    # ======================================================

    st.subheader("📋 Consumption Details")

    st.dataframe(
        consumption,
        use_container_width=True,
        hide_index=True,
        height=500
    )
    # ==========================================================
# Stock Status Dashboard
# ==========================================================

elif selected == "Stock Status":

    st.header("📦 Chemical Stock Status")

    if filtered.empty:

        st.warning("⚠ No data available.")

        st.stop()

    stock = filtered.copy()

    numeric_cols = [
        "Daily Requirement",
        "Monthly Requirement",
        "3 Month Requirement",
        "Available Stock",
        "Available Days"
    ]

    for col in numeric_cols:

        stock[col] = pd.to_numeric(
            stock[col],
            errors="coerce"
        )

    stock = stock.fillna(0)

    def status(days):

        if days >= 90:
            return "Healthy"

        elif days >= 30:
            return "Warning"

        else:
            return "Critical"

    stock["Status"] = stock["Available Days"].apply(status)

    # ======================================================
    # KPI
    # ======================================================

    st.subheader("Inventory Summary")

    c1,c2,c3,c4 = st.columns(4)

    with c1:

        st.metric(
            "Total Stock",
            round(stock["Available Stock"].sum(),2)
        )

    with c2:

        st.metric(
            "Daily Requirement",
            round(stock["Daily Requirement"].sum(),2)
        )

    with c3:

        st.metric(
            "Average Available Days",
            round(stock["Available Days"].mean(),1)
        )

    with c4:

        st.metric(
            "Chemicals",
            stock["Chemical"].nunique()
        )

    st.divider()

    # ======================================================
    # Available Days
    # ======================================================

    st.subheader("📅 Remaining Days")

    fig = px.bar(
        stock,
        x="Chemical",
        y="Available Days",
        color="Status",
        text="Available Days",
        color_discrete_map={
            "Healthy":"green",
            "Warning":"orange",
            "Critical":"red"
        }
    )

    fig.update_layout(
        template="plotly_white"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # ======================================================
    # Stock Distribution
    # ======================================================

    st.subheader("🥧 Inventory Distribution")

    fig = px.pie(
        stock,
        names="Chemical",
        values="Available Stock",
        hole=.55
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # ======================================================
    # Vendor Inventory
    # ======================================================

    st.subheader("🏭 Vendor Inventory")

    vendor = stock.groupby(
        "Vendor",
        as_index=False
    ).agg({
        "Available Stock":"sum",
        "Chemical":"count"
    })

    vendor.columns = [
        "Vendor",
        "Total Stock",
        "Chemicals"
    ]

    st.dataframe(
        vendor,
        use_container_width=True,
        hide_index=True
    )

    # ======================================================
    # Critical Chemicals
    # ======================================================

    st.subheader("🚨 Immediate Procurement")

    critical = stock[
        stock["Status"]=="Critical"
    ]

    if critical.empty:

        st.success(
            "No chemical requires immediate procurement."
        )

    else:

        st.dataframe(
            critical,
            use_container_width=True,
            hide_index=True
        )

    st.divider()

    # ======================================================
    # Complete Inventory
    # ======================================================

    st.subheader("📋 Complete Inventory")

    st.dataframe(
        stock,
        use_container_width=True,
        hide_index=True,
        height=500
    )
    # ==========================================================
# Procurement Dashboard
# ==========================================================

elif selected == "Procurement":

    st.header("🚚 Procurement Dashboard")

    if filtered.empty:

        st.warning("⚠ No data available.")

        st.stop()

    procurement = filtered.copy()

    procurement["Available Days"] = pd.to_numeric(
        procurement["Available Days"],
        errors="coerce"
    )

    procurement["Available Stock"] = pd.to_numeric(
        procurement["Available Stock"],
        errors="coerce"
    )

    procurement["Priority"] = procurement["Available Days"].apply(
        lambda x:
        "High" if x < 30 else
        "Medium" if x < 90 else
        "Low"
    )

    # ======================================================
    # KPI
    # ======================================================

    c1,c2,c3 = st.columns(3)

    with c1:
        st.metric(
            "High Priority",
            len(procurement[procurement["Priority"]=="High"])
        )

    with c2:
        st.metric(
            "Medium Priority",
            len(procurement[procurement["Priority"]=="Medium"])
        )

    with c3:
        st.metric(
            "Low Priority",
            len(procurement[procurement["Priority"]=="Low"])
        )

    st.divider()

    # ======================================================
    # Priority Chart
    # ======================================================

    st.subheader("Priority Chemicals")

    fig = px.bar(
        procurement.sort_values("Available Days"),
        x="Chemical",
        y="Available Days",
        color="Priority",
        text="Available Days",
        color_discrete_map={
            "High":"red",
            "Medium":"orange",
            "Low":"green"
        }
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # ======================================================
    # Vendor Summary
    # ======================================================

    st.subheader("Vendor Wise Summary")

    vendor = procurement.groupby(
        "Vendor",
        as_index=False
    ).agg({
        "Chemical":"count",
        "Available Stock":"sum"
    })

    st.dataframe(
        vendor,
        use_container_width=True,
        hide_index=True
    )

    # ======================================================
    # Procurement Table
    # ======================================================

    st.subheader("Procurement Recommendation")

    st.dataframe(
        procurement.sort_values("Available Days"),
        use_container_width=True,
        hide_index=True
    )

# ==========================================================
# Forecast Dashboard
# ==========================================================

elif selected == "Forecast":

    st.header("📈 Forecast Dashboard")

    if filtered.empty:

        st.warning("⚠ No data available.")

        st.stop()

    forecast = filtered.copy()

    forecast["Available Days"] = pd.to_numeric(
        forecast["Available Days"],
        errors="coerce"
    )

    forecast["Daily Requirement"] = pd.to_numeric(
        forecast["Daily Requirement"],
        errors="coerce"
    )

    forecast["Predicted Reorder (Days)"] = (
        forecast["Available Days"] - 15
    ).clip(lower=0)

    st.subheader("Forecast Summary")

    st.dataframe(
        forecast[
            [
                "Chemical",
                "Available Days",
                "Predicted Reorder (Days)",
                "Vendor"
            ]
        ],
        use_container_width=True,
        hide_index=True
    )

    st.subheader("Forecast Chart")

    fig = px.bar(
        forecast,
        x="Chemical",
        y="Predicted Reorder (Days)",
        color="Chemical",
        text="Predicted Reorder (Days)"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# ==========================================================
# Reports
# ==========================================================

elif selected == "Reports":

    st.header("📄 Reports")

    if filtered.empty:

        st.warning("⚠ No data available.")

        st.stop()

    st.subheader("Download Current Report")

    csv = filtered.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="📥 Download CSV Report",
        data=csv,
        file_name="Chemical_Report.csv",
        mime="text/csv"
    )

    st.subheader("Current Dataset")

    st.dataframe(
        filtered,
        use_container_width=True,
        hide_index=True,
        height=600
    )
    
