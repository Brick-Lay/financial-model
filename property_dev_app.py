# Property Development Financial Model - Streamlit App Version (Grouped Sidebar with Validation)

import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from datetime import datetime
from dateutil.relativedelta import relativedelta

# --- Streamlit App Setup ---
st.title("🏗️ Property Development Feasibility App")
st.sidebar.header("Project Inputs")

# --- Basic Sidebar Inputs ---
project_name = st.sidebar.text_input("Project Name", value="")
land_purchase_price = st.sidebar.number_input("Land Purchase Price ($)", value=0)
construction_size_m2 = st.sidebar.number_input("Construction Size (m²)", value=200)
construction_cost_per_m2 = st.sidebar.number_input("Construction Cost per m² ($)", value=2000)
sale_price_per_unit = st.sidebar.number_input("Sale Price per Unit ($)", value=750000)
number_of_units = st.sidebar.number_input("Number of Units to Sell", value=2)

# --- Finance Inputs ---
land_loan_lvr = st.sidebar.slider("Loan to Value Ratio (LVR)", min_value=0.0, max_value=1.0, value=0.70)
annual_interest_rate = st.sidebar.number_input("Annual Interest Rate (%)", value=6.5) / 100
loan_term_years = st.sidebar.number_input("Loan Term (Years)", value=30)

deposit_percentage = st.sidebar.slider("Deposit Percentage (%)", min_value=0.0, max_value=1.0, value=0.10)

# --- Timeline Inputs ---
months_until_settlement = st.sidebar.number_input("Months Until Settlement", value=3)
months_until_construction_start = st.sidebar.number_input("Months Until Construction Start after Settlement", value=3)
construction_duration_months = st.sidebar.number_input("Construction Duration (Months)", value=9)

# --- Advanced Settings ---
with st.sidebar.expander("⚙️ Advanced Settings"):
    st.subheader("General")
    stamp_duty = st.number_input("Stamp Duty ($)", value=0)
    legal_fees = st.number_input("Legal Fees ($)", value=2000)
    contingency_percent = st.slider("Contingency Percentage (%)", min_value=0.0, max_value=1.0, value=0.10)

    st.subheader("Construction Finance Settings")
    construction_draws = st.number_input("Number of Construction Draws", min_value=1, max_value=12, value=5)
    loan_on_construction_percent = st.slider("Loan on Construction (%)", min_value=0.0, max_value=1.0, value=0.70)
    equity_on_construction_percent = 1.0 - loan_on_construction_percent

    st.subheader("Additional Costs")
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

# --- Input Validation ---
if land_purchase_price <= 0:
    st.warning("⚠️ Please enter a valid Land Purchase Price.")
elif number_of_units <= 0:
    st.warning("⚠️ Please enter a valid number of units to sell.")
elif sale_price_per_unit <= 0:
    st.warning("⚠️ Please enter a valid Sale Price per Unit.")
elif construction_size_m2 <= 0:
    st.warning("⚠️ Please enter a valid Construction Size in m².")
else:
    # --- Construction Payment Timing ---
    construction_draw_months = []
    if construction_duration_months >= construction_draws:
        interval = construction_duration_months // construction_draws
        start_month = months_until_settlement + months_until_construction_start
        for i in range(construction_draws):
            construction_draw_months.append(start_month + i * interval)
    else:
        construction_draw_months = [months_until_settlement + months_until_construction_start]

    # --- Cashflow Calculation (Updated with drawdown logic) ---
    data = {
        'Month Name': [],
        'Cumulative Cash Outflow ($)': [],
        'Loan Balance ($)': []
    }

    cash_outflow = 0
    loan_balance = 0
    peak_cash_invested = 0

    construction_cost_total = construction_size_m2 * construction_cost_per_m2
    construction_loan_draw = (construction_cost_total * loan_on_construction_percent) / len(construction_draw_months)
    construction_equity_draw = (construction_cost_total * equity_on_construction_percent) / len(construction_draw_months)

    for i in range(0, months_until_settlement + months_until_construction_start + construction_duration_months + 1):
        date = datetime(2025, 3, 1) + relativedelta(months=i)
        month_label = date.strftime("%b-%Y")

        if i == months_until_settlement:
            cash_outflow += (land_purchase_price * (1 - land_loan_lvr)) + stamp_duty + legal_fees + landscaping_cost + connection_costs + permit_fees + title_fees + asset_protection_bond + construction_insurance + survey_cost + town_planning_cost + working_drawings + consultants_cost
            loan_balance += land_purchase_price * land_loan_lvr

        if i in construction_draw_months:
            cash_outflow += construction_equity_draw
            loan_balance += construction_loan_draw

        peak_cash_invested = max(peak_cash_invested, cash_outflow)
        data['Month Name'].append(month_label)
        data['Cumulative Cash Outflow ($)'].append(cash_outflow)
        data['Loan Balance ($)'].append(loan_balance)

    cashflow_df = pd.DataFrame(data)
