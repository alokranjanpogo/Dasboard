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

stock = load_stock_master()

consumption = load_consumption_master()

po_tracker = load_po_tracker()

chemical_master = load_chemical_master()

if stock.empty:
    st.error(
        "Stock Master not found."
    )
    st.stop()

stock = stock_health(stock)

# =====================================================
# TITLE
# =====================================================

st.title(
    "🧪 Chemical Stock & Consumption Dashboard"
)

# =====================================================
# SIDEBAR
# =====================================================

st.sidebar.header(
    "Dashboard Navigation"
)

page = st.sidebar.radio(
    "Select Dashboard",
    [
        "Executive Dashboard",
        "Consumption Analysis",
        "Inventory Health",
        "Procurement Planning",
        "PO Tracker",
        "Location Analysis",
        "Shift Analysis",
        "Vendor Analysis"
    ]
)

# =====================================================
# DATE FILTER
# =====================================================

st.sidebar.subheader(
    "Date Range"
)

start_date = st.sidebar.date_input(
    "Start Date",
    value=stock["Date"].min()
)

end_date = st.sidebar.date_input(
    "End Date",
    value=stock["Date"].max()
)

# =====================================================
# EXECUTIVE DASHBOARD
# =====================================================

if page == "Executive Dashboard":

    st.header("📊 Executive Dashboard")

    selected_exec_chemical = st.selectbox(
        "🧪 Select Chemical",
        sorted(
            stock["Chemical"]
            .dropna()
            .unique()
            .tolist()
        )
    )

    chemical_stock = stock[
        stock["Chemical"]
        == selected_exec_chemical
    ].copy()

    chemical_stock = chemical_stock.sort_values(
        "Date"
    )

    if chemical_stock.empty:

        st.warning(
            "No data found."
        )

        st.stop()

    latest_row = chemical_stock.iloc[-1]

    # ======================================
    # CHEMICAL MASTER DATA
    # ======================================

    chemical_info = pd.DataFrame()

    if not chemical_master.empty:

        chemical_info = chemical_master[
            chemical_master["Chemical"]
            == selected_exec_chemical
        ]

    # ======================================
    # KPI CARDS
    # ======================================

    st.markdown("---")

    c1, c2, c3, c4, c5 = st.columns(5)

    with c1:
        st.metric(
            "🧪 Chemical",
            latest_row["Chemical"]
        )

    with c2:
        st.metric(
            "📦 Current Stock",
            f"{latest_row['Available Stock']:.2f}"
        )

    with c3:
        st.metric(
            "📅 Available Days",
            f"{latest_row['Available Days']:.1f}"
        )

    with c4:

        current_consumption = 0

        if not consumption.empty:

            current_consumption = round(
                consumption[
                    consumption["Chemical"]
                    ==
                    selected_exec_chemical
                ]["Consumption"]
                .mean(),
                2
            )

        st.metric(
            "⚙ Daily Consumption",
            current_consumption
        )

    with c5:

        st.metric(
            "🏭 Vendor",
            latest_row["Vendor"]
        )

    # ======================================
    # SECOND KPI ROW
    # ======================================

    if not chemical_info.empty:

        lead_time = chemical_info.iloc[0][
            "Lead Time"
        ]

        safety_stock = chemical_info.iloc[0][
            "Safety Stock"
        ]

        reorder_level = chemical_info.iloc[0][
            "Reorder Level"
        ]

        k1, k2, k3 = st.columns(3)

        with k1:

            st.metric(
                "🚚 Lead Time",
                lead_time
            )

        with k2:

            st.metric(
                "🛡 Safety Stock",
                safety_stock
            )

        with k3:

            st.metric(
                "🔄 Reorder Level",
                reorder_level
            )

    st.markdown("---")

    # ======================================
    # INVENTORY STATUS
    # ======================================

    status = latest_row["Status"]

    if status == "Healthy":

        st.success(
            "✅ Inventory Status : HEALTHY"
        )

    elif status == "Warning":

        st.warning(
            "⚠ Inventory Status : WARNING"
        )

    else:

        st.error(
            "🚨 Inventory Status : CRITICAL"
        )

    # ======================================
    # STOCK TREND
    # ======================================

    st.subheader(
        f"📈 Stock Trend : {selected_exec_chemical}"
    )

    fig_stock = px.line(
        chemical_stock,
        x="Date",
        y="Available Stock",
        markers=True
    )

    fig_stock.update_layout(
        template="plotly_white",
        height=500,
        yaxis_title="Available Stock",
        xaxis_title="Date"
    )

    st.plotly_chart(
        fig_stock,
        use_container_width=True
    )

    # ======================================
    # CONSUMPTION TREND
    # ======================================

    if not consumption.empty:

        st.subheader(
            f"📉 Consumption Trend : {selected_exec_chemical}"
        )

        chemical_consumption = consumption[
            consumption["Chemical"]
            ==
            selected_exec_chemical
        ]

        if not chemical_consumption.empty:

            daily = (
                chemical_consumption
                .groupby("Date")
                ["Consumption"]
                .sum()
                .reset_index()
            )

            fig_cons = px.bar(
                daily,
                x="Date",
                y="Consumption",
                text="Consumption",
                color="Consumption"
            )

            fig_cons.update_layout(
                template="plotly_white",
                height=500
            )

            st.plotly_chart(
                fig_cons,
                use_container_width=True
            )

    # ======================================
    # OPEN PO STATUS
    # ======================================

    st.subheader(
        "🚚 Open Purchase Orders"
    )

    po_data = pd.DataFrame()

    if not po_tracker.empty:

        po_data = po_tracker[
            po_tracker["Chemical"]
            ==
            selected_exec_chemical
        ]

    if po_data.empty:

        st.info(
            "No PO found."
        )

    else:

        open_po_qty = po_data[
            "Pending Qty"
        ].sum()

        st.metric(
            "Pending Quantity",
            round(open_po_qty, 2)
        )

        st.dataframe(
            po_data,
            hide_index=True,
            use_container_width=True
        )

    # ======================================
    # PROCUREMENT RECOMMENDATION
    # ======================================

    st.markdown("---")

    st.subheader(
        "🛒 Procurement Recommendation"
    )

    requirement = latest_row[
        "3 Month Requirement"
    ]

    current_stock = latest_row[
        "Available Stock"
    ]

    pending_po = 0

    if not po_data.empty:

        pending_po = po_data[
            "Pending Qty"
        ].sum()

    projected_stock = (
        current_stock
        + pending_po
    )

    required_qty = max(
        requirement
        - projected_stock,
        0
    )

    p1, p2, p3, p4 = st.columns(4)

    with p1:

        st.metric(
            "Current Stock",
            round(
                current_stock,
                2
            )
        )

    with p2:

        st.metric(
            "Open PO Qty",
            round(
                pending_po,
                2
            )
        )

    with p3:

        st.metric(
            "Projected Stock",
            round(
                projected_stock,
                2
            )
        )

    with p4:

        st.metric(
            "Required Qty",
            round(
                required_qty,
                2
            )
        )

    if required_qty > 0:

        st.error(
            f"""
            🚨 PROCUREMENT REQUIRED

            Required Quantity :
            {required_qty:.2f}

            Vendor :
            {latest_row['Vendor']}
            """
        )

    else:

        st.success(
            "✅ Current inventory is sufficient."
        )

    # ======================================
    # HISTORY
    # ======================================

    st.markdown("---")

    st.subheader(
        "📋 Historical Stock Records"
    )

    st.dataframe(
        chemical_stock.sort_values(
            "Date",
            ascending=False
        ),
        hide_index=True,
        use_container_width=True
    )
# =====================================================
# CONSUMPTION ANALYSIS
# =====================================================

elif page == "Consumption Analysis":

    st.header("📈 Consumption Analysis")

    if consumption.empty:

        st.warning(
            "No Consumption Data Found"
        )

        st.stop()

    selected_chemical = st.selectbox(
        "🧪 Select Chemical",
        sorted(
            consumption["Chemical"]
            .unique()
            .tolist()
        ),
        key="consumption_page"
    )

    chem_df = consumption[
        consumption["Chemical"]
        == selected_chemical
    ].copy()

    if chem_df.empty:

        st.warning("No Data Found")

        st.stop()

    # ==================================
    # KPI CARDS
    # ==================================

    total_consumption = (
        chem_df["Consumption"]
        .sum()
    )

    avg_consumption = (
        chem_df["Consumption"]
        .mean()
    )

    max_consumption = (
        chem_df["Consumption"]
        .max()
    )

    locations_count = (
        chem_df["Location"]
        .nunique()
    )

    st.markdown("---")

    c1, c2, c3, c4 = st.columns(4)

    with c1:

        st.metric(
            "Total Consumption",
            round(
                total_consumption,
                2
            )
        )

    with c2:

        st.metric(
            "Average Consumption",
            round(
                avg_consumption,
                2
            )
        )

    with c3:

        st.metric(
            "Maximum Consumption",
            round(
                max_consumption,
                2
            )
        )

    with c4:

        st.metric(
            "Locations",
            locations_count
        )

    # ==================================
    # DAILY TREND
    # ==================================

    st.markdown("---")

    st.subheader(
        f"📅 Daily Consumption Trend : {selected_chemical}"
    )

    daily = (
        chem_df
        .groupby("Date")
        ["Consumption"]
        .sum()
        .reset_index()
    )

    fig_daily = px.line(
        daily,
        x="Date",
        y="Consumption",
        markers=True
    )

    fig_daily.update_layout(
        template="plotly_white",
        height=500
    )

    st.plotly_chart(
        fig_daily,
        use_container_width=True
    )

    # ==================================
    # WEEKLY TREND
    # ==================================

    st.subheader(
        "📆 Weekly Consumption"
    )

    weekly = (
        chem_df
        .groupby(
            "Week",
            as_index=False
        )["Consumption"]
        .sum()
    )

    fig_weekly = px.bar(
        weekly,
        x="Week",
        y="Consumption",
        text="Consumption",
        color="Consumption"
    )

    fig_weekly.update_layout(
        template="plotly_white",
        height=500
    )

    st.plotly_chart(
        fig_weekly,
        use_container_width=True
    )

    # ==================================
    # MONTHLY TREND
    # ==================================

    st.subheader(
        "📅 Monthly Consumption"
    )

    monthly = (
        chem_df
        .groupby(
            "Month",
            as_index=False
        )["Consumption"]
        .sum()
    )

    fig_month = px.bar(
        monthly,
        x="Month",
        y="Consumption",
        text="Consumption",
        color="Consumption"
    )

    fig_month.update_layout(
        template="plotly_white",
        height=500
    )

    st.plotly_chart(
        fig_month,
        use_container_width=True
    )

    # ==================================
    # YEARLY TREND
    # ==================================

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

    fig_year = px.line(
        yearly,
        x="Year",
        y="Consumption",
        markers=True
    )

    fig_year.update_layout(
        template="plotly_white",
        height=500
    )

    st.plotly_chart(
        fig_year,
        use_container_width=True
    )

    # ==================================
    # SHIFT ANALYSIS
    # ==================================

    st.markdown("---")

    st.subheader(
        "🏭 Shift-wise Consumption"
    )

    shift_data = (
        chem_df
        .groupby(
            "Shift",
            as_index=False
        )["Consumption"]
        .sum()
    )

    fig_shift = px.pie(
        shift_data,
        names="Shift",
        values="Consumption",
        hole=0.55
    )

    fig_shift.update_layout(
        height=500
    )

    st.plotly_chart(
        fig_shift,
        use_container_width=True
    )

    # ==================================
    # LOCATION ANALYSIS
    # ==================================

    st.subheader(
        "📍 Location-wise Consumption"
    )

    location_data = (
        chem_df
        .groupby(
            "Location",
            as_index=False
        )["Consumption"]
        .sum()
    )

    fig_location = px.bar(
        location_data,
        x="Location",
        y="Consumption",
        text="Consumption",
        color="Consumption"
    )

    fig_location.update_layout(
        template="plotly_white",
        height=550
    )

    st.plotly_chart(
        fig_location,
        use_container_width=True
    )

    # ==================================
    # PART A / PART B / FH
    # ==================================

    st.subheader(
        "🏭 Consumption Distribution"
    )

    fig_location_pie = px.pie(
        location_data,
        names="Location",
        values="Consumption",
        hole=0.6
    )

    st.plotly_chart(
        fig_location_pie,
        use_container_width=True
    )

    # ==================================
    # SHIFT x LOCATION HEATMAP
    # ==================================

    st.subheader(
        "🔥 Shift vs Location"
    )

    heat = (
        chem_df
        .pivot_table(
            index="Location",
            columns="Shift",
            values="Consumption",
            aggfunc="sum"
        )
        .reset_index()
    )

    st.dataframe(
        heat,
        use_container_width=True,
        hide_index=True
    )

    # ==================================
    # RAW DATA
    # ==================================

    st.markdown("---")

    st.subheader(
        "📋 Consumption Records"
    )

    st.dataframe(
        chem_df.sort_values(
            "Date",
            ascending=False
        ),
        hide_index=True,
        use_container_width=True,
        height=450
    )

    # ==================================
    # DOWNLOAD
    # ==================================

    csv = (
        chem_df
        .to_csv(index=False)
        .encode("utf-8")
    )

    st.download_button(
        "📥 Download Consumption Report",
        csv,
        file_name=f"{selected_chemical}_Consumption_Report.csv",
        mime="text/csv"
    )
# =====================================================
# INVENTORY HEALTH
# =====================================================

elif page == "Inventory Health":

    st.header("📦 Inventory Health Dashboard")

    selected_chemical = st.selectbox(
        "🧪 Select Chemical",
        sorted(
            stock["Chemical"]
            .dropna()
            .unique()
            .tolist()
        ),
        key="inventory_page"
    )

    inventory = stock[
        stock["Chemical"]
        == selected_chemical
    ].copy()

    inventory = inventory.sort_values(
        "Date"
    )

    if inventory.empty:

        st.warning(
            "No Inventory Found"
        )

        st.stop()

    latest = inventory.iloc[-1]

    # =====================================
    # CHEMICAL MASTER DATA
    # =====================================

    safety_stock = 0
    reorder_level = 0
    lead_time = 0

    if not chemical_master.empty:

        chem_info = chemical_master[
            chemical_master["Chemical"]
            ==
            selected_chemical
        ]

        if not chem_info.empty:

            safety_stock = chem_info.iloc[0][
                "Safety Stock"
            ]

            reorder_level = chem_info.iloc[0][
                "Reorder Level"
            ]

            lead_time = chem_info.iloc[0][
                "Lead Time"
            ]

    # =====================================
    # OPEN PO
    # =====================================

    open_po = 0

    if not po_tracker.empty:

        po_filter = po_tracker[
            po_tracker["Chemical"]
            ==
            selected_chemical
        ]

        if not po_filter.empty:

            open_po = po_filter[
                "Pending Qty"
            ].sum()

    current_stock = latest[
        "Available Stock"
    ]

    projected_stock = (
        current_stock
        + open_po
    )

    available_days = latest[
        "Available Days"
    ]

    # =====================================
    # KPI CARDS
    # =====================================

    st.markdown("---")

    c1, c2, c3, c4 = st.columns(4)

    with c1:

        st.metric(
            "📦 Current Stock",
            round(
                current_stock,
                2
            )
        )

    with c2:

        st.metric(
            "📅 Available Days",
            round(
                available_days,
                1
            )
        )

    with c3:

        st.metric(
            "🚚 Open PO Qty",
            round(
                open_po,
                2
            )
        )

    with c4:

        st.metric(
            "📊 Projected Stock",
            round(
                projected_stock,
                2
            )
        )

    st.markdown("---")

    k1, k2, k3 = st.columns(3)

    with k1:

        st.metric(
            "🛡 Safety Stock",
            safety_stock
        )

    with k2:

        st.metric(
            "🔄 Reorder Level",
            reorder_level
        )

    with k3:

        st.metric(
            "⏳ Lead Time",
            lead_time
        )

    # =====================================
    # INVENTORY STATUS
    # =====================================

    st.markdown("---")

    status = latest["Status"]

    if status == "Healthy":

        st.success(
            "✅ HEALTHY INVENTORY"
        )

    elif status == "Warning":

        st.warning(
            "⚠ WARNING INVENTORY"
        )

    else:

        st.error(
            "🚨 CRITICAL INVENTORY"
        )

    # =====================================
    # STATUS CHECK
    # =====================================

    if current_stock <= safety_stock:

        st.error(
            "🚨 Current Stock Below Safety Stock"
        )

    elif current_stock <= reorder_level:

        st.warning(
            "⚠ Reorder Level Reached"
        )

    else:

        st.success(
            "✅ Inventory Above Reorder Level"
        )

    # =====================================
    # STOCK TREND
    # =====================================

    st.subheader(
        "📈 Available Stock Trend"
    )

    fig_stock = px.line(
        inventory,
        x="Date",
        y="Available Stock",
        markers=True
    )

    fig_stock.update_layout(
        template="plotly_white",
        height=500
    )

    st.plotly_chart(
        fig_stock,
        use_container_width=True
    )

    # =====================================
    # AVAILABLE DAYS TREND
    # =====================================

    st.subheader(
        "📅 Available Days Trend"
    )

    fig_days = px.line(
        inventory,
        x="Date",
        y="Available Days",
        markers=True
    )

    fig_days.update_layout(
        template="plotly_white",
        height=500
    )

    st.plotly_chart(
        fig_days,
        use_container_width=True
    )

    # =====================================
    # STOCK VS SAFETY STOCK
    # =====================================

    st.subheader(
        "📊 Stock vs Safety Stock"
    )

    compare_df = pd.DataFrame(
        {
            "Type": [
                "Current Stock",
                "Safety Stock",
                "Reorder Level",
                "Projected Stock"
            ],
            "Value": [
                current_stock,
                safety_stock,
                reorder_level,
                projected_stock
            ]
        }
    )

    fig_compare = px.bar(
        compare_df,
        x="Type",
        y="Value",
        color="Type",
        text="Value"
    )

    fig_compare.update_layout(
        template="plotly_white",
        height=500
    )

    st.plotly_chart(
        fig_compare,
        use_container_width=True
    )

    # =====================================
    # INVENTORY HISTORY
    # =====================================

    st.subheader(
        "📋 Inventory History"
    )

    st.dataframe(
        inventory.sort_values(
            "Date",
            ascending=False
        ),
        hide_index=True,
        use_container_width=True,
        height=450
    )

    # =====================================
    # DOWNLOAD REPORT
    # =====================================

    csv = inventory.to_csv(
        index=False
    ).encode(
        "utf-8"
    )

    st.download_button(
        "📥 Download Inventory Report",
        csv,
        file_name=f"{selected_chemical}_Inventory_Report.csv",
        mime="text/csv"
    )
    
# =====================================================
# PROCUREMENT PLANNING
# =====================================================

elif page == "Procurement Planning":

    st.header("🚚 Procurement Planning Dashboard")

    selected_chemical = st.selectbox(
        "🧪 Select Chemical",
        sorted(
            stock["Chemical"]
            .dropna()
            .unique()
            .tolist()
        ),
        key="procurement_page"
    )

    chemical_stock = stock[
        stock["Chemical"]
        ==
        selected_chemical
    ].copy()

    chemical_stock = (
        chemical_stock
        .sort_values("Date")
    )

    latest = chemical_stock.iloc[-1]

    # =====================================
    # CHEMICAL MASTER DATA
    # =====================================

    lead_time = 0
    safety_stock = 0
    reorder_level = 0

    if not chemical_master.empty:

        info = chemical_master[
            chemical_master["Chemical"]
            ==
            selected_chemical
        ]

        if not info.empty:

            lead_time = info.iloc[0][
                "Lead Time"
            ]

            safety_stock = info.iloc[0][
                "Safety Stock"
            ]

            reorder_level = info.iloc[0][
                "Reorder Level"
            ]

    # =====================================
    # PO DATA
    # =====================================

    open_po_qty = 0

    if not po_tracker.empty:

        chemical_po = po_tracker[
            po_tracker["Chemical"]
            ==
            selected_chemical
        ]

        if not chemical_po.empty:

            open_po_qty = (
                chemical_po[
                    "Pending Qty"
                ]
                .sum()
            )

    else:

        chemical_po = pd.DataFrame()

    current_stock = (
        latest[
            "Available Stock"
        ]
    )

    three_month_requirement = (
        latest[
            "3 Month Requirement"
        ]
    )

    projected_stock = (
        current_stock
        + open_po_qty
    )

    required_qty = max(
        three_month_requirement
        - projected_stock,
        0
    )

    # =====================================
    # KPI ROW
    # =====================================

    c1, c2, c3, c4 = st.columns(4)

    with c1:

        st.metric(
            "📦 Current Stock",
            round(
                current_stock,
                2
            )
        )

    with c2:

        st.metric(
            "🚚 Open PO Qty",
            round(
                open_po_qty,
                2
            )
        )

    with c3:

        st.metric(
            "📊 Projected Stock",
            round(
                projected_stock,
                2
            )
        )

    with c4:

        st.metric(
            "🔄 Required Qty",
            round(
                required_qty,
                2
            )
        )

    st.markdown("---")

    c5, c6, c7 = st.columns(3)

    with c5:

        st.metric(
            "📅 Lead Time",
            lead_time
        )

    with c6:

        st.metric(
            "🛡 Safety Stock",
            safety_stock
        )

    with c7:

        st.metric(
            "⚠ Reorder Level",
            reorder_level
        )

    # =====================================
    # PROCUREMENT DECISION
    # =====================================

    st.subheader(
        "🛒 Procurement Recommendation"
    )

    if required_qty > 0:

        st.error(
            f"""
            🚨 PROCUREMENT REQUIRED

            Required Quantity :
            {required_qty:.2f}

            Vendor :
            {latest['Vendor']}
            """
        )

    else:

        st.success(
            """
            ✅ Inventory Available

            No Immediate Procurement Required
            """
        )

    # =====================================
    # AVAILABLE VS REQUIREMENT
    # =====================================

    st.subheader(
        "📊 Stock vs Requirement"
    )

    compare = pd.DataFrame(
        {
            "Category": [
                "Current Stock",
                "Open PO",
                "Projected Stock",
                "3 Month Requirement"
            ],
            "Value": [
                current_stock,
                open_po_qty,
                projected_stock,
                three_month_requirement
            ]
        }
    )

    fig = px.bar(
        compare,
        x="Category",
        y="Value",
        color="Category",
        text="Value"
    )

    fig.update_layout(
        template="plotly_white",
        height=550
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # =====================================
    # INVENTORY HISTORY
    # =====================================

    st.subheader(
        "📈 Historical Stock Trend"
    )

    fig = px.line(
        chemical_stock,
        x="Date",
        y="Available Stock",
        markers=True
    )

    fig.update_layout(
        template="plotly_white",
        height=500
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # =====================================
    # PO SUMMARY
    # =====================================

    st.subheader(
        "🚚 Related Purchase Orders"
    )

    if chemical_po.empty:

        st.info(
            "No Purchase Orders Found"
        )

    else:

        st.dataframe(
            chemical_po,
            hide_index=True,
            use_container_width=True
        )

    # =====================================
    # REORDER PRIORITY
    # =====================================

    st.subheader(
        "🎯 Reorder Priority"
    )

    available_days = latest[
        "Available Days"
    ]

    if available_days < 15:

        priority = "High"

    elif available_days < 45:

        priority = "Medium"

    else:

        priority = "Low"

    priority_df = pd.DataFrame(
        {
            "Chemical": [
                selected_chemical
            ],
            "Available Days": [
                available_days
            ],
            "Vendor": [
                latest["Vendor"]
            ],
            "Priority": [
                priority
            ]
        }
    )

    st.dataframe(
        priority_df,
        hide_index=True,
        use_container_width=True
    )

    # =====================================
    # DOWNLOAD REPORT
    # =====================================

    report = chemical_stock.copy()

    report["Open PO Qty"] = (
        open_po_qty
    )

    report["Projected Stock"] = (
        projected_stock
    )

    report["Required Qty"] = (
        required_qty
    )

    csv = (
        report
        .to_csv(index=False)
        .encode("utf-8")
    )

    st.download_button(
        "📥 Download Procurement Report",
        csv,
        file_name=f"{selected_chemical}_Procurement_Report.csv",
        mime="text/csv"
    )
# =====================================================
# PO TRACKER
# =====================================================

elif page == "PO Tracker":

    st.header("🚚 Purchase Order Tracker")

    if po_tracker.empty:

        st.warning(
            "No PO Data Found"
        )

        st.stop()

    selected_chemical = st.selectbox(
        "🧪 Select Chemical",
        sorted(
            po_tracker["Chemical"]
            .dropna()
            .unique()
            .tolist()
        ),
        key="po_page"
    )

    po_data = po_tracker[
        po_tracker["Chemical"]
        ==
        selected_chemical
    ].copy()

    # =====================================
    # KPI CARDS
    # =====================================

    total_po = len(po_data)

    open_po = len(
        po_data[
            po_data["Status"]
            == "Open"
        ]
    )

    pending_qty = (
        po_data["Pending Qty"]
        .sum()
    )

    received_qty = (
        po_data["Received Qty"]
        .sum()
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:

        st.metric(
            "PO Count",
            total_po
        )

    with c2:

        st.metric(
            "Open PO",
            open_po
        )

    with c3:

        st.metric(
            "Pending Qty",
            round(
                pending_qty,
                2
            )
        )

    with c4:

        st.metric(
            "Received Qty",
            round(
                received_qty,
                2
            )
        )

    # =====================================
    # STATUS DISTRIBUTION
    # =====================================

    st.subheader(
        "📊 PO Status Distribution"
    )

    status_df = (
        po_data
        .groupby(
            "Status",
            as_index=False
        )
        .size()
    )

    fig_status = px.pie(
        status_df,
        names="Status",
        values="size",
        hole=0.55
    )

    st.plotly_chart(
        fig_status,
        use_container_width=True
    )

    # =====================================
    # PENDING QTY
    # =====================================

    st.subheader(
        "📦 Pending Quantity"
    )

    fig_pending = px.bar(
        po_data,
        x="PO Number",
        y="Pending Qty",
        color="Vendor",
        text="Pending Qty"
    )

    fig_pending.update_layout(
        template="plotly_white",
        height=550
    )

    st.plotly_chart(
        fig_pending,
        use_container_width=True
    )

    # =====================================
    # VENDOR PERFORMANCE
    # =====================================

    st.subheader(
        "🏭 Vendor Distribution"
    )

    vendor_df = (
        po_data
        .groupby(
            "Vendor",
            as_index=False
        )[["Pending Qty"]]
        .sum()
    )

    fig_vendor = px.pie(
        vendor_df,
        names="Vendor",
        values="Pending Qty",
        hole=0.55
    )

    st.plotly_chart(
        fig_vendor,
        use_container_width=True
    )

    # =====================================
    # DELIVERY SCHEDULE
    # =====================================

    st.subheader(
        "📅 Delivery Schedule"
    )

    if "Expected Delivery Date" in po_data.columns:

        fig_delivery = px.bar(
            po_data,
            x="Expected Delivery Date",
            y="Pending Qty",
            color="Vendor"
        )

        st.plotly_chart(
            fig_delivery,
            use_container_width=True
        )

    # =====================================
    # FULL PO TABLE
    # =====================================

    st.subheader(
        "📋 Purchase Orders"
    )

    st.dataframe(
        po_data,
        hide_index=True,
        use_container_width=True
    )

    # =====================================
    # DOWNLOAD
    # =====================================

    csv = (
        po_data
        .to_csv(index=False)
        .encode("utf-8")
    )

    st.download_button(
        "📥 Download PO Report",
        csv,
        file_name=f"{selected_chemical}_PO_Report.csv",
        mime="text/csv"
    )
# =====================================================
# LOCATION ANALYSIS
# =====================================================

elif page == "Location Analysis":

    st.header("📍 Location Analysis")

    selected_chemical = st.selectbox(
        "🧪 Select Chemical",
        sorted(
            consumption["Chemical"]
            .unique()
        ),
        key="location_page"
    )

    df = consumption[
        consumption["Chemical"]
        ==
        selected_chemical
    ]

    location_df = (
        df.groupby(
            "Location",
            as_index=False
        )["Consumption"]
        .sum()
    )

    fig = px.bar(
        location_df,
        x="Location",
        y="Consumption",
        color="Location",
        text="Consumption"
    )

    fig.update_layout(
        template="plotly_white",
        height=600
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    fig2 = px.pie(
        location_df,
        names="Location",
        values="Consumption",
        hole=0.6
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )

    st.dataframe(
        location_df,
        use_container_width=True
    )
# =====================================================
# SHIFT ANALYSIS
# =====================================================

elif page == "Shift Analysis":

    st.header("🏭 Shift Analysis")

    selected_chemical = st.selectbox(
        "🧪 Select Chemical",
        sorted(
            consumption["Chemical"]
            .unique()
        ),
        key="shift_page"
    )

    df = consumption[
        consumption["Chemical"]
        ==
        selected_chemical
    ]

    shift_df = (
        df.groupby(
            "Shift",
            as_index=False
        )["Consumption"]
        .sum()
    )

    fig = px.pie(
        shift_df,
        names="Shift",
        values="Consumption",
        hole=0.60
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    fig2 = px.bar(
        shift_df,
        x="Shift",
        y="Consumption",
        color="Shift",
        text="Consumption"
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )

    st.dataframe(
        shift_df,
        use_container_width=True
    )
# =====================================================
# VENDOR ANALYSIS
# =====================================================

elif page == "Vendor Analysis":

    st.header("🏭 Vendor Analysis")

    selected_chemical = st.selectbox(
        "🧪 Select Chemical",
        sorted(
            stock["Chemical"]
            .dropna()
            .unique()
            .tolist()
        ),
        key="vendor_page"
    )

    # =====================================
    # STOCK DATA
    # =====================================

    vendor_stock = stock[
        stock["Chemical"]
        ==
        selected_chemical
    ].copy()

    vendor_stock = (
        vendor_stock
        .sort_values("Date")
        .groupby(
            ["Vendor", "Chemical"],
            as_index=False
        )
        .tail(1)
    )

    # =====================================
    # PO DATA
    # =====================================

    vendor_po = pd.DataFrame()

    if not po_tracker.empty:

        vendor_po = po_tracker[
            po_tracker["Chemical"]
            ==
            selected_chemical
        ]

    # =====================================
    # KPI
    # =====================================

    total_stock = (
        vendor_stock[
            "Available Stock"
        ]
        .sum()
    )

    vendor_count = (
        vendor_stock[
            "Vendor"
        ]
        .nunique()
    )

    pending_qty = 0

    if not vendor_po.empty:

        pending_qty = (
            vendor_po[
                "Pending Qty"
            ]
            .sum()
        )

    open_po = 0

    if not vendor_po.empty:

        open_po = len(
            vendor_po[
                vendor_po["Status"]
                == "Open"
            ]
        )

    c1, c2, c3, c4 = st.columns(4)

    with c1:

        st.metric(
            "Chemical",
            selected_chemical
        )

    with c2:

        st.metric(
            "Vendors",
            vendor_count
        )

    with c3:

        st.metric(
            "Available Stock",
            round(
                total_stock,
                2
            )
        )

    with c4:

        st.metric(
            "Open PO",
            open_po
        )

    st.markdown("---")

    # =====================================
    # VENDOR STOCK
    # =====================================

    st.subheader(
        f"📦 {selected_chemical} Stock by Vendor"
    )

    fig_stock = px.bar(
        vendor_stock,
        x="Vendor",
        y="Available Stock",
        text="Available Stock",
        color="Vendor"
    )

    fig_stock.update_layout(
        template="plotly_white",
        height=550
    )

    st.plotly_chart(
        fig_stock,
        use_container_width=True
    )

    # =====================================
    # PO PENDING
    # =====================================

    if not vendor_po.empty:

        st.subheader(
            f"🚚 {selected_chemical} Pending Qty by Vendor"
        )

        vendor_pending = (
            vendor_po
            .groupby(
                "Vendor",
                as_index=False
            )["Pending Qty"]
            .sum()
        )

        fig_pending = px.bar(
            vendor_pending,
            x="Vendor",
            y="Pending Qty",
            text="Pending Qty",
            color="Vendor"
        )

        fig_pending.update_layout(
            template="plotly_white",
            height=550
        )

        st.plotly_chart(
            fig_pending,
            use_container_width=True
        )

    # =====================================
    # STOCK SHARE
    # =====================================

    st.subheader(
        f"📊 {selected_chemical} Vendor Share"
    )

    fig_pie = px.pie(
        vendor_stock,
        names="Vendor",
        values="Available Stock",
        hole=0.60
    )

    st.plotly_chart(
        fig_pie,
        use_container_width=True
    )

    # =====================================
    # VENDOR SUMMARY
    # =====================================

    st.subheader(
        "📋 Vendor Summary"
    )

    summary = (
        vendor_stock[
            [
                "Vendor",
                "Chemical",
                "Available Stock",
                "Available Days",
                "Status"
            ]
        ]
        .sort_values(
            "Available Stock",
            ascending=False
        )
    )

    st.dataframe(
        summary,
        hide_index=True,
        use_container_width=True
    )

    # =====================================
    # PO DETAILS
    # =====================================

    if not vendor_po.empty:

        st.subheader(
            "🚚 Purchase Order Details"
        )

        st.dataframe(
            vendor_po,
            hide_index=True,
            use_container_width=True
        )

    # =====================================
    # DOWNLOAD
    # =====================================

    csv = (
        summary
        .to_csv(index=False)
        .encode("utf-8")
    )

    st.download_button(
        f"📥 Download {selected_chemical} Vendor Report",
        csv,
        file_name=f"{selected_chemical}_Vendor_Report.csv",
        mime="text/csv"
    )
