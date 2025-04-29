# Property Development Financial Model - Streamlit App Version (Grouped Sidebar with Advanced Construction Settings)

import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from datetime import datetime
from dateutil.relativedelta import relativedelta

# --- Streamlit App Setup ---
st.title("🏗️ Property Development Feasibility App")
st.sidebar.header("Project Inputs")

# --- Basic Sidebar Inputs ---
project_name = st.sidebar.text_input("Project Name", value="My Project")
land_purchase_price = st.sidebar.number_input("Land Purchase Price ($)", value=1131000)
construction_size_m2 = st.sidebar.number_input("Construction Size (m²)", value=300)
construction_cost_per_m2 = st.sidebar.number_input("Construction Cost per m² ($)", value=2000)
sale_price_per_unit = st.sidebar.number_input("Sale Price per Unit ($)", value=750000)
number_of_units = st.sidebar.number_input("Number of Units to Sell", value=2)

# --- Finance Inputs ---
land_loan_lvr = st.sidebar.slider("Loan to Value Ratio (LVR)", min_value=0.0, max_value=1.0, value=0.80)
annual_interest_rate = st.sidebar.number_input("Annual Interest Rate (%)", value=7.84) / 100
loan_term_years = st.sidebar.number_input("Loan Term (Years)", value=30)

deposit_percentage = st.sidebar.slider("Deposit Percentage (%)", min_value=0.0, max_value=1.0, value=0.05)

# --- Timeline Inputs ---
months_until_settlement = st.sidebar.number_input("Months Until Settlement", value=5)
months_until_construction_start = st.sidebar.number_input("Months Until Construction Start after Settlement", value=6)
construction_duration_months = st.sidebar.number_input("Construction Duration (Months)", value=9)

# --- Advanced Settings ---
with st.sidebar.expander("⚙️ Advanced Settings"):
    st.subheader("General")
    stamp_duty = st.number_input("Stamp Duty ($)", value=60405)
    legal_fees = st.number_input("Legal Fees ($)", value=2000)
    contingency_percent = st.slider("Contingency Percentage (%)", min_value=0.0, max_value=1.0, value=0.10)

    st.subheader("Construction Finance Settings")
    construction_draws = st.number_input("Number of Construction Draws", min_value=1, max_value=12, value=5)
    loan_on_construction_percent = st.slider("Loan on Construction (%)", min_value=0.0, max_value=1.0, value=0.70)
    equity_on_construction_percent = 1.0 - loan_on_construction_percent

    st.subheader("Additional Costs")
    landscaping_cost = st.number_input("Landscaping Cost ($)", value=42500)
    connection_costs = st.number_input("Connection Costs ($)", value=14800)
    permit_fees = st.number_input("Permit Fees ($)", value=5000)
    title_fees = st.number_input("Title Fees ($)", value=5000)
    asset_protection_bond = st.number_input("Asset Protection Bond ($)", value=2000)
    construction_insurance = st.number_input("Construction Insurance ($)", value=4000)
    survey_cost = st.number_input("Survey Cost ($)", value=2750)
    town_planning_cost = st.number_input("Town Planning Cost ($)", value=8800)
    working_drawings = st.number_input("Working Drawings ($)", value=7700)
    consultants_cost = st.number_input("Consultants Cost ($)", value=15000)

# --- Construction Payment Timing ---
# This will be used later in the cashflow calculation to space drawdowns evenly.
construction_draw_months = []
if construction_duration_months >= construction_draws:
    interval = construction_duration_months // construction_draws
    start_month = months_until_settlement + months_until_construction_start
    for i in range(construction_draws):
        construction_draw_months.append(start_month + i * interval)
else:
    # fallback to single draw at start if construction period is shorter than number of draws
    construction_draw_months = [months_until_settlement + months_until_construction_start]
