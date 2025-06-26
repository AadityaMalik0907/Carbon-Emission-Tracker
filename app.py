import streamlit as st
import matplotlib.pyplot as plt
from datetime import datetime
from carbon_calculator import calculate_emissions, EMISSION_FACTORS
from carbon_database import log_emission, get_user_emissions, sign_up

st.set_page_config(page_title="Carbon Emission Tracker", layout="wide")
st.title("🌱 Carbon Emission Tracker")

# ------------------------ Login / Signup Section ------------------------ #
st.sidebar.header("🔐 User Authentication")
auth_mode = st.sidebar.radio("Login or Sign Up", ["Login", "Sign Up"])
email = st.sidebar.text_input("Email", key="email")
password = st.sidebar.text_input("Password", type="password", key="password")

if "user_id" not in st.session_state:
    st.session_state["user_id"] = None

if st.sidebar.button("Submit"):
    if email and password:
        try:
            if auth_mode == "Sign Up":
                uid = sign_up(email, password)
                st.sidebar.success("Account created.")
            else:
                uid = "user:" + email  # Fake login ID for demo
            st.session_state["user_id"] = uid
            st.rerun()
        except Exception as e:
            st.sidebar.error(f"Auth failed: {e}")
    else:
        st.sidebar.warning("Please fill both fields.")

user_id = st.session_state.get("user_id")
if not user_id:
    st.info("Please log in to use the tracker.")
    st.stop()

# ------------------------ Emission Input Section ------------------------ #
st.header("Enter Your Daily Activity Data")
inputs = {}

cols = st.columns(3)
for i, (activity, factor) in enumerate(EMISSION_FACTORS.items()):
    with cols[i % 3]:
        qty = st.number_input(f"{activity.title()} ({factor} kg CO2/unit)", min_value=0.0, step=0.1)
        inputs[activity] = qty

if st.button("Calculate and Save"):
    total = calculate_emissions(inputs)
    st.metric("Total Emissions", f"{total:.2f} kg CO₂")
    log_emission(user_id, inputs)
    st.success("Emission data saved!")

# ------------------------ Emission History & Graphs ------------------------ #
st.header("📈 Emission History & Charts")
if st.button("Show My Emission Charts"):
    history = get_user_emissions(user_id)
    if history:
        dates = []
        totals = []
        activity_totals = {k: 0 for k in EMISSION_FACTORS.keys()}

        for date, entry in sorted(history.items()):
            dates.append(date)
            totals.append(entry['total_emission'])
            for k, v in entry['activities'].items():
                activity_totals[k] += v * EMISSION_FACTORS.get(k, 0)

        fig, ax = plt.subplots()
        ax.plot(dates, totals, marker='o')
        ax.set_title("Total Emissions Over Time")
        ax.set_xlabel("Date")
        ax.set_ylabel("kg CO₂")
        st.pyplot(fig)

        fig2, ax2 = plt.subplots()
        ax2.bar(activity_totals.keys(), activity_totals.values())
        ax2.set_title("Cumulative Emissions by Activity")
        ax2.set_ylabel("kg CO₂")
        st.pyplot(fig2)

        fig3, ax3 = plt.subplots()
        ax3.pie(activity_totals.values(), labels=activity_totals.keys(), autopct="%1.1f%%")
        ax3.set_title("Emission Share by Activity")
        st.pyplot(fig3)
    else:
        st.info("No emission data found.")
