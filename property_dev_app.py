# Property Development Feasibility App - Final Version

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

# --- Land and Sale Inputs ---
st.sidebar.header("Land & Sale Details")
land_purchase_price = st.sidebar.number_input("Land Purchase Price ($)", value=0)
sale_price_per_unit = st.sidebar.number_input("Sale Price per Unit ($)", value=750000)
number_of_units = st.sidebar.number_input("Number of Units to Sell", value=2)

# --- Construction Inputs ---
st.sidebar.header("Construction Inputs")
construction_size_m2 = st.sidebar.number_input("Construction Size (m²)", value=200)
construction_cost_per_m2 = st.sidebar.number_input("Construction Cost per m² ($)", value=2000)

# --- Finance Inputs ---
st.sidebar.header("Finance Settings")
land_loan_lvr = st.sidebar.slider("Land Loan to Value Ratio (LVR)", 0.0, 1.0, 0.7)
annual_interest_rate = st.sidebar.number_input("Annual Interest Rate (%)", value=6.5) / 100
loan_term_years = st.sidebar.number_input("Loan Term (Years)", value=30)
deposit_percentage = st.sidebar.slider("Deposit Percentage (%)", 0.0, 1.0, 0.1)

# --- Timeline Inputs ---
st.sidebar.header("Timeline Controls")
months_until_settlement = st.sidebar.number_input("Months Until Settlement", value=3)
months_until_construction_start = st.sidebar.number_input("Months Until Construction Start after Settlement", value=3)
construction_duration_months = st.sidebar.number_input("Construction Duration (Months)", value=9)

# --- Advanced Settings ---
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

# --- Validation Checks ---
if land_purchase_price <= 0:
    st.warning("⚠️ Please enter a valid Land Purchase Price.")
elif number_of_units <= 0:
    st.warning("⚠️ Please enter a valid number of units.")
elif sale_price_per_unit <= 0:
    st.warning("⚠️ Please enter a valid Sale Price per Unit.")
elif construction_size_m2 <= 0:
    st.warning("⚠️ Please enter a valid Construction Size in m².")
else:
    # --- Run Button ---
    if st.sidebar.button("🚀 Run Feasibility"):
        
        # --- Calculations Start ---
        construction_cost_total = construction_size_m2 * construction_cost_per_m2

        construction_draw_months = []
        if construction_duration_months >= construction_draws:
            interval = construction_duration_months // construction_draws
            start_month = months_until_settlement + months_until_construction_start
            for i in range(construction_draws):
                construction_draw_months.append(start_month + i * interval)
        else:
            construction_draw_months = [months_until_settlement + months_until_construction_start]

        cashflow_data = {
            'Month': [],
            'Month Name': [],
            'Cash Outflow This Month ($)': [],
            'Loan Draw This Month ($)': [],
            'Cumulative Cash Invested ($)': [],
            'Loan Balance ($)': [],
            'Net Cash Position ($)': [],
        }

        cash_out_cum = 0
        loan_balance_cum = 0
        peak_cash_invested = 0

        construction_loan_draw_total = construction_cost_total * loan_on_construction_percent
        construction_equity_draw_total = construction_cost_total * equity_on_construction_percent
        construction_loan_draw = construction_loan_draw_total / len(construction_draw_months)
        construction_equity_draw = construction_equity_draw_total / len(construction_draw_months)

        sale_happens_month = months_until_settlement + months_until_construction_start + construction_duration_months + 1

        for month in range(0, sale_happens_month + 2):
            date = datetime(2025, 3, 1) + relativedelta(months=month)
            month_label = date.strftime("%b-%Y")
            cash_out_this_month = 0
            loan_draw_this_month = 0

            if month == months_until_settlement:
                cash_out_this_month += (land_purchase_price * (1 - land_loan_lvr)) + stamp_duty + legal_fees + landscaping_cost + connection_costs + permit_fees + title_fees + asset_protection_bond + construction_insurance + survey_cost + town_planning_cost + working_drawings + consultants_cost
                loan_draw_this_month += land_purchase_price * land_loan_lvr

            if month in construction_draw_months:
                cash_out_this_month += construction_equity_draw
                loan_draw_this_month += construction_loan_draw

            if month == sale_happens_month:
                cash_out_this_month -= sale_price_per_unit * number_of_units

            cash_out_cum += cash_out_this_month
            loan_balance_cum += loan_draw_this_month
            net_cash_position = cash_out_cum - loan_balance_cum
            peak_cash_invested = max(peak_cash_invested, cash_out_cum)

            cashflow_data['Month'].append(month)
            cashflow_data['Month Name'].append(month_label)
            cashflow_data['Cash Outflow This Month ($)'].append(cash_out_this_month)
            cashflow_data['Loan Draw This Month ($)'].append(loan_draw_this_month)
            cashflow_data['Cumulative Cash Invested ($)'].append(cash_out_cum)
            cashflow_data['Loan Balance ($)'].append(loan_balance_cum)
            cashflow_data['Net Cash Position ($)'].append(net_cash_position)

        cashflow_df = pd.DataFrame(cashflow_data)

        # --- Final Financial Summary ---
        total_project_cost = cashflow_df['Cumulative Cash Invested ($)'].max()
        total_sale_value = sale_price_per_unit * number_of_units
        gross_profit = total_sale_value - total_project_cost
        roi_total_cost = (gross_profit / total_project_cost) * 100
        cash_on_cash_roi = (gross_profit / peak_cash_invested) * 100
        profit_margin = (gross_profit / total_sale_value) * 100

        # --- Deal Grading ---
        if cash_on_cash_roi >= 80:
            grade, color = "A+", "🟢"
        elif 60 <= cash_on_cash_roi < 80:
            grade, color = "A", "🟢"
        elif 40 <= cash_on_cash_roi < 60:
            grade, color = "B", "🟡"
        elif 20 <= cash_on_cash_roi < 40:
            grade, color = "C", "🟠"
        elif 0 <= cash_on_cash_roi < 20:
            grade, color = "D", "🔴"
        else:
            grade, color = "F", "🟥"

        # --- Display Financial Summary ---
        st.subheader("📊 Feasibility Summary")
        st.markdown(f"""
        **Project:** `{project_name or "Unnamed Project"}`  
        - **Total Sale Value:** ${total_sale_value:,.0f}  
        - **Total Project Cost:** ${total_project_cost:,.0f}  
        - **Gross Profit:** ${gross_profit:,.0f}  
        - **ROI on Total Cost:** `{roi_total_cost:.1f}%`  
        - **Cash-on-Cash ROI:** `{cash_on_cash_roi:.1f}%`  
        - **Profit Margin:** `{profit_margin:.1f}%`  
        - **Peak Cash Invested:** ${peak_cash_invested:,.0f}  
        - **Deal Grade:** `{grade}` {color}
        """)

        # --- Graph ---
        st.subheader("📈 Cashflow Overview")
        fig, ax = plt.subplots(figsize=(14,7))
        ax.plot(cashflow_df['Month Name'], cashflow_df['Cumulative Cash Invested ($)'], label='Cumulative Cash Invested', marker='o')
        ax.plot(cashflow_df['Month Name'], cashflow_df['Loan Balance ($)'], label='Loan Balance', marker='x')
        ax.plot(cashflow_df['Month Name'], cashflow_df['Net Cash Position ($)'], label='Net Cash Position', linestyle='--', color='purple')
        ax.set_xlabel("Month")
        ax.set_ylabel("Amount ($)")
        ax.set_title("Cashflow, Loan Balance and Net Exposure Timeline")
        ax.legend()
        ax.grid(True)
        plt.xticks(rotation=45)
        plt.tight_layout()
        for label in ax.xaxis.get_ticklabels()[::2]:
            label.set_visible(False)
        st.pyplot(fig)

        # --- Download CSV ---
        csv = cashflow_df.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Download Full Cashflow CSV", data=csv, file_name=f"{project_name or 'project'}_cashflow.csv", mime="text/csv")
