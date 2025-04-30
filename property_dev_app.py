
# Final corrected MVP version - proper total project cost based on last unit completion

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from dateutil.relativedelta import relativedelta

st.title("🏗️ Property Development Feasibility App")

# Sidebar Inputs
st.sidebar.header("Project Info")
project_name = st.sidebar.text_input("Project Name", value="My Project")

st.sidebar.header("Land & Sales")
land_price = st.sidebar.number_input("Land Price ($)", value=1350000)
sale_price = st.sidebar.number_input("Sale Price per Unit ($)", value=850000)
units = st.sidebar.number_input("Number of Units", value=6)

st.sidebar.header("Construction")
construction_size_m2 = st.sidebar.number_input("Build Size Total (m²)", value=120)
construction_cost_per_m2 = st.sidebar.number_input("Construction Cost per m² ($)", value=2000)
build_duration = st.sidebar.number_input("Build Duration (months)", value=9)
start_offset = st.sidebar.number_input("First Unit Start Month", value=3)

st.sidebar.header("Finance")
land_lvr = st.sidebar.slider("Land Loan LVR", 0.0, 1.0, 0.7)
loan_portion = st.sidebar.slider("Construction Loan Portion", 0.0, 1.0, 0.7)

soft_costs = st.sidebar.number_input("Soft Costs ($)", value=80000)

if st.sidebar.button("🚀 Run Feasibility"):
    unit_data = []
    for i in range(int(units)):
        unit = {
            "label": f"Unit {i+1}",
            "size": construction_size_m2,
            "rate": construction_cost_per_m2,
            "start": int(start_offset + i * 2),
            "duration": int(build_duration),
            "sale": sale_price
        }
        unit_data.append(unit)

    equity_land = land_price * (1 - land_lvr)
    loan_land = land_price * land_lvr

    cashflow = {
        "Month": [],
        "Month Name": [],
        "Cash Out ($)": [],
        "Loan In ($)": [],
        "Cumulative Cash ($)": [],
        "Loan Balance ($)": [],
        "Net Cash Position ($)": [],
    }

    cash_months = {}
    loan_months = {}

    cash_months[0] = equity_land + soft_costs
    loan_months[0] = loan_land

    for unit in unit_data:
        total = unit["size"] * unit["rate"]
        per_month = total / unit["duration"]
        for m in range(unit["start"], unit["start"] + unit["duration"]):
            cash_months[m] = cash_months.get(m, 0) + per_month * 0.3
            loan_months[m] = loan_months.get(m, 0) + per_month * 0.7
        sale_month = unit["start"] + unit["duration"] + 1
        cash_months[sale_month] = cash_months.get(sale_month, 0) - unit["sale"]

    max_month = max(max(cash_months), max(loan_months))
    cum_cash = cum_loan = 0

    for m in range(max_month + 2):
        label = (datetime(2025, 3, 1) + relativedelta(months=m)).strftime("%b-%Y")
        cash = cash_months.get(m, 0)
        loan = loan_months.get(m, 0)
        cum_cash += cash
        cum_loan += loan
        cashflow["Month"].append(m)
        cashflow["Month Name"].append(label)
        cashflow["Cash Out ($)"].append(cash)
        cashflow["Loan In ($)"].append(loan)
        cashflow["Cumulative Cash ($)"].append(cum_cash)
        cashflow["Loan Balance ($)"].append(cum_loan)
        cashflow["Net Cash Position ($)"].append(cum_cash - cum_loan)

    df = pd.DataFrame(cashflow)

    # Use last unit sale month to determine true project cost
    last_sale_month = max([u["start"] + u["duration"] + 1 for u in unit_data])
    last_index = df[df["Month"] == last_sale_month].index[0]
    total_project_cost = df["Cumulative Cash ($)"].iloc[last_index - 1] + df["Loan Balance ($)"].iloc[last_index - 1]

    total_sale = sum([u["sale"] for u in unit_data])
    gross_profit = total_sale - total_project_cost
    peak_cash = df["Cumulative Cash ($)"].max()
    roi_cash = (gross_profit / peak_cash) * 100
    roi_total = (gross_profit / total_project_cost) * 100

    grade, color = "F", "🟥"
    if roi_cash >= 80: grade, color = "A+", "🟢"
    elif roi_cash >= 60: grade, color = "A", "🟢"
    elif roi_cash >= 40: grade, color = "B", "🟡"
    elif roi_cash >= 20: grade, color = "C", "🟠"
    elif roi_cash > 0: grade, color = "D", "🔴"

    st.subheader("📊 Financial Summary")
    st.markdown(f"- **Land Cost:** ${land_price:,.0f}")
    st.markdown(f"- **Soft Costs:** ${soft_costs:,.0f}")
    st.markdown(f"- **Total Sale Value:** ${total_sale:,.0f}")
    st.markdown(f"- **Total Project Cost:** ${total_project_cost:,.0f}")
    st.markdown(f"- **Gross Profit:** ${gross_profit:,.0f}")
    st.markdown(f"- **ROI on Cost:** {roi_total:.1f}%")
    st.markdown(f"- **Cash-on-Cash ROI:** {roi_cash:.1f}%")
    st.markdown(f"- **Peak Cash Invested:** ${peak_cash:,.0f}")
    st.markdown(f"- **Deal Grade:** `{grade}` {color}")

    st.subheader("📈 Cashflow Overview")
    fig, ax = plt.subplots(figsize=(14, 6))
    ax.plot(df["Month Name"], df["Cumulative Cash ($)"], label="Cash Invested", marker="o")
    ax.plot(df["Month Name"], df["Loan Balance ($)"], label="Loan Balance", marker="x")
    ax.plot(df["Month Name"], df["Net Cash Position ($)"], label="Net Cash", linestyle="--", color="purple")
    ax.set_xticks(df["Month Name"][::2])
    ax.set_xticklabels(df["Month Name"][::2], rotation=45)
    ax.grid(True)
    ax.legend()
    st.pyplot(fig)

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Download Cashflow CSV", data=csv, file_name="cashflow.csv", mime="text/csv")
