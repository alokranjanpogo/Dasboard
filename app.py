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

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric(
            "Total Consumption",
            f"{cons['Consumption'].sum():,.2f} Ton"
        )

    with c2:
        st.metric(
            "Average Consumption",
            f"{cons['Consumption'].mean():,.2f} Ton"
        )

    with c3:
        st.metric(
            "Maximum Consumption",
            f"{cons['Consumption'].max():,.2f} Ton"
        )

    st.subheader("Daily Consumption Trend")

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

    fig.update_layout(
        yaxis_title="Consumption (Ton)"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.subheader("Chemical-wise Consumption")

    chem = (
        cons.groupby(
            "Chemical",
            as_index=False
        )["Consumption"]
        .sum()
    )

    fig = px.bar(
        chem,
        x="Chemical",
        y="Consumption",
        text="Consumption",
        color="Chemical"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# ==================================================
# INVENTORY HEALTH
# ==================================================

elif page == "Inventory Health":

    st.header("📦 Inventory Health")

    fig = px.bar(
        display,
        x="Chemical",
        y="Available Days",
        color="Status",
        text="Available Days"
    )

    fig.update_layout(
        yaxis_title="Available Days"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    critical_df = display[
        display["Status"] == "Critical"
    ]

    if not critical_df.empty:

        st.error(
            f"{len(critical_df)} Critical Chemicals Found"
        )

        st.dataframe(
            critical_df,
            use_container_width=True
        )

    st.dataframe(
        display,
        use_container_width=True
    )

# ==================================================
# PROCUREMENT
# ==================================================

elif page == "Procurement Planning":

    st.header("🚚 Procurement Planning")

    latest_date = display["Date"].max()

    latest = display[
        display["Date"] == latest_date
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
        text="Required Qty",
        color="Vendor"
    )

    fig.update_layout(
        yaxis_title="Quantity Required (Ton)"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )
