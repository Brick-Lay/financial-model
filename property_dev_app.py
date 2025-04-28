# Property Development Financial Model - Streamlit App Version

import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from datetime import datetime
from dateutil.relativedelta import relativedelta

# --- Streamlit App Setup ---
st.title("🏗️ Property Development Financial Model")
st.sidebar.header("Project Inputs")

# --- Sidebar Inputs ---
land_purchase_price = st.sidebar.number_input("Land Purchase Price ($)", value=1131000)
stamp_duty = st.sidebar.number_input("Stamp Duty ($)", value=60405)
legal_fees = st.sidebar.number_input("Legal Fees ($)", value=2000)
survey_cost = st.sidebar.number_input("Survey Cost ($)", value=2750)
town_planning_cost = st.sidebar.number_input("Town Planning Cost ($)", value=8800)
working_drawings = st.sidebar.number_input("Working Drawings ($)", value=7700)
consultants_cost = st.sidebar.number_input("Consultants Cost ($)", value=15000)
construction_cost = st.sidebar.number_input("Construction Cost ($)", value=1200000)
landscaping_cost = st.sidebar.number_input("Landscaping Cost ($)", value=42500)
contingency = st.sidebar.number_input("Contingency ($)", value=124250)
connection_costs = st.sidebar.number_input("Connection Costs ($)", value=14800)
permit_fees = st.sidebar.number_input("Permit Fees ($)", value=5000)
title_fees = st.sidebar.number_input("Title Fees ($)", value=5000)
asset_protection_bond = st.sidebar.number_input("Asset Protection Bond ($)", value=2000)
construction_insurance = st.sidebar.number_input("Construction Insurance ($)", value=4000)
sale_price_per_townhouse = st.sidebar.number_input("Sale Price per Townhouse ($)", value=1700000)
number_of_townhouses = st.sidebar.number_input("Number of Townhouses", value=2)

# Loan and Timing Inputs
deposit_percentage = st.sidebar.slider("Deposit Percentage (%)", min_value=0.0, max_value=1.0, value=0.05)
land_loan_lvr = st.sidebar.slider("Loan to Value Ratio (LVR)", min_value=0.0, max_value=1.0, value=0.80)
annual_interest_rate = st.sidebar.number_input("Annual Interest Rate (%)", value=7.84) / 100
loan_term_years = st.sidebar.number_input("Loan Term (Years)", value=30)

contract_signing_date = datetime(2025, 3, 1)
months_until_settlement = st.sidebar.number_input("Months Until Settlement", value=5)
months_until_construction_start = st.sidebar.number_input("Months Until Construction Start after Settlement", value=6)
construction_duration_months = st.sidebar.number_input("Construction Duration (Months)", value=9)

# Stage payments are fixed
stage_payments = {"Slab": 0.10, "Frame": 0.15, "Lockup": 0.35, "Fixing": 0.20, "Completion": 0.20}

# Soft costs schedule
soft_costs_schedule = {
    1: survey_cost + town_planning_cost,
    2: permit_fees + asset_protection_bond,
    4: working_drawings + consultants_cost,
    8: construction_insurance,
    10: connection_costs,
    14: landscaping_cost,
    18: title_fees
}

# --- Calculations ---
deposit_paid_at_contract = land_purchase_price * deposit_percentage
land_loan_amount = land_purchase_price * land_loan_lvr
cash_due_at_settlement = (land_purchase_price - land_loan_amount) - deposit_paid_at_contract + stamp_duty + legal_fees
construction_loan_amount = construction_cost * 0.70
construction_cash_contribution = construction_cost * 0.30
soft_costs_total = sum([
    survey_cost, town_planning_cost, working_drawings, consultants_cost,
    landscaping_cost, connection_costs, permit_fees,
    title_fees, asset_protection_bond, construction_insurance
])
total_project_cost = land_purchase_price + soft_costs_total + construction_cost + contingency
total_cash_invested = deposit_paid_at_contract + cash_due_at_settlement + construction_cash_contribution + soft_costs_total + contingency
gross_sales = sale_price_per_townhouse * number_of_townhouses
gross_profit = gross_sales - total_project_cost
roi_total_cost = (gross_profit / total_project_cost) * 100
roi_cash_invested = (gross_profit / total_cash_invested) * 100

land_loan_monthly_rate = annual_interest_rate / 12
land_loan_term_months = loan_term_years * 12
land_loan_monthly_repayment = land_loan_amount * land_loan_monthly_rate * (1 + land_loan_monthly_rate)**land_loan_term_months / ((1 + land_loan_monthly_rate)**land_loan_term_months - 1)

# --- Cashflow Table ---
months_total = months_until_settlement + months_until_construction_start + construction_duration_months
loan_balance = 0
cumulative_interest_paid = 0
monthly_interest_rate = annual_interest_rate / 12
construction_loan_balance = 0
cashflow = []

contingency_allocation = {stage: contingency * pct for stage, pct in stage_payments.items()}
cumulative_cash_outflow = 0

for month in range(months_total + 1):
    current_date = contract_signing_date + relativedelta(months=+month)
    record = {
        "Month Number": month,
        "Month Name": current_date.strftime("%b-%Y"),
        "Description": "",
        "Cash Outflow ($)": 0,
        "Cumulative Cash Outflow ($)": 0,
        "Loan Drawn ($)": 0,
        "Loan Balance ($)": 0,
        "Interest This Month ($)": 0,
        "Cumulative Interest ($)": cumulative_interest_paid
    }

    if month in soft_costs_schedule:
        record["Description"] = "Soft Costs Payment"
        record["Cash Outflow ($)"] += soft_costs_schedule[month]

    if month == 0:
        record["Description"] += " | Contract signed. Deposit paid"
        record["Cash Outflow ($)"] += deposit_paid_at_contract

    if month == months_until_settlement:
        record["Description"] += " | Land settlement"
        record["Cash Outflow ($)"] += cash_due_at_settlement
        record["Loan Drawn ($)"] += land_loan_amount
        loan_balance += land_loan_amount

    if month > months_until_settlement:
        monthly_interest = loan_balance * monthly_interest_rate
        principal_payment = land_loan_monthly_repayment - monthly_interest
        loan_balance -= principal_payment
        cumulative_interest_paid += monthly_interest
        record["Description"] += " | Land loan P&I repayment"
        record["Cash Outflow ($)"] += land_loan_monthly_repayment
        record["Interest This Month ($)"] += monthly_interest

    construction_start_month = months_until_settlement + months_until_construction_start
    stages = list(stage_payments.keys())
    intervals = [0, 2, 4, 6, 8]
    if month in [construction_start_month + i for i in intervals]:
        stage_idx = intervals.index(month - construction_start_month)
        stage = stages[stage_idx]
        base_amount = construction_cost * stage_payments[stage]
        contingency_amount = contingency_allocation[stage]
        total_stage_amount = base_amount + contingency_amount
        record["Description"] += f" | Construction: {stage} stage payment (incl. contingency)"
        record["Cash Outflow ($)"] += total_stage_amount * 0.30
        record["Loan Drawn ($)"] += total_stage_amount * 0.70
        construction_loan_balance += total_stage_amount * 0.70

    if construction_loan_balance > 0:
        construction_loan_interest = construction_loan_balance * monthly_interest_rate
        cumulative_interest_paid += construction_loan_interest
        record["Cash Outflow ($)"] += construction_loan_interest
        record["Interest This Month ($)"] += construction_loan_interest

    cumulative_cash_outflow += record["Cash Outflow ($)"]
    record["Cumulative Cash Outflow ($)"] = cumulative_cash_outflow
    record["Loan Balance ($)"] = loan_balance + construction_loan_balance
    record["Cumulative Interest ($)"] = cumulative_interest_paid
    cashflow.append(record)

cashflow_df = pd.DataFrame(cashflow)

# --- Main Output ---
st.header("Summary")
st.write(f"Total Project Cost: ${total_project_cost:,.0f}")
st.write(f"Total Cash Invested: ${total_cash_invested:,.0f}")
st.write(f"Gross Sales: ${gross_sales:,.0f}")
st.write(f"Gross Profit: ${gross_profit:,.0f}")
st.write(f"ROI on Total Cost: {roi_total_cost:.2f}%")
st.write(f"ROI on Cash Invested: {roi_cash_invested:.2f}%")
st.write(f"Cumulative Interest Paid: ${cumulative_interest_paid:,.0f}")

st.header("Month-by-Month Cashflow Table")
st.dataframe(cashflow_df)

# --- Graph ---
st.header("Cashflow Graph")
fig, ax = plt.subplots(figsize=(12,6))
ax.plot(cashflow_df['Month Name'], cashflow_df['Cumulative Cash Outflow ($)'], label='Cumulative Cash Outflow ($)', marker='o')
ax.plot(cashflow_df['Month Name'], cashflow_df['Loan Balance ($)'], label='Loan Balance ($)', marker='x')
plt.xticks(rotation=45)
plt.xlabel('Month')
plt.ylabel('Amount ($)')
plt.title('Project Cash Outflow and Loan Balance Over Time')
plt.grid(True)
plt.legend()
st.pyplot(fig)
