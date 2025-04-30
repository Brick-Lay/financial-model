
# Final MVP: Feasibility App with Correct Total Project Cost Calculation

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from dateutil.relativedelta import relativedelta

st.set_page_config(layout="wide")
st.title("🏗️ Property Development Feasibility App (Multi-Unit MVP)")

if "units" not in st.session_state:
    st.session_state.units = []

st.sidebar.header("Global Inputs")
land_price = st.sidebar.number_input("Land Price ($)", value=1350000)
land_lvr = st.sidebar.slider("Land LVR", 0.0, 1.0, 0.7)
interest_rate = st.sidebar.number_input("Interest Rate (%)", value=6.5) / 100
soft_costs = st.sidebar.number_input("Soft Costs ($)", value=80000)
start_offset = st.sidebar.number_input("Initial Start Month", value=3)

with st.expander("➕ Add Unit"):
    label = st.text_input("Unit Label", value=f"Unit {len(st.session_state.units)+1}")
    size = st.number_input("Build Size (m²)", value=120)
    rate = st.number_input("Cost per m² ($)", value=2000)
    cont = st.slider("Contingency (%)", 0.0, 0.3, 0.1)
    start = st.number_input("Start Month", value=start_offset)
    dur = st.number_input("Build Duration (months)", value=9)
    sale = st.number_input("Sale Price ($)", value=850000)
    if st.button("Add Unit"):
        st.session_state.units.append({
            "label": label, "size": size, "rate": rate, "cont": cont,
            "start": int(start), "duration": int(dur), "sale": sale
        })

if st.session_state.units:
    st.subheader("📋 Units")
    for i, u in enumerate(st.session_state.units):
        with st.expander(f"{u['label']}"):
            st.markdown(f"- Size: {u['size']} m²")
            st.markdown(f"- Rate: ${u['rate']:,.0f}")
            st.markdown(f"- Contingency: {u['cont']*100:.1f}%")
            st.markdown(f"- Start: Month {u['start']}")
            st.markdown(f"- Duration: {u['duration']} months")
            st.markdown(f"- Sale: ${u['sale']:,.0f}")
            if st.button(f"Remove {u['label']}", key=f"del_{i}"):
                st.session_state.units.pop(i)
                st.experimental_rerun()

if st.button("🚀 Run Feasibility") and st.session_state.units:
    cash_months, loan_months = {}, {}
    equity_land = land_price * (1 - land_lvr)
    loan_land = land_price * land_lvr
    cash_months[0] = equity_land + soft_costs
    loan_months[0] = loan_land

    for u in st.session_state.units:
        cost = u["size"] * u["rate"]
        cont = u["cont"] * cost
        total = cost + cont
        per_month = total / u["duration"]
        for m in range(u["start"], u["start"] + u["duration"]):
            cash_months[m] = cash_months.get(m, 0) + per_month * 0.3
            loan_months[m] = loan_months.get(m, 0) + per_month * 0.7
        sale_m = u["start"] + u["duration"] + 1
        cash_months[sale_m] = cash_months.get(sale_m, 0) - u["sale"]

    max_month = max(max(cash_months), max(loan_months))
    cashflow = {
        "Month": [], "Month Name": [], "Cash Out ($)": [], "Loan In ($)": [],
        "Cumulative Cash ($)": [], "Loan Balance ($)": [], "Net Cash Position ($)": []
    }

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

    # ✅ NEW FIX: Use first unit's sale month to exclude proceeds from total cost
    sale_months = [u["start"] + u["duration"] + 1 for u in st.session_state.units]
    first_sale_month = min(sale_months)
    first_sale_index = df[df["Month"] == first_sale_month].index[0]
    total_project_cost = df["Cumulative Cash ($)"].iloc[first_sale_index - 1] + df["Loan Balance ($)"].iloc[first_sale_index - 1]

    total_sale = sum(u["sale"] for u in st.session_state.units)
    profit = total_sale - total_project_cost
    peak_cash = df["Cumulative Cash ($)"].max()
    roi_cash = (profit / peak_cash) * 100
    roi_total = (profit / total_project_cost) * 100

    grade, color = "F", "🟥"
    if roi_cash >= 80: grade, color = "A+", "🟢"
    elif roi_cash >= 60: grade, color = "A", "🟢"
    elif roi_cash >= 40: grade, color = "B", "🟡"
    elif roi_cash >= 20: grade, color = "C", "🟠"
    elif roi_cash > 0: grade, color = "D", "🔴"

    st.subheader("📊 Summary")
    st.markdown(f"- **Total Sale Value:** ${total_sale:,.0f}")
    st.markdown(f"- **Total Project Cost:** ${total_project_cost:,.0f}")
    st.markdown(f"- **Gross Profit:** ${profit:,.0f}")
    st.markdown(f"- **ROI on Cost:** {roi_total:.1f}%")
    st.markdown(f"- **Cash-on-Cash ROI:** {roi_cash:.1f}%")
    st.markdown(f"- **Peak Cash Invested:** ${peak_cash:,.0f}")
    st.markdown(f"- **Deal Grade:** `{grade}` {color}")

    st.subheader("📈 Cashflow Chart")
    fig, ax = plt.subplots(figsize=(14, 6))
    ax.plot(df["Month Name"], df["Cumulative Cash ($)"], label="Cash Invested", marker="o")
    ax.plot(df["Month Name"], df["Loan Balance ($)"], label="Loan", marker="x")
    ax.plot(df["Month Name"], df["Net Cash Position ($)"], label="Net Position", linestyle="--", color="purple")
    ax.set_xticks(df["Month Name"][::2])
    ax.set_xticklabels(df["Month Name"][::2], rotation=45)
    ax.grid(True)
    ax.legend()
    st.pyplot(fig)

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Download Cashflow CSV", data=csv, file_name="cashflow.csv", mime="text/csv")
