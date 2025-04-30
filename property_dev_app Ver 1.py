
# Property Development Feasibility App - Final Version

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from dateutil.relativedelta import relativedelta

# --- App Title ---
st.title("🏗️ Property Development Feasibility App")

# --- Sidebar Inputs ---
st.sidebar.header("Project Info")
project_name = st.sidebar.text_input("Project Name", value="")

st.sidebar.header("Land & Sales")
land_purchase_price = st.sidebar.number_input("Land Purchase Price ($)", value=0)
sale_price_per_unit = st.sidebar.number_input("Sale Price per Unit ($)", value=750000)
number_of_units = st.sidebar.number_input("Number of Units", value=2)

st.sidebar.header("Construction")
construction_size_m2 = st.sidebar.number_input("Build Size Total (m²)", value=200)
construction_cost_per_m2 = st.sidebar.number_input("Build Cost per m² ($)", value=2000)

st.sidebar.header("Finance")
land_loan_lvr = st.sidebar.slider("Land LVR (%)", 0.0, 1.0, 0.7)
loan_on_construction_percent = st.sidebar.slider("Construction Loan Portion", 0.0, 1.0, 0.7)
equity_on_construction_percent = 1.0 - loan_on_construction_percent
interest_rate = st.sidebar.number_input("Annual Interest Rate (%)", value=6.5) / 100

st.sidebar.header("Timeline")
months_until_settlement = st.sidebar.number_input("Months Until Settlement", value=3)
months_until_construction_start = st.sidebar.number_input("Months Until Build Start (after settlement)", value=3)
construction_duration_months = st.sidebar.number_input("Build Duration (months)", value=9)
construction_draws = st.sidebar.number_input("Drawdowns", value=5, min_value=1)

with st.sidebar.expander("⚙️ Advanced Costs"):
    stamp_duty = st.number_input("Stamp Duty", value=0)
    legal_fees = st.number_input("Legal Fees", value=2000)
    contingency_percent = st.slider("Contingency (%)", 0.0, 0.2, 0.10)
    landscaping_cost = st.number_input("Landscaping", value=25000)
    connection_costs = st.number_input("Connections", value=15000)
    permit_fees = st.number_input("Permit Fees", value=5000)
    title_fees = st.number_input("Title Fees", value=3000)
    asset_protection_bond = st.number_input("Asset Bond", value=2000)
    construction_insurance = st.number_input("Insurance", value=3500)
    survey_cost = st.number_input("Survey Cost", value=2500)
    town_planning_cost = st.number_input("Town Planning", value=6000)
    working_drawings = st.number_input("Working Drawings", value=6000)
    consultants_cost = st.number_input("Consultants", value=8000)

# --- Input Validation (now correctly indented) ---
if land_purchase_price <= 0:
    st.warning("⚠️ Land Purchase Price must be greater than 0.")
elif number_of_units <= 0:
    st.warning("⚠️ You must sell at least one unit.")
elif sale_price_per_unit <= 0:
    st.warning("⚠️ Set a valid sale price.")
elif construction_size_m2 <= 0:
    st.warning("⚠️ Build size must be greater than zero.")
else:
    if st.sidebar.button("🚀 Run Feasibility"):
        st.success("✅ Feasibility calculation will run from here (you can paste the full logic block here).")
