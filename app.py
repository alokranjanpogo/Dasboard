import streamlit as st
import pandas as pd
import plotly.express as px

from utils.loader import (
    build_master_stock,
    calculate_consumption,
    stock_health
)

# ==================================================
# PAGE CONFIG
# ==================================================

st.set_page_config(
    page_title="Chemical Dashboard",
    page_icon="🧪",
    layout="wide"
)

# ==================================================
# LOAD DATA
# ==================================================

master = build_master_stock()

if master.empty:
    st.error("No Excel data found.")
    st.stop()

consumption = calculate_consumption()

master["Date"] = pd.to_datetime(master["Date"])
consumption["Date"] = pd.to_datetime(consumption["Date"])

# ==================================================
# TITLE
# ==================================================

st.title("🧪 Chemical Stock & Consumption Dashboard")

# ==================================================
# SIDEBAR FILTERS
# ==================================================

st.sidebar.header("Filters")

years = ["All"] + sorted(
    master["Year"].unique().tolist()
)

selected_year = st.sidebar.selectbox(
    "Year",
    years
)

chemicals = ["All"] + sorted(
    master["Chemical"].unique().tolist()
)

selected_chemical = st.sidebar.selectbox(
    "Chemical",
    chemicals
)

st.sidebar.subheader("Date Range")

start_date = st.sidebar.date_input(
    "Start Date",
    value=master["Date"].min()
)

end_date = st.sidebar.date_input(
    "End Date",
    value=master["Date"].max()
)

# ==================================================
# FILTER DATA
# ==================================================

inventory = master.copy()

if selected_year != "All":
    inventory = inventory[
        inventory["Year"] == selected_year
    ]

if selected_chemical != "All":
    inventory = inventory[
        inventory["Chemical"]
        == selected_chemical
    ]

inventory = inventory[
    (inventory["Date"] >= pd.to_datetime(start_date))
    &
    (inventory["Date"] <= pd.to_datetime(end_date))
]

display = stock_health(
    inventory.copy()
)

cons = consumption.copy()

if selected_year != "All":
    cons = cons[
        cons["Year"] == selected_year
    ]

if selected_chemical != "All":
    cons = cons[
        cons["Chemical"]
        == selected_chemical
    ]

cons = cons[
    (cons["Date"] >= pd.to_datetime(start_date))
    &
    (cons["Date"] <= pd.to_datetime(end_date))
]

# ==================================================
# MENU
# ==================================================

page = st.sidebar.radio(
    "Dashboard",
    [
        "Executive Dashboard",
        "Consumption Analysis",
        "Inventory Health",
        "Procurement Planning"
    ]
)

# ==================================================
# EXECUTIVE DASHBOARD
# ==================================================

if page == "Executive Dashboard":

    st.header("📊 Executive Dashboard")

    selected_exec_chemical = st.selectbox(
        "🧪 Select Chemical",
        sorted(display["Chemical"].unique())
    )

    chemical_df = display[
        display["Chemical"] == selected_exec_chemical
    ]

    latest_row = (
        chemical_df
        .sort_values("Date")
        .iloc[-1]
    )

    st.markdown("---")

    c1, c2, c3, c4, c5 = st.columns(5)

    with c1:
        st.metric(
            "🧪 Chemical",
            latest_row["Chemical"]
        )

    with c2:
        st.metric(
            "📦 Stock",
            f"{latest_row['Available Stock']:.2f} Ton"
        )

    with c3:
        st.metric(
            "📅 Available Days",
            f"{latest_row['Available Days']:.1f} Days"
        )

    with c4:
        st.metric(
            "⚙️ Daily Requirement",
            f"{latest_row['Daily Requirement']:.2f} Ton"
        )

    with c5:
        st.metric(
            "🏭 Vendor",
            latest_row["Vendor"]
        )

    st.markdown("---")

    status = latest_row["Status"]

    if status == "Healthy":
        st.success(
            "✅ Inventory Status : HEALTHY"
        )

    elif status == "Warning":
        st.warning(
            "⚠️ Inventory Status : WARNING"
        )

    else:
        st.error(
            "🚨 Inventory Status : CRITICAL"
        )

    # =====================================
    # STOCK TREND
    # =====================================

    st.subheader(
        f"📈 Stock Trend : {selected_exec_chemical}"
    )

    history = master[
        master["Chemical"]
        == selected_exec_chemical
    ].copy()

    fig = px.line(
        history,
        x="Date",
        y="Available Stock",
        markers=True
    )

    fig.update_layout(
        template="plotly_white",
        yaxis_title="Available Stock (Ton)",
        xaxis_title="Date"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # =====================================
    # CONSUMPTION TREND
    # =====================================

    st.subheader(
        f"📉 Consumption Trend : {selected_exec_chemical}"
    )

    chem_consumption = cons[
        cons["Chemical"]
        == selected_exec_chemical
    ]

    fig = px.bar(
        chem_consumption,
        x="Date",
        y="Consumption",
        color="Consumption",
        text="Consumption"
    )

    fig.update_layout(
        template="plotly_white",
        yaxis_title="Consumption (Ton)"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # =====================================
    # PROCUREMENT STATUS
    # =====================================

    required_qty = max(
        latest_row["3 Month Requirement"]
        - latest_row["Available Stock"],
        0
    )

    st.subheader(
        "🚚 Procurement Recommendation"
    )

    p1, p2, p3 = st.columns(3)

    with p1:
        st.metric(
            "3 Month Requirement",
            f"{latest_row['3 Month Requirement']:.2f} Ton"
        )

    with p2:
        st.metric(
            "Current Stock",
            f"{latest_row['Available Stock']:.2f} Ton"
        )

    with p3:
        st.metric(
            "Required Qty",
            f"{required_qty:.2f} Ton"
        )

    if required_qty > 0:

        st.error(
            f"""
            Procurement Required

            Quantity : {required_qty:.2f} Ton

            Vendor : {latest_row['Vendor']}
            """
        )

    else:

        st.success(
            "✅ Procurement not required."
        )

    # =====================================
    # INVENTORY HISTORY
    # =====================================

    st.subheader(
        "📋 Historical Inventory Records"
    )

    st.dataframe(
        history.sort_values(
            "Date",
            ascending=False
        ),
        use_container_width=True,
        hide_index=True
    )

# ==================================================
# CONSUMPTION ANALYSIS
# ==================================================

elif page == "Consumption Analysis":

    st.header("📈 Consumption Analysis")

    selected_chemical_ca = st.selectbox(
        "🧪 Select Chemical",
        sorted(cons["Chemical"].unique()),
        key="consumption_chemical"
    )

    chem_df = cons[
        cons["Chemical"] == selected_chemical_ca
    ]

    if chem_df.empty:
        st.warning("No data available.")
        st.stop()

    latest = (
        chem_df
        .sort_values("Date")
        .iloc[-1]
    )

    # ====================================
    # KPI SECTION
    # ====================================

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric(
            "Chemical",
            selected_chemical_ca
        )

    with c2:
        st.metric(
            "Total Consumption",
            f"{chem_df['Consumption'].sum():.2f} Ton"
        )

    with c3:
        st.metric(
            "Average Consumption",
            f"{chem_df['Consumption'].mean():.2f} Ton"
        )

    with c4:
        st.metric(
            "Maximum Consumption",
            f"{chem_df['Consumption'].max():.2f} Ton"
        )

    st.divider()

    # ====================================
    # DAILY CONSUMPTION
    # ====================================

    st.subheader(
        f"📊 Daily Consumption Trend : {selected_chemical_ca}"
    )

    fig = px.line(
        chem_df,
        x="Date",
        y="Consumption",
        markers=True
    )

    fig.update_layout(
        template="plotly_white",
        yaxis_title="Consumption (Ton)"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # ====================================
    # STOCK TREND
    # ====================================

    st.subheader(
        f"📦 Stock Trend : {selected_chemical_ca}"
    )

    fig = px.line(
        chem_df,
        x="Date",
        y="Available Stock",
        markers=True
    )

    fig.update_layout(
        template="plotly_white",
        yaxis_title="Available Stock (Ton)"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # ====================================
    # WEEKLY CONSUMPTION
    # ====================================

    st.subheader(
        "📅 Weekly Consumption"
    )

    weekly = (
        chem_df
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
        text="Consumption"
    )

    fig.update_layout(
        template="plotly_white",
        yaxis_title="Consumption (Ton)"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # ====================================
    # MONTHLY CONSUMPTION
    # ====================================

    st.subheader(
        "📆 Monthly Consumption"
    )

    monthly = (
        chem_df
        .groupby(
            "Month",
            as_index=False
        )["Consumption"]
        .sum()
    )

    fig = px.bar(
        monthly,
        x="Month",
        y="Consumption",
        text="Consumption"
    )

    fig.update_layout(
        template="plotly_white",
        yaxis_title="Consumption (Ton)"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # ====================================
    # YEARLY CONSUMPTION
    # ====================================

    st.subheader(
        "📈 Yearly Consumption"
    )

    yearly = (
        chem_df
        .groupby(
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

    fig.update_layout(
        template="plotly_white",
        yaxis_title="Consumption (Ton)"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # ====================================
    # DETAILS TABLE
    # ====================================

    st.subheader(
        "📋 Consumption Details"
    )

    st.dataframe(
        chem_df.sort_values(
            "Date",
            ascending=False
        ),
        use_container_width=True,
        hide_index=True
    )
# ==================================================
# INVENTORY HEALTH
# ==================================================

# ==================================================
# INVENTORY HEALTH
# ==================================================

elif page == "Inventory Health":

    st.header("📦 Inventory Health Dashboard")

    # =====================================
    # LATEST RECORD OF EACH CHEMICAL
    # =====================================

    latest_inventory = (
        display
        .sort_values("Date")
        .groupby("Chemical")
        .tail(1)
        .copy()
    )

    # =====================================
    # KPI CARDS
    # =====================================

    critical = len(
        latest_inventory[
            latest_inventory["Status"] == "Critical"
        ]
    )

    warning = len(
        latest_inventory[
            latest_inventory["Status"] == "Warning"
        ]
    )

    healthy = len(
        latest_inventory[
            latest_inventory["Status"] == "Healthy"
        ]
    )

    c1, c2, c3 = st.columns(3)

    with c1:
        st.error(
            f"🔴 Critical Chemicals : {critical}"
        )

    with c2:
        st.warning(
            f"🟡 Warning Chemicals : {warning}"
        )

    with c3:
        st.success(
            f"🟢 Healthy Chemicals : {healthy}"
        )

    st.divider()

    # =====================================
    # AVAILABLE DAYS
    # =====================================

    st.subheader(
        "📅 Available Days by Chemical"
    )

    fig = px.bar(
        latest_inventory,
        x="Chemical",
        y="Available Days",
        color="Status",
        text=latest_inventory[
            "Available Days"
        ].round(1),
        color_discrete_map={
            "Healthy": "green",
            "Warning": "orange",
            "Critical": "red"
        },
        height=600
    )

    fig.update_traces(
        textposition="outside"
    )

    fig.update_layout(
        template="plotly_white",
        xaxis_title="Chemical",
        yaxis_title="Available Days",
        showlegend=True
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.divider()

    # =====================================
    # AVAILABLE STOCK
    # =====================================

    st.subheader(
        "📦 Available Stock by Chemical"
    )

    fig = px.bar(
        latest_inventory,
        x="Chemical",
        y="Available Stock",
        color="Status",
        text=latest_inventory[
            "Available Stock"
        ].round(2),
        color_discrete_map={
            "Healthy": "green",
            "Warning": "orange",
            "Critical": "red"
        },
        height=600
    )

    fig.update_traces(
        textposition="outside"
    )

    fig.update_layout(
        template="plotly_white",
        xaxis_title="Chemical",
        yaxis_title="Available Stock (Ton)"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.divider()

    # =====================================
    # STATUS DONUT
    # =====================================

    st.subheader(
        "🟢 Inventory Status Distribution"
    )

    health = (
        latest_inventory
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
        hole=0.60,
        color="Status",
        color_discrete_map={
            "Healthy": "green",
            "Warning": "orange",
            "Critical": "red"
        }
    )

    fig.update_layout(
        template="plotly_white",
        height=500
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.divider()

    # =====================================
    # CRITICAL CHEMICALS
    # =====================================

    st.subheader(
        "🚨 Critical Chemical Alert"
    )

    critical_df = latest_inventory[
        latest_inventory["Status"] == "Critical"
    ]

    if critical_df.empty:

        st.success(
            "✅ No Critical Chemicals Found"
        )

    else:

        st.error(
            f"{len(critical_df)} Critical Chemicals Require Immediate Attention"
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
            use_container_width=True,
            hide_index=True
        )

    st.divider()

    # =====================================
    # INVENTORY TABLE
    # =====================================

    st.subheader(
        "📋 Current Inventory Status"
    )

    st.dataframe(
        latest_inventory.sort_values(
            "Available Days"
        ),
        use_container_width=True,
        hide_index=True,
        height=450
    )

    st.divider()

    # =====================================
    # DOWNLOAD REPORT
    # =====================================

    csv = latest_inventory.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        "📥 Download Inventory Report",
        csv,
        file_name="Inventory_Health_Report.csv",
        mime="text/csv"
    )
# ==================================================
# PROCUREMENT PLANNING
# ==================================================

# ==================================================
# PROCUREMENT PLANNING
# ==================================================

elif page == "Procurement Planning":

    st.header("🚚 Procurement Planning Dashboard")

    # =====================================
    # LATEST RECORD OF EACH CHEMICAL
    # =====================================

    latest = (
        display
        .sort_values("Date")
        .groupby("Chemical")
        .tail(1)
        .copy()
    )

    # =====================================
    # PROCUREMENT CALCULATION
    # =====================================

    latest["Required Qty"] = (
        latest["3 Month Requirement"]
        - latest["Available Stock"]
    )

    latest["Required Qty"] = (
        latest["Required Qty"]
        .clip(lower=0)
    )

    # =====================================
    # PROCUREMENT STATUS
    # =====================================

    latest["Procurement Status"] = (
        latest["Required Qty"]
        .apply(
            lambda x:
            "Required"
            if x > 0
            else "Not Required"
        )
    )

    # =====================================
    # KPI CARDS
    # =====================================

    total_required = latest[
        "Required Qty"
    ].sum()

    chemicals_to_buy = len(
        latest[
            latest["Required Qty"] > 0
        ]
    )

    vendors = latest["Vendor"].nunique()

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric(
            "📦 Chemicals to Procure",
            chemicals_to_buy
        )

    with c2:
        st.metric(
            "🚚 Required Quantity",
            f"{total_required:.2f} Ton"
        )

    with c3:
        st.metric(
            "🏭 Vendors",
            vendors
        )

    st.divider()

    # =====================================
    # PROCUREMENT TABLE
    # =====================================

    st.subheader(
        "📋 Procurement Requirement"
    )

    procurement_df = latest[
        latest["Required Qty"] > 0
    ].sort_values(
        "Required Qty",
        ascending=False
    )

    if procurement_df.empty:

        st.success(
            "✅ No Procurement Required"
        )

    else:

        st.dataframe(
            procurement_df[
                [
                    "Chemical",
                    "Vendor",
                    "Available Stock",
                    "3 Month 
