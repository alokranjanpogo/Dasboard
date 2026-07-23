import streamlit as st
from streamlit_option_menu import option_menu
import plotly.express as px
import plotly.graph_objects as go
from utils.loader import *

st.set_page_config(
    page_title="Chemical Consumption Dashboard",
    page_icon="🧪",
    layout="wide"
)

# ---------- CSS ----------

st.markdown("""
<style>

.main{
    background:#f4f8fb;
}

.kpi{
background:white;
padding:18px;
border-radius:12px;
box-shadow:0px 3px 10px rgba(0,0,0,0.12);
text-align:center;
}

.sidebar .sidebar-content{
background:#0E4D92;
}

</style>
""",unsafe_allow_html=True)

st.title(" Chemical Consumption & Stock Management Dashboard")

selected = option_menu(
    menu_title=None,
    options=[
        "Executive Dashboard",
        "Consumption Analysis",
        "Stock Status",
        "Order Status",
        "Forecast",
        "Reports"
    ],
    icons=[
        "speedometer2",
        "bar-chart",
        "boxes",
        "truck",
        "graph-up-arrow",
        "file-earmark-text"
    ],
    orientation="horizontal"
)

if selected=="Executive Dashboard":


    # ==============================
    # Executive Dashboard
    # ==============================

    st.title("📊 Executive Dashboard")

    latest_date, stock = get_latest_stock()

    st.caption(f"Latest Stock Date : {latest_date}")

    st.divider()

    # ==========================================
    # Executive KPI Cards
    # ==========================================
    
    st.header("📊 Executive Summary")
    
    total_chemicals = len(stock)
    
    available_stock = pd.to_numeric(
    stock.iloc[:,4],
    errors="coerce"
    ).sum()
    
    daily_requirement = pd.to_numeric(
    stock.iloc[:,1],
    errors="coerce"
    ).sum()
    
    monthly_requirement = pd.to_numeric(
    stock.iloc[:,2],
    errors="coerce"
    ).sum()
    
    c1,c2,c3,c4=st.columns(4)
    
    with c1:
        st.metric(
            "🧪 Chemicals",
            total_chemicals
        )
    
    with c2:
        st.metric(
            "📦 Available Stock",
            f"{available_stock:.2f} Ton"
        )
        
    with c3:
        st.metric(
            "📅 Daily Requirement",
            f"{daily_requirement:.2f} Ton"
        )
        
    with c4:
        st.metric(
            "🗓 Monthly Requirement",
            f"{monthly_requirement:.2f} Ton"
        )
    
    st.divider()
    
    # ==========================================
    # Stock Health
    # ==========================================
    
    st.header("📦 Current Chemical Stock Status")
    
    display = stock.copy()
    
    display.columns=[
    "Chemical",
    "Daily Requirement",
    "Monthly Requirement",
    "3 Month Requirement",
    "Available Stock",
    "Available Months"
    ]
    
        def health(x):
        
        if x>=3:
            return "🟢 Healthy"
        
        elif x>=1:
            return "🟡 Reorder Soon"
        
        else:
            return "🔴 Critical"
            
        display["Status"]=display["Available Months"].apply(health)
        
        st.dataframe(
        display,
        use_container_width=True,
        hide_index=True
        )
    
    # ==========================================
    # Stock Availability
    # ==========================================
    
    st.header("📈 Available Stock by Chemical")
    
    fig=px.bar(
    display,
    x="Chemical",
    y="Available Stock",
    color="Status",
    text="Available Stock",
    height=500
    )
    
    fig.update_layout(
    xaxis_title="Chemical",
    yaxis_title="Stock (Ton)",
    legend_title=""
    )
    
    st.plotly_chart(
    fig,
    use_container_width=True
    )
    
    # ==========================================
    # Stock Distribution
    # ==========================================
    
    st.header("🥧 Chemical Distribution")
    
    fig2=px.pie(
    display,
    names="Chemical",
    values="Available Stock",
    hole=0.6
    )
    
    st.plotly_chart(
    fig2,
    use_container_width=True
    )
    
    # ==========================================
    # Low Stock Alert
    # ==========================================
    
    st.header("🚨 Critical Chemicals")
    
    critical=display[
    display["Status"]=="🔴 Critical"
    ]
    
    if len(critical)==0:
    
    st.success("✅ No Critical Chemical")
    
    else:
    
    st.error("Immediate Procurement Required")
    
    st.dataframe(
        critical,
        use_container_width=True,
        hide_index=True
    )
    
        # ==============================
        # Latest Stock Data
        # ==============================
    
        st.header("Current Chemical Stock")
    
        st.dataframe(
            stock,
            use_container_width=True,
            height=500
        )
    
        # ==============================
        # Detected Columns
        # ==============================
    
        st.header("Detected Columns")
    
        st.write(list(stock.columns))
    
elif selected=="Consumption Analysis":
    st.info("Consumption Dashboard Coming in Part 4")    


elif selected=="Stock Status":
    st.info("Stock Dashboard Coming in Part 5")

elif selected=="Order Status":
    st.info("Order Dashboard Coming in Part 6")

elif selected=="Forecast":
    st.info("Forecast Dashboard Coming in Part 7")

elif selected=="Reports":
    st.info("Reports Dashboard Coming in Part 8")

from utils.loader import *

