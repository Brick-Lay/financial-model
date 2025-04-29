# Property Development Financial Model - Streamlit App Version (Grouped Sidebar)

import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from datetime import datetime
from dateutil.relativedelta import relativedelta

# --- Streamlit App Setup ---
st.title("🏗️ Property Development Feasibility App")
st.sidebar.header("Project Inputs")

# --- Grouped Sidebar Inputs ---
with st.sidebar.expander("🏠 Land and Purchase Details"):
    land_purchase_price = st.number_input("Land Purchase Price ($)", value=1131000)
    stamp_duty = st.number_input("Stamp Duty ($)", value=60405)
    legal_fees = st.number_input("Legal Fees ($)", value=2000)

with st.sidebar.expander("🏗️ Construction Inputs"):
    construction_size_m2 = st.number_input("Construction Size (m²)", value=300)
    construction_cost_per_m2 = st.number_input("Construction Cost per m² ($)", value=2000)
    contingency_percent = st.slider("Contingency Percentage (%)", min_value=0.0, max_value=1.0, value=0.10)
    landscaping_cost = st.number_input("Landscaping Cost ($)", value=42500)
    connection_costs = st.number_input("Connection Costs ($)", value=14800)
    permit_fees = st.number_input("Permit Fees ($)", value=5000)
    title_fees = st.number_input("Title Fees ($)", value=5000)
    asset_protection_bond = st.number_input("Asset Protection Bond ($)", value=2000)
    construction_insurance = st.number_input("Construction Insurance ($)", value=4000)

with st.sidebar.expander("📄 Soft Costs"):
    survey_cost = st.number_input("Survey Cost ($)", value=2750)
    town_planning_cost = st.number_input("Town Planning Cost ($)", value=8800)
    working_drawings = st.number_input("Working Drawings ($)", value=7700)
    consultants_cost = st.number_input("Consultants Cost ($)", value=15000)

with st.sidebar.expander("🏢 Sales Details"):
    sale_price_per_unit = st.number_input("Sale Price per Unit ($)", value=750000)
    number_of_units = st.number_input("Number of Units to Sell", value=2)

with st.sidebar.expander("💰 Finance Details"):
    deposit_percentage = st.slider("Deposit Percentage (%)", min_value=0.0, max_value=1.0, value=0.05)
    land_loan_lvr = st.slider("Loan to Value Ratio (LVR)", min_value=0.0, max_value=1.0, value=0.80)
    annual_interest_rate = st.number_input("Annual Interest Rate (%)", value=7.84) / 100
    loan_term_years = st.number_input("Loan Term (Years)", value=30)

with st.sidebar.expander("🗓️ Timeline"):
    contract_signing_date = datetime(2025, 3, 1)
    months_until_settlement = st.number_input("Months Until Settlement", value=5)
    months_until_construction_start = st.number_input("Months Until Construction Start after Settlement", value=6)
    construction_duration_months = st.number_input("Construction Duration (Months)", value=9)

# --- Add Run Button ---
run_model = st.sidebar.button("Run Feasibility")

if run_model:
    # --- Calculations ---
    construction_cost = construction_size_m2 * construction_cost_per_m2
    contingency = construction_cost * contingency_percent
    soft_costs_total = (survey_cost + town_planning_cost + working_drawings + consultants_cost +
                        landscaping_cost + connection_costs + permit_fees + title_fees +
                        asset_protection_bond + construction_insurance + stamp_duty + legal_fees)

    total_project_cost = land_purchase_price + construction_cost + contingency + soft_costs_total
    total_sale_value = sale_price_per_unit * number_of_units
    gross_profit = total_sale_value - total_project_cost
    roi_total_cost = (gross_profit / total_project_cost) * 100

    # --- Cashflow Calculation ---
    data = {
        'Month Name': [],
        'Cumulative Cash Outflow ($)': [],
        'Loan Balance ($)': []
    }

    cash_outflow = 0
    loan_balance = 0

    for i in range(0, months_until_settlement + months_until_construction_start + construction_duration_months):
        date = contract_signing_date + relativedelta(months=i)
        month_label = date.strftime("%b-%Y")
        if i == months_until_settlement:
            cash_outflow += (land_purchase_price * (1 - land_loan_lvr)) + soft_costs_total
            loan_balance += land_purchase_price * land_loan_lvr
        if i > months_until_settlement + months_until_construction_start and (i - (months_until_settlement + months_until_construction_start)) % (construction_duration_months // 5) == 0:
            cash_outflow += (construction_cost * 0.30) / 5
            loan_balance += (construction_cost * 0.70) / 5
        data['Month Name'].append(month_label)
        data['Cumulative Cash Outflow ($)'].append(cash_outflow)
        data['Loan Balance ($)'].append(loan_balance)

    cashflow_df = pd.DataFrame(data)

    # --- Display Outputs ---
    st.header("Summary")
    st.write(f"Total Project Cost: ${total_project_cost:,.0f}")
    st.write(f"Total Sale Value: ${total_sale_value:,.0f}")
    st.write(f"Gross Profit: ${gross_profit:,.0f}")
    st.write(f"ROI on Total Cost: {roi_total_cost:.2f}%")

    st.header("Cashflow Table")
    st.dataframe(cashflow_df)

    # --- Download Button for Cashflow ---
    st.download_button(
        label="📥 Download Cashflow CSV",
        data=cashflow_df.to_csv(index=False),
        file_name='cashflow_table.csv',
        mime='text/csv'
    )

    # --- Improved Graph Code ---
    st.header("Cashflow Graph")
    fig, ax = plt.subplots(figsize=(14,7))
    ax.plot(cashflow_df['Month Name'], cashflow_df['Cumulative Cash Outflow ($)'], label='Cumulative Cash Outflow ($)', marker='o')
    ax.plot(cashflow_df['Month Name'], cashflow_df['Loan Balance ($)'], label='Loan Balance ($)', marker='x')
    ax.set_xlabel('Month')
    ax.set_ylabel('Amount ($)')
    ax.set_title('🔵 Project Cash Outflow and Loan Balance Over Time')
    ax.grid(True)
    ax.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    for label in ax.xaxis.get_ticklabels()[::2]:
        label.set_visible(False)
    st.pyplot(fig)
