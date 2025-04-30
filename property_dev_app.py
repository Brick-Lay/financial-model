
# MVP: Property Development Feasibility App with Per-Unit Costing and Timeline Staging

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from dateutil.relativedelta import relativedelta

st.set_page_config(page_title="Feasibility Tool", layout="wide")
st.title("🏗️ Multi-Unit Property Development Feasibility App")

# --- Unit Manager ---
if "units" not in st.session_state:
    st.session_state.units = []

# --- Add Unit Form ---
with st.expander("➕ Add New Unit"):
    name = st.text_input("Unit Label (e.g. TH-01)")
    build_size = st.number_input("Build Size (m²)", value=100)
    cost_per_m2 = st.number_input("Cost per m² ($)", value=2000)
    contingency_pct = st.slider("Contingency (%)", 0.0, 0.3, 0.1)
    start_month = st.number_input("Start Month", value=0)
    duration = st.number_input("Build Duration (months)", value=9)
    sale_price = st.number_input("Sale Price ($)", value=750000)
    if st.button("Add Unit"):
        st.session_state.units.append({
            "label": name,
            "size": build_size,
            "rate": cost_per_m2,
            "contingency": contingency_pct,
            "start": int(start_month),
            "duration": int(duration),
            "sale": sale_price
        })

# --- Unit List ---
st.subheader("📋 Project Units")
if st.session_state.units:
    for i, unit in enumerate(st.session_state.units):
        with st.expander(f"{unit['label']}"):
            st.markdown(f"**Build Size:** {unit['size']} m²")
            st.markdown(f"**Rate:** ${unit['rate']:,.0f} /m²")
            st.markdown(f"**Contingency:** {unit['contingency']*100:.1f}%")
            st.markdown(f"**Start Month:** {unit['start']}")
            st.markdown(f"**Duration:** {unit['duration']} months")
            st.markdown(f"**Sale Price:** ${unit['sale']:,.0f}")
            if st.button(f"❌ Remove {unit['label']}", key=f"rm_{i}"):
                st.session_state.units.pop(i)
                st.experimental_rerun()
else:
    st.info("Add at least one unit to begin.")

# --- Global Inputs ---
st.sidebar.header("Global Project Settings")
land_price = st.sidebar.number_input("Land Purchase Price ($)", value=500000)
land_lvr = st.sidebar.slider("Land Loan LVR", 0.0, 1.0, 0.7)
interest_rate = st.sidebar.number_input("Interest Rate (%)", value=6.5) / 100
soft_costs = st.sidebar.number_input("Total Soft Costs ($)", value=80000)
months_to_settlement = st.sidebar.number_input("Months to Land Settlement", value=3)

# --- Run Button ---
if st.button("🚀 Run Feasibility") and st.session_state.units:
    land_equity = land_price * (1 - land_lvr)
    land_loan = land_price * land_lvr

    cashflow = {
        "Month": [],
        "Month Name": [],
        "Cash Out ($)": [],
        "Loan In ($)": [],
        "Cumulative Cash ($)": [],
        "Loan Balance ($)": [],
        "Net Cash Position ($)": [],
    }

    monthly_cash = {}
    monthly_loan = {}

    # Schedule land settlement + soft costs
    monthly_cash[months_to_settlement] = land_equity + soft_costs
    monthly_loan[months_to_settlement] = land_loan

    for unit in st.session_state.units:
        start = unit["start"]
        end = start + unit["duration"]
        total_cost = unit["size"] * unit["rate"]
        contingency = unit["contingency"] * total_cost
        total_with_contingency = total_cost + contingency
        monthly_draw = total_cost / unit["duration"]
        monthly_contingency = contingency / unit["duration"]
        for m in range(start, end):
            monthly_cash[m] = monthly_cash.get(m, 0) + (monthly_draw * 0.3 + monthly_contingency * 0.3)
            monthly_loan[m] = monthly_loan.get(m, 0) + (monthly_draw * 0.7 + monthly_contingency * 0.7)
        sale_month = end + 1
        monthly_cash[sale_month] = monthly_cash.get(sale_month, 0) - unit["sale"]

    max_month = max(max(monthly_cash), max(monthly_loan))
    cum_cash = cum_loan = 0
    for m in range(max_month + 2):
        date = datetime(2025, 3, 1) + relativedelta(months=m)
        label = date.strftime("%b-%Y")
        cash = monthly_cash.get(m, 0)
        loan = monthly_loan.get(m, 0)
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

    # Estimate total cost before any sale proceeds
    sale_months = [unit["start"] + unit["duration"] + 1 for unit in st.session_state.units]
    sale_index = min([df[df["Month"] == m].index[0] for m in sale_months if m in df["Month"].values])
    total_project_cost = df["Cumulative Cash ($)"].iloc[sale_index - 1] + df["Loan Balance ($)"].iloc[sale_index - 1]
    sale_total = sum([u["sale"] for u in st.session_state.units])
    gross_profit = sale_total - total_project_cost
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
    st.markdown(f"- **Total Sale Value:** ${sale_total:,.0f}")
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
    st.download_button("📥 Download Cashflow CSV", data=csv, file_name="multi_unit_cashflow.csv", mime="text/csv")
