# Property Development Feasibility App - Updated Version

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from dateutil.relativedelta import relativedelta

# --- App Title ---
st.title("🏗️ Property Development Feasibility App")

# --- Sidebar Inputs ---
st.sidebar.header("Project Settings")
project_name = st.sidebar.text_input("Project Name", value="")

st.sidebar.header("Land & Sale Details")
land_purchase_price = st.sidebar.number_input("Land Purchase Price ($)", value=0)
sale_price_per_unit = st.sidebar.number_input("Sale Price per Unit ($)", value=750000)
number_of_units = st.sidebar.number_input("Number of Units to Sell", value=2)

st.sidebar.header("Construction Inputs")
construction_size_m2 = st.sidebar.number_input("Construction Size (m²)", value=200)
construction_cost_per_m2 = st.sidebar.number_input("Construction Cost per m² ($)", value=2000)

st.sidebar.header("Finance Settings")
land_loan_lvr = st.sidebar.slider("Land Loan to Value Ratio (LVR)", 0.0, 1.0, 0.7)
annual_interest_rate = st.sidebar.number_input("Annual Interest Rate (%)", value=6.5) / 100
loan_term_years = st.sidebar.number_input("Loan Term (Years)", value=30)
deposit_percentage = st.sidebar.slider("Deposit Percentage (%)", 0.0, 1.0, 0.1)

st.sidebar.header("Timeline Controls")
months_until_settlement = st.sidebar.number_input("Months Until Settlement", value=3)
months_until_construction_start = st.sidebar.number_input("Months Until Construction Start after Settlement", value=3)
construction_duration_months = st.sidebar.number_input("Construction Duration (Months)", value=9)

with st.sidebar.expander("⚙️ Advanced Settings"):
    st.subheader("Soft Costs")
    stamp_duty = st.number_input("Stamp Duty ($)", value=0)
    legal_fees = st.number_input("Legal Fees ($)", value=2000)
    contingency_percent = st.slider("Contingency Percentage (%)", 0.0, 1.0, 0.10)

    st.subheader("Construction Finance Settings")
    construction_draws = st.number_input("Number of Construction Draws", min_value=1, max_value=12, value=5)
    loan_on_construction_percent = st.slider("Loan on Construction (%)", 0.0, 1.0, 0.70)
    equity_on_construction_percent = 1.0 - loan_on_construction_percent

    st.subheader("Other Costs")
    landscaping_cost = st.number_input("Landscaping Cost ($)", value=25000)
    connection_costs = st.number_input("Connection Costs ($)", value=15000)
    permit_fees = st.number_input("Permit Fees ($)", value=5000)
    title_fees = st.number_input("Title Fees ($)", value=3000)
    asset_protection_bond = st.number_input("Asset Protection Bond ($)", value=2000)
    construction_insurance = st.number_input("Construction Insurance ($)", value=3500)
    survey_cost = st.number_input("Survey Cost ($)", value=2500)
    town_planning_cost = st.number_input("Town Planning Cost ($)", value=6000)
    working_drawings = st.number_input("Working Drawings ($)", value=6000)
    consultants_cost = st.number_input("Consultants Cost ($)", value=8000)

# --- Validation ---
if st.sidebar.button("🚀 Run Feasibility"):
    if land_purchase_price <= 0:
        st.warning("⚠️ Land Purchase Price must be greater than $0.")
    elif number_of_units <= 0:
        st.warning("⚠️ Number of Units to Sell must be at least 1.")
    elif sale_price_per_unit <= 0:
        st.warning("⚠️ Sale Price per Unit must be greater than $0.")
    elif construction_size_m2 <= 0:
        st.warning("⚠️ Construction Size must be greater than 0 m².")
    else:
        # Proceed with calculations
        start_date = datetime.now()  # Use dynamic start date

        # --- Construction Payment Timing ---
        construction_draw_months = []
        if construction_duration_months >= construction_draws:
            interval = construction_duration_months // construction_draws
            start_month = months_until_settlement + months_until_construction_start
            for i in range(construction_draws):
                construction_draw_months.append(start_month + i * interval)
        else:
            construction_draw_months = [months_until_settlement + months_until_construction_start]

        # --- Cashflow Calculation ---
        def calculate_cashflow():
            cash_out_cum = 0
            loan_balance_cum = 0
            net_cash_position = 0

            cashflow_data = {
                'Month': [],
                'Month Name': [],
                'Cash Outflow This Month ($)': [],
                'Loan Draw This Month ($)': [],
                'Cumulative Cash Invested ($)': [],
                'Loan Balance ($)': [],
                'Net Cash Position ($)': [],
            }

            for month in range(0, sale_happens_month + 2):
                date = start_date + relativedelta(months=month)
                month_label = date.strftime("%b-%Y")
                cash_out_this_month = 0
                loan_draw_this_month = 0

                # Business Logic for each month

                cashflow_data[...] # Final Cashflow

---