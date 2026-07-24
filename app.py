# ==========================================================
# Chemical Dashboard
# ==========================================================

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from streamlit_option_menu import option_menu

from utils.loader import (
    build_master_stock,
    get_latest_stock,
    dashboard_summary,
    stock_health,
    calculate_consumption,
    weekly_consumption,
    monthly_consumption,
    yearly_consumption,
    chemical_consumption,
    filter_data,
    get_years,
    get_months,
    get_weeks,
    get_chemicals
)
# ==========================================================
# PAGE CONFIG
# ==========================================================

st.set_page_config(
    page_title="Chemical Dashboard",
    page_icon="🧪",
    layout="wide"
)

# ==========================================================
# CSS
# ==========================================================

st.markdown("""
<style>

.main{
background:#F4F8FB;
}

h1,h2,h3{
color:#003366;
}

div[data-testid="stMetric"]{

background:white;

padding:15px;

border-radius:10px;

box-shadow:0px 2px 8px rgba(0,0,0,0.15);

}

</style>

""",unsafe_allow_html=True)

# ==========================================================
# LOAD DATA
# ==========================================================

master = build_master_stock()

summary = dashboard_summary()

latest_date, latest_stock = get_latest_stock()

# ==========================================================
# PAGE CONFIG
# ==========================================================

st.set_page_config(
    page_title="Chemical Consumption & Stock Dashboard",
    page_icon="🧪",
    layout="wide"
)

# ==========================================================
# TITLE
# ==========================================================

st.title("🧪 Chemical Consumption & Stock Dashboard")
st.caption("Tata Steel UISL | Water Management Division")

# ==========================================================
# SIDEBAR FILTERS
# ==========================================================

st.sidebar.header("Dashboard Filters")

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

weeks = ["All"] + list(get_weeks(selected_year, selected_month))
selected_week = st.sidebar.selectbox(
    "Week",
    weeks
)

chemicals = ["All"] + list(get_chemicals())
selected_chemical = st.sidebar.selectbox(
    "Chemical",
    chemicals
)

# ==========================================================
# FILTER DATA
# ==========================================================

inventory = filter_data(
    year=selected_year,
    month=selected_month,
    week=selected_week,
    chemical=selected_chemical
)

# ==========================================================
# MENU
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
        "bar-chart",
        "boxes",
        "truck",
        "graph-up",
        "file-earmark-text"
    ],
    orientation="horizontal",
    default_index=0
)
# ==========================================================
# EXECUTIVE DASHBOARD
# ==========================================================

# ==========================================================
# EXECUTIVE DASHBOARD
# ==========================================================

if selected == "Executive Dashboard":

    st.header("📊 Executive Dashboard")

    if inventory.empty:
        st.warning("No data available for selected filters.")
        st.stop()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Total Chemicals",
            inventory["Chemical"].nunique()
        )

    with col2:
        st.metric(
            "Total Stock",
            f'{inventory["Available Stock"].sum():,.2f} Ton'
        )

    with col3:
        st.metric(
            "Daily Requirement",
            f'{inventory["Daily Requirement"].sum():,.2f} Ton'
        )

    with col4:
        st.metric(
            "Monthly Requirement",
            f'{inventory["Monthly Requirement"].sum():,.2f} Ton'
        )

    st.divider()

    inventory = stock_health(inventory)

    status = (
        inventory.groupby(
            "Status",
            as_index=False
        ).size()
    )

    fig = px.pie(
        status,
        names="Status",
        values="size",
        hole=0.55
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.subheader("Current Inventory")

    st.dataframe(
        inventory,
        use_container_width=True,
        hide_index=True
    )

    csv = inventory.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        "📥 Download Executive Report",
        csv,
        file_name="Executive_Report.csv",
        mime="text/csv"
    )
# ======================================================
# HEALTH CARDS
# ======================================================

st.subheader("Inventory Health")

c1,c2,c3 = st.columns(3)

with c1:

    st.success(
        f'🟢 Healthy : {summary["Healthy"]}'
    )

with c2:

    st.warning(
        f'🟡 Warning : {summary["Warning"]}'
    )

with c3:

    st.error(
        f'🔴 Critical : {summary["Critical"]}'
    )

st.divider()

# ======================================================
# STOCK TABLE
# ======================================================

st.subheader("Current Stock")

st.dataframe(

    display,

    hide_index=True,

    use_container_width=True,

    height=420

)

st.divider()

# ======================================================
# AVAILABLE STOCK
# ======================================================

st.subheader("Available Stock by Chemical")

fig = px.bar(

    display,

    x="Chemical",

    y="Available Stock",

    color="Status",

    text="Available Stock",

    color_discrete_map={

        "Healthy":"green",

        "Warning":"orange",

        "Critical":"red"

    },

    height=520

)

fig.update_layout(

    template="plotly_white",

    xaxis_title="Chemical",

    yaxis_title="Stock (Ton)"

)

fig.update_traces(

    textposition="outside"

)

st.plotly_chart(

    fig,

    use_container_width=True

)

# ======================================================
# AVAILABLE DAYS
# ======================================================

st.subheader("Remaining Stock Days")

fig = px.bar(

    display,

    x="Chemical",

    y="Available Days",

    color="Status",

    text="Available Days",

    color_discrete_map={

        "Healthy":"green",

        "Warning":"orange",

        "Critical":"red"

    },

    height=520

)

fig.update_layout(

    template="plotly_white"

)

st.plotly_chart(

    fig,

    use_container_width=True

)

# ======================================================
# PIE
# ======================================================

st.subheader("Stock Distribution")

fig = px.pie(

    display,

    names="Chemical",

    values="Available Stock",

    hole=.60

)

st.plotly_chart(

    fig,

    use_container_width=True

)

st.divider()

# ======================================================
# CRITICAL CHEMICAL ALERT
# ======================================================

st.subheader("🚨 Critical Chemical Alert")

critical_df = display[
    display["Status"] == "Critical"
]

if critical_df.empty:

    st.success(
        "✅ No critical chemicals found."
    )

else:

    st.error(
        f"{len(critical_df)} chemical(s) require immediate procurement."
    )

    st.dataframe(

        critical_df[
            [
                "Chemical",
                "Available Stock",
                "Available Days",
                "Vendor"
            ]
        ],

        hide_index=True,

        use_container_width=True

    )

st.divider()

# ======================================================
# VENDOR SUMMARY
# ======================================================

st.subheader("🏭 Vendor Summary")

vendor = (

    display

    .groupby(
        "Vendor",
        as_index=False
    )

    .agg({

        "Chemical":"count",

        "Available Stock":"sum",

        "Available Days":"mean"

    })

)

vendor.columns=[

    "Vendor",

    "Chemicals",

    "Total Stock",

    "Average Days"

]

st.dataframe(

    vendor,

    hide_index=True,

    use_container_width=True

)

st.divider()

# ======================================================
# STOCK HEALTH DONUT
# ======================================================

st.subheader("🟢 Inventory Health")

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

    hole=0.65,

    color="Status",

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

st.divider()

# ======================================================
# INVENTORY SUMMARY
# ======================================================

st.subheader("📋 Inventory Summary")

inventory = display[

    [

        "Chemical",

        "Available Stock",

        "Available Days",

        "Vendor",

        "Status"

    ]

].sort_values(

    "Available Days"

)

st.dataframe(

    inventory,

    use_container_width=True,

    hide_index=True,

    height=420

)

st.divider()

# ======================================================
# DOWNLOAD REPORT
# ======================================================

st.subheader("📥 Download Executive Report")

csv = inventory.to_csv(
    index=False
).encode("utf-8")

st.download_button(

    "📄 Download CSV",

    csv,

    file_name="Executive_Dashboard_Report.csv",

    mime="text/csv"

)

st.divider()

# ======================================================
# EXECUTIVE REMARKS
# ======================================================

        st.subheader("📝 Executive Remarks")
        
        if summary["Critical"] > 0:
        
        st.error(
        
            "Immediate procurement is recommended for critical chemicals."
        
        )
        
        elif summary["Warning"] > 0:
        
        st.warning(
        
            "Some chemicals are approaching the reorder level."
        
        )
        
        else: 
        
        st.success(
        
            "Inventory is healthy. No immediate procurement required."
        
        )

# ==========================================================
# CONSUMPTION ANALYSIS
# ==========================================================

elif selected == "Consumption Analysis":

    st.header("📈 Chemical Consumption Analysis")

    from utils.loader import get_excel_files

    st.write("Files found:")
    st.write(get_excel_files())
    
    st.stop()

# ===========================================
# FILTERS
# ===========================================

if selected_year != "All":

    consumption = consumption[
        consumption["Year"] == selected_year
    ]

if selected_month != "All":

    consumption = consumption[
        consumption["Month"] == selected_month
    ]

if selected_week != "All":

    consumption = consumption[
        consumption["Week"] == selected_week
    ]

if selected_chemical != "All":

    consumption = consumption[
        consumption["Chemical"] == selected_chemical
    ]

if consumption.empty:

    st.warning("No data available for selected filter.")

    st.stop()

# ===========================================
# KPI
# ===========================================

st.subheader("Consumption Summary")

c1,c2,c3,c4 = st.columns(4)

with c1:

    st.metric(

        "Total Consumption",

        f"{consumption['Consumption'].sum():.2f} Ton"

    )

with c2:

    st.metric(

        "Average Daily",

        f"{consumption['Consumption'].mean():.2f} Ton"

    )

with c3:

    st.metric(

        "Maximum",

        f"{consumption['Consumption'].max():.2f} Ton"

    )

with c4:

    st.metric(

        "Chemicals",

        consumption["Chemical"].nunique()

    )

st.divider()

# ===========================================
# DAILY TREND
# ===========================================

st.subheader("📅 Daily Consumption Trend")

daily = (

    consumption

    .groupby(

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

fig.update_layout(

    template="plotly_white"

)

st.plotly_chart(

    fig,

    use_container_width=True

)

# ===========================================
# CHEMICAL CONSUMPTION
# ===========================================

st.subheader("🧪 Chemical-wise Consumption")

chemical = (

    consumption

    .groupby(

        "Chemical",

        as_index=False

    )["Consumption"]

    .sum()

)

fig = px.bar(

    chemical,

    x="Chemical",

    y="Consumption",

    text="Consumption",

    color="Chemical",

    height=500

)

fig.update_layout(

    template="plotly_white",

    showlegend=False

)

fig.update_traces(

    textposition="outside"

)

st.plotly_chart(

    fig,

    use_container_width=True

)

# ===========================================
# PIE CHART
# ===========================================

st.subheader("🥧 Consumption Distribution")

fig = px.pie(

    chemical,

    names="Chemical",

    values="Consumption",

    hole=0.60

)

st.plotly_chart(

    fig,

    use_container_width=True

)
# ======================================================
# WEEKLY CONSUMPTION
# ======================================================

st.subheader("📅 Weekly Consumption")

weekly = (
    consumption
    .groupby(
        "Week",
        as_index=False
    )["Consumption"]
    .sum()
)

fig = px.bar(
    weekly,
    x="Week",
    y="Consumption",
    text="Consumption",
    color="Consumption",
    height=450
)

fig.update_layout(
    template="plotly_white",
    xaxis_title="Week",
    yaxis_title="Consumption (Ton)"
)

fig.update_traces(
    textposition="outside"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# ======================================================
# MONTHLY CONSUMPTION
# ======================================================

st.subheader("📆 Monthly Consumption")

monthly = (
    consumption
    .groupby(
        "Month",
        as_index=False
    )["Consumption"]
    .sum()
)

month_order = [
    "January","February","March","April",
    "May","June","July","August",
    "September","October","November","December"
]

monthly["Month"] = pd.Categorical(
    monthly["Month"],
    categories=month_order,
    ordered=True
)

monthly = monthly.sort_values("Month")

fig = px.line(
    monthly,
    x="Month",
    y="Consumption",
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
# YEARLY CONSUMPTION
# ======================================================

st.subheader("📈 Yearly Consumption")

yearly = (
    consumption
    .groupby(
        "Year",
        as_index=False
    )["Consumption"]
    .sum()
)

fig = px.bar(
    yearly,
    x="Year",
    y="Consumption",
    text="Consumption",
    height=450
)

fig.update_layout(
    template="plotly_white"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# ======================================================
# TOP CONSUMING CHEMICAL
# ======================================================

st.subheader("🏆 Top Consuming Chemicals")

top = chemical.sort_values(
    "Consumption",
    ascending=False
)

st.dataframe(
    top,
    use_container_width=True,
    hide_index=True
)

# ======================================================
# CONSUMPTION DETAILS
# ======================================================

st.subheader("📋 Consumption Details")

st.dataframe(
    consumption.sort_values(
        ["Date", "Chemical"]
    ),
    use_container_width=True,
    hide_index=True,
    height=450
)

# ======================================================
# DOWNLOAD REPORT
# ======================================================

csv = consumption.to_csv(
    index=False
).encode("utf-8")

st.download_button(
    "📥 Download Consumption Report",
    csv,
    file_name="Consumption_Report.csv",
    mime="text/csv"
)
