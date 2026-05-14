# ============================================================
# 🚰 WATER TREATMENT PLANT MONITORING DASHBOARD
# ============================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="WTP Monitoring Dashboard",
    page_icon="🚰",
    layout="wide"
)

# ============================================================
# TITLE
# ============================================================

st.markdown(
    """
    <h1 style='text-align:center;color:#0B5ED7;'>🚰 SMART WTP MONITORING DASHBOARD</h1>
    <hr>
    """,
    unsafe_allow_html=True
)

# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.header("⚙️ Plant Controls")

uploaded_file = st.sidebar.file_uploader(
    "Upload WTP Excel File",
    type=["xlsx"]
)

# ============================================================
# SAMPLE DATA
# ============================================================

if uploaded_file:
    df = pd.read_excel(uploaded_file)
else:
    dates = pd.date_range(start="2026-01-01", periods=30)

    df = pd.DataFrame({
        "Date": dates,
        "Raw Water Turbidity": np.random.randint(50, 400, 30),
        "Filtered Water Turbidity": np.random.uniform(0.1, 1.0, 30),
        "pH": np.random.uniform(6.8, 7.8, 30),
        "Residual Chlorine": np.random.uniform(0.2, 1.0, 30),
        "Flow MLD": np.random.randint(80, 120, 30),
        "Conductivity": np.random.randint(250, 700, 30),
        "Alum Dose": np.random.randint(20, 60, 30),
        "Hypo Dose": np.random.randint(1, 5, 30)
    })

# ============================================================
# DATE FILTER
# ============================================================

if "Date" in df.columns:
    df["Date"] = pd.to_datetime(df["Date"])

    start_date = st.sidebar.date_input(
        "Start Date",
        df["Date"].min()
    )

    end_date = st.sidebar.date_input(
        "End Date",
        df["Date"].max()
    )

    df = df[(df["Date"] >= pd.to_datetime(start_date)) &
            (df["Date"] <= pd.to_datetime(end_date))]

# ============================================================
# KPI SECTION
# ============================================================

st.subheader("📊 LIVE PLANT STATUS")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "💧 Raw Turbidity",
        f"{df['Raw Water Turbidity'].iloc[-1]:.0f} NTU"
    )

with col2:
    st.metric(
        "✅ Filtered Turbidity",
        f"{df['Filtered Water Turbidity'].iloc[-1]:.2f} NTU"
    )

with col3:
    st.metric(
        "🧪 Alum Dose",
        f"{df['Alum Dose'].iloc[-1]:.0f} mg/L"
    )

with col4:
    st.metric(
        "☣️ Residual Chlorine",
        f"{df['Residual Chlorine'].iloc[-1]:.2f} ppm"
    )

st.markdown("---")

# ============================================================
# LIVE GAUGES
# ============================================================

st.subheader("🎯 LIVE PROCESS GAUGES")

c1, c2, c3 = st.columns(3)

with c1:
    fig1 = go.Figure(go.Indicator(
        mode="gauge+number",
        value=float(df['pH'].iloc[-1]),
        title={'text': "pH"},
        gauge={
            'axis': {'range': [0, 14]},
            'bar': {'color': "blue"}
        }
    ))

    fig1.update_layout(height=300)
    st.plotly_chart(fig1, use_container_width=True)

with c2:
    fig2 = go.Figure(go.Indicator(
        mode="gauge+number",
        value=float(df['Flow MLD'].iloc[-1]),
        title={'text': "Flow (MLD)"},
        gauge={
            'axis': {'range': [0, 150]},
            'bar': {'color': "green"}
        }
    ))

    fig2.update_layout(height=300)
    st.plotly_chart(fig2, use_container_width=True)

with c3:
    fig3 = go.Figure(go.Indicator(
        mode="gauge+number",
        value=float(df['Conductivity'].iloc[-1]),
        title={'text': "Conductivity"},
        gauge={
            'axis': {'range': [0, 1000]},
            'bar': {'color': "orange"}
        }
    ))

    fig3.update_layout(height=300)
    st.plotly_chart(fig3, use_container_width=True)

# ============================================================
# TREND CHARTS
# ============================================================

st.subheader("📈 PROCESS TREND ANALYSIS")

left, right = st.columns(2)

with left:
    fig = px.line(
        df,
        x="Date",
        y="Raw Water Turbidity",
        title="Raw Water Turbidity Trend",
        markers=True
    )

    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

with right:
    fig = px.line(
        df,
        x="Date",
        y="Filtered Water Turbidity",
        title="Filtered Water Turbidity Trend",
        markers=True
    )

    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

# ============================================================
# CHEMICAL DOSING ANALYSIS
# ============================================================

st.subheader("🧪 CHEMICAL DOSING ANALYSIS")

c1, c2 = st.columns(2)

with c1:
    fig = px.bar(
        df,
        x="Date",
        y="Alum Dose",
        title="Alum Consumption"
    )

    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

with c2:
    fig = px.line(
        df,
        x="Date",
        y="Hypo Dose",
        title="Hypochlorite Dose Trend",
        markers=True
    )

    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

# ============================================================
# FILTER BED STATUS
# ============================================================

st.subheader("🧱 FILTER BED STATUS")

fb1, fb2, fb3, fb4, fb5, fb6 = st.columns(6)

filter_values = [85, 90, 78, 92, 88, 81]

for i, (col, val) in enumerate(zip(
        [fb1, fb2, fb3, fb4, fb5, fb6],
        filter_values
    )):

    with col:
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=val,
            title={'text': f"FB-{i+1}"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "darkblue"}
            }
        ))

        fig.update_layout(height=220)
        st.plotly_chart(fig, use_container_width=True)

# ============================================================
# AI BASED FUTURE DOSE PREDICTION
# ============================================================

st.subheader("🤖 AI FUTURE DOSE PREDICTION")

latest_turbidity = df['Raw Water Turbidity'].iloc[-1]
latest_conductivity = df['Conductivity'].iloc[-1]

predicted_alum = round((latest_turbidity * 0.12), 2)
predicted_hypo = round((latest_conductivity * 0.0045), 2)

pred1, pred2 = st.columns(2)

with pred1:
    st.success(f"Recommended Alum Dose: {predicted_alum} mg/L")

with pred2:
    st.success(f"Recommended Hypo Dose: {predicted_hypo} ppm")

# ============================================================
# ALERT SECTION
# ============================================================

st.subheader("🚨 SMART ALERTS")

if df['Filtered Water Turbidity'].iloc[-1] > 1:
    st.error("⚠️ Filtered water turbidity is above permissible limit.")
else:
    st.success("✅ Filtered water quality is within limit.")

if df['Residual Chlorine'].iloc[-1] < 0.2:
    st.warning("⚠️ Residual chlorine is low.")

if df['pH'].iloc[-1] < 6.5 or df['pH'].iloc[-1] > 8.5:
    st.error("⚠️ pH is outside acceptable range.")

# ============================================================
# RAW DATA TABLE
# ============================================================

st.subheader("📋 PLANT DATA")

st.dataframe(df, use_container_width=True)

# ============================================================
# FOOTER
# ============================================================

st.markdown("---")
st.caption("Developed for Smart Water Treatment Plant Monitoring")

