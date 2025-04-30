
import streamlit as st
import pandas as pd

st.title("🏗️ Property Development Feasibility App")

st.sidebar.header("Inputs")
project_name = st.sidebar.text_input("Project Name", value="My Project")
land_price = st.sidebar.number_input("Land Price ($)", value=500000)
sale_price = st.sidebar.number_input("Sale Price per Unit ($)", value=750000)
units = st.sidebar.number_input("Number of Units", value=2)

if st.sidebar.button("🚀 Run Feasibility"):
    total_sale = sale_price * units
    st.subheader("📊 Summary")
    st.markdown(f"**Project Name:** {project_name}")
    st.markdown(f"**Land Purchase Price:** ${land_price:,.0f}")
    st.markdown(f"**Sale Value:** ${total_sale:,.0f}")
