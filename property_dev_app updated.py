
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

# --- Input Validation ---
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
        construction_cost_total = construction_size_m2 * construction_cost_per_m2
        construction_loan_draw_total = construction_cost_total * loan_on_construction_percent
        construction_equity_draw_total = construction_cost_total * equity_on_construction_percent
        contingency = contingency_percent * construction_cost_total

        draw_amount_loan = construction_loan_draw_total / construction_draws
        draw_amount_equity = construction_equity_draw_total / construction_draws

        start_month = months_until_settlement + months_until_construction_start
        draw_months = [start_month + i * (construction_duration_months // construction_draws) for i in range(construction_draws)]
        sale_month = months_until_settlement + months_until_construction_start + construction_duration_months + 1

        cashflow = {
            "Month": [],
            "Month Name": [],
            "Cash Outflow This Month ($)": [],
            "Loan Draw This Month ($)": [],
            "Cumulative Cash Invested ($)": [],
            "Loan Balance ($)": [],
            "Net Cash Position ($)": []
        }

        cash_out_cum = 0
        loan_cum = 0

        for month in range(sale_month + 2):
            date = datetime(2025, 3, 1) + relativedelta(months=month)
            label = date.strftime("%b-%Y")
            cash_out = 0
            loan_in = 0

            if month == months_until_settlement:
                cash_out += (land_purchase_price * (1 - land_loan_lvr)) + stamp_duty + legal_fees + landscaping_cost + connection_costs + permit_fees + title_fees + asset_protection_bond + construction_insurance + survey_cost + town_planning_cost + working_drawings + consultants_cost
                loan_in += land_purchase_price * land_loan_lvr

            if month in draw_months:
                cash_out += draw_amount_equity
                loan_in += draw_amount_loan

            if month == sale_month:
                cash_out -= sale_price_per_unit * number_of_units

            cash_out_cum += cash_out
            loan_cum += loan_in

            cashflow["Month"].append(month)
            cashflow["Month Name"].append(label)
            cashflow["Cash Outflow This Month ($)"].append(cash_out)
            cashflow["Loan Draw This Month ($)"].append(loan_in)
            cashflow["Cumulative Cash Invested ($)"].append(cash_out_cum)
            cashflow["Loan Balance ($)"].append(loan_cum)
            cashflow["Net Cash Position ($)"].append(cash_out_cum - loan_cum)

        df = pd.DataFrame(cashflow)

        total_project_cost = df["Cumulative Cash Invested ($)"].iloc[-2] + df["Loan Balance ($)"].iloc[-2]
        total_sale_value = sale_price_per_unit * number_of_units
        gross_profit = total_sale_value - total_project_cost
        roi_total_cost = (gross_profit / total_project_cost) * 100
        peak_cash_invested = df["Cumulative Cash Invested ($)"].max()
        cash_on_cash_roi = (gross_profit / peak_cash_invested) * 100
        profit_margin = (gross_profit / total_sale_value) * 100

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

        st.subheader("📊 Feasibility Summary")
        summary_text = (
            f"**Project:** `{project_name or 'Unnamed Project'}`  
"
            f"- **Total Sale Value:** ${total_sale_value:,.0f}  
"
            f"- **Total Project Cost:** ${total_project_cost:,.0f}  
"
            f"- **Gross Profit:** ${gross_profit:,.0f}  
"
            f"- **ROI on Total Cost:** `{roi_total_cost:.1f}%`  
"
            f"- **Cash-on-Cash ROI:** `{cash_on_cash_roi:.1f}%`  
"
            f"- **Profit Margin:** `{profit_margin:.1f}%`  
"
            f"- **Peak Cash Invested:** ${peak_cash_invested:,.0f}  
"
            f"- **Deal Grade:** `{grade}` {color}"
        )
        st.markdown(summary_text)

        st.subheader("📈 Cashflow Overview")
        fig, ax = plt.subplots(figsize=(14,7))
        ax.plot(df['Month Name'], df['Cumulative Cash Invested ($)'], label='Cumulative Cash Invested', marker='o')
        ax.plot(df['Month Name'], df['Loan Balance ($)'], label='Loan Balance', marker='x')
        ax.plot(df['Month Name'], df['Net Cash Position ($)'], label='Net Cash Position', linestyle='--', color='purple')
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

        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Download Full Cashflow CSV", data=csv, file_name=f"{project_name or 'project'}_cashflow.csv", mime="text/csv")
