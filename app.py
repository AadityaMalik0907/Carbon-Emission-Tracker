import streamlit as st
import matplotlib.pyplot as plt
from datetime import datetime
from carbon_calculator import calculate_emissions
from carbon_database import log_emission, get_user_emissions
st.set_page_config(page_title="Carbon Emission Tracker", layout="wide")
st.title("Carbon Emission Tracker")
st.sidebar.header("User Login")
user_id = st.sidebar.text_input("Enter your User ID")
today = datetime.now().strftime("%Y-%m-%d")
st.sidebar.markdown("Don't have an account? Generate your UID in Firebase Console.")
st.header("Enter Your Weekly Activities")
with st.form("activity_form"):
    electricity = st.number_input("Electricity (kWh)", min_value=0.0)
    petrol = st.number_input("Petrol (litres)", min_value=0.0)
    diesel = st.number_input("Diesel (litres)", min_value=0.0)
    natural_gas = st.number_input("Natural Gas (m³)", min_value=0.0)
    organic_waste = st.number_input("Organic Waste (kg)", min_value=0.0)
    paper = st.number_input("Paper (kg)", min_value=0.0)
    plastic = st.number_input("Plastic (kg)", min_value=0.0)
    submitted = st.form_submit_button("Calculate & Save")
if submitted and user_id:
    user_data = {
        'electricity': electricity,
        'petrol': petrol,
        'diesel': diesel,
        'natural_gas': natural_gas,
        'organic_waste': organic_waste,
        'paper': paper,
        'plastic': plastic
    }
    total, breakdown = calculate_emissions(user_data)
    st.success(f"Total Emission: {total:.2f} kg CO2")
    st.subheader("Emission Breakdown")
    fig1, ax1 = plt.subplots()
    ax1.bar(breakdown.keys(), breakdown.values(), color="red")
    ax1.set_ylabel("CO2 Emission (kg)")
    ax1.set_title("Carbon Emission by Activity")
    st.pyplot(fig1)
    fig2, ax2 = plt.subplots()
    ax2.pie(breakdown.values(), labels=breakdown.keys(), autopct='%1.1f%%', startangle=140)
    ax2.axis("equal")
    st.pyplot(fig2)
    log_emission(user_id, breakdown)
st.header("Weekly Emission Comparison")

col1, col2 = st.columns(2)
with col1:
    week1 = st.text_input("Week 1 Dates (comma-separated, e.g. 2025-06-01,2025-06-02)")
with col2:
    week2 = st.text_input("Week 2 Dates (comma-separated, e.g. 2025-06-08,2025-06-09)")

if st.button("Compare Weeks") and user_id:
    data = get_user_emissions(user_id)
    if data:
        week1_dates = [d.strip() for d in week1.split(",") if d.strip() in data]
        week2_dates = [d.strip() for d in week2.split(",") if d.strip() in data]

        week1_total = sum(data[d]['total_emission'] for d in week1_dates)
        week2_total = sum(data[d]['total_emission'] for d in week2_dates)

        st.subheader("Comparison Result")
        fig, ax = plt.subplots()
        ax.bar(["Week 1", "Week 2"], [week1_total, week2_total], color=["orange", "blue"])
        ax.set_ylabel("Total CO2 Emission (kg)")
        ax.set_title("Weekly Emission Comparison")
        st.pyplot(fig)
    else:
        st.warning("No emission data found for this user.")
