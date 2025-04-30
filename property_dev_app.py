
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from dateutil.relativedelta import relativedelta

st.title("🏗️ Property Development Feasibility App")

# --- Sidebar Inputs ---
st.sidebar.header("Project Info")
project_name = st.sidebar.text_input("Project Name", value="My Project")

st.sidebar.header("Land & Sales")
land_price = st.sidebar.number_input("Land Price ($)", value=500000)
sale_price = st.sidebar.number_input("Sale Price per Unit ($)", value=750000)
units = st.sidebar.number_input("Number of Units", value=2)

st.sidebar.header("Construction")
construction_size_m2 = st.sidebar.number_input("Build Size Total (m²)", value=200)
construction_cost_per_m2 = st.sidebar.number_input("Construction Cost per m² ($)", value=2000)

st.sidebar.header("Finance")
land_lvr = st.sidebar.slider("Land Loan LVR", 0.0, 1.0, 0.7)
loan_on_construction_percent = st.sidebar.slider("Construction Loan Portion", 0.0, 1.0, 0.7)
interest_rate = st.sidebar.number_input("Interest Rate (%)", value=6.5) / 100

st.sidebar.header("Timeline")
months_to_settlement = st.sidebar.number_input("Months to Settlement", value=3)
months_to_start = st.sidebar.number_input("Months to Start Build (after settlement)", value=3)
build_duration = st.sidebar.number_input("Build Duration (months)", value=9)
draws = st.sidebar.number_input("Number of Draws", value=5, min_value=1)

# --- Advanced Costs ---
with st.sidebar.expander("⚙️ Advanced Costs"):
    contingency_percent = st.slider("Contingency on Construction (%)", 0.0, 0.3, 0.1)
    stamp_duty = st.number_input("Stamp Duty ($)", value=30000)
    legal_fees = st.number_input("Legal Fees ($)", value=3000)
    consultants = st.number_input("Consultants ($)", value=10000)
    permits = st.number_input("Permits & Planning ($)", value=8000)
    insurance = st.number_input("Insurance & Bonds ($)", value=5000)
    connections = st.number_input("Utility Connections ($)", value=15000)

if st.sidebar.button("🚀 Run Feasibility"):
    sale_value = sale_price * units
    construction_cost = construction_cost_per_m2 * construction_size_m2
    contingency = contingency_percent * construction_cost
    total_construction_cost = construction_cost + contingency
    equity_land = land_price * (1 - land_lvr)
    loan_land = land_price * land_lvr
    soft_costs = stamp_duty + legal_fees + consultants + permits + insurance + connections

    draw_amount = construction_cost / draws
    draw_months = [months_to_settlement + months_to_start + i * (build_duration // draws) for i in range(draws)]
    sale_month = months_to_settlement + months_to_start + build_duration + 1

    cashflow = {
        "Month": [],
        "Month Name": [],
        "Cash Out ($)": [],
        "Loan In ($)": [],
        "Cumulative Cash ($)": [],
        "Loan Balance ($)": [],
        "Net Cash Position ($)": [],
    }

    cash_cum = 0
    loan_cum = 0

    for m in range(sale_month + 2):
        label = (datetime(2025, 3, 1) + relativedelta(months=m)).strftime("%b-%Y")
        cash = 0
        loan = 0
        if m == months_to_settlement:
            cash += equity_land + soft_costs
            loan += loan_land
        if m in draw_months:
            cash += draw_amount * 0.3
            loan += draw_amount * 0.7
        if m == sale_month:
            cash -= sale_value

        cash_cum += cash
        loan_cum += loan
        cashflow["Month"].append(m)
        cashflow["Month Name"].append(label)
        cashflow["Cash Out ($)"].append(cash)
        cashflow["Loan In ($)"].append(loan)
        cashflow["Cumulative Cash ($)"].append(cash_cum)
        cashflow["Loan Balance ($)"].append(loan_cum)
        cashflow["Net Cash Position ($)"].append(cash_cum - loan_cum)

    df = pd.DataFrame(cashflow)

    total_project_cost = df["Cumulative Cash ($)"].iloc[-2] + df["Loan Balance ($)"].iloc[-2]
    gross_profit = sale_value - total_project_cost
    roi_total = (gross_profit / total_project_cost) * 100
    peak_cash = df["Cumulative Cash ($)"].max()
    roi_cash = (gross_profit / peak_cash) * 100

    grade, color = "F", "🟥"
    if roi_cash >= 80: grade, color = "A+", "🟢"
    elif roi_cash >= 60: grade, color = "A", "🟢"
    elif roi_cash >= 40: grade, color = "B", "🟡"
    elif roi_cash >= 20: grade, color = "C", "🟠"
    elif roi_cash > 0: grade, color = "D", "🔴"

    st.subheader("📊 Feasibility Summary")
    st.markdown(f"**Project:** `{project_name}`")
    st.markdown(f"- **Total Sale Value:** ${sale_value:,.0f}")
    st.markdown(f"- **Total Construction Cost (incl. contingency):** ${total_construction_cost:,.0f}")
    st.markdown(f"- **Soft Costs:** ${soft_costs:,.0f}")
    st.markdown(f"- **Total Project Cost:** ${total_project_cost:,.0f}")
    st.markdown(f"- **Gross Profit:** ${gross_profit:,.0f}")
    st.markdown(f"- **ROI on Total Cost:** {roi_total:.1f}%")
    st.markdown(f"- **Cash-on-Cash ROI:** {roi_cash:.1f}%")
    st.markdown(f"- **Peak Cash Invested:** ${peak_cash:,.0f}")
    st.markdown(f"- **Deal Grade:** `{grade}` {color}")

    st.subheader("📈 Cashflow Overview")
    fig, ax = plt.subplots(figsize=(14, 6))
    ax.plot(df["Month Name"], df["Cumulative Cash ($)"], label="Cash Invested", marker="o")
    ax.plot(df["Month Name"], df["Loan Balance ($)"], label="Loan Balance", marker="x")
    ax.plot(df["Month Name"], df["Net Cash Position ($)"], label="Net Cash Position", linestyle="--", color="purple")
    ax.set_xticks(df["Month Name"][::2])
    ax.set_xticklabels(df["Month Name"][::2], rotation=45)
    ax.legend()
    ax.grid(True)
    st.pyplot(fig)

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Download Cashflow CSV", data=csv, file_name="cashflow.csv", mime="text/csv")
