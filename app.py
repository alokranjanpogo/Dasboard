import streamlit as st
from streamlit_option_menu import option_menu

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

st.title("🧪 Chemical Consumption & Stock Management Dashboard")

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
    st.info("Executive Dashboard Coming in Part 3")

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

from utils.loader import 

st.divider()

st.subheader("Excel Connection Test")

consumption_sheets,stock_sheets=get_sheet_names()

col1,col2=st.columns(2)

with col1:
    st.success("Consumption File")
    st.write(consumption_sheets)

with col2:
    st.success("Stock File")
    st.write(stock_sheets)
