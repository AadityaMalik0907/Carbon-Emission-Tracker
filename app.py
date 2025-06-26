import streamlit as st
import matplotlib.pyplot as plt
from datetime import datetime
from carbon_calculator import calculate_emissions, EMISSION_FACTORS
from carbon_database import log_emission, get_user_emissions, sign_up

st.set_page_config(page_title="Carbon Emission Tracker", layout="wide")
st.title("Carbon Emission Tracker")

# ------------------------ Emission Input Section ------------------------ #
st.header("Enter Your Daily Activity Data")
inputs = {}

cols = st.columns(3)
for i, (activity, factor) in enumerate(EMISSION_FACTORS.items()):
    with cols[i % 3]:
        qty = st.number_input(f"{activity.title()} ({factor} kg CO2/unit)", min_value=0.0, step=0.1)
        inputs[activity] = qty

if st.button("Calculate"):
    total, breakdown = calculate_emissions(inputs)
    st.metric("Total Emissions", f"{total:.2f} kg CO₂")
    st.session_state["latest_inputs"] = inputs
    st.session_state["latest_total"] = total
    st.session_state["latest_breakdown"] = breakdown

    if total > 0:
        # Bar chart for emission per activity
        fig1, ax1 = plt.subplots()
        bars = ax1.bar(breakdown.keys(), breakdown.values(), color="red")
        ax1.set_title("Carbon Emission per Activity")
        ax1.set_ylabel("CO2 Emission (kg)")
        ax1.set_xlabel("Activity")
        for bar in bars:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width() / 2, height + 1, f"{height:.1f}", ha='center')
        st.pyplot(fig1)

        # Pie chart for emission share
        fig2, ax2 = plt.subplots()
        ax2.pie(breakdown.values(), labels=breakdown.keys(), autopct='%1.1f%%', startangle=140)
        ax2.set_title('Carbon Emission Share by Activity')
        ax2.axis('equal')
        st.pyplot(fig2)

        # Comparison with ideal value
        ideal = 70
        fig3, ax3 = plt.subplots()
        ax3.bar(["Ideal Emission", "Your Emission"], [ideal, total], color=["green", "blue"])
        ax3.set_title("Comparison with Ideal Daily Emission")
        ax3.set_ylabel("kg CO₂")
        for i, val in enumerate([ideal, total]):
            ax3.text(i, val + 1, f"{val:.1f}", ha="center")
        st.pyplot(fig3)

        # Detect spike
        if total > 100:
            st.warning("Your carbon emission is significantly high today. Consider reducing energy or fuel usage.")

        if st.button("Save my data (requires login)"):
            st.session_state.show_login = True
    else:
        st.info("Please enter values greater than 0 to see the charts.")

if st.session_state.get("show_login"):
    st.subheader("Login or Sign Up to Save Data")
    auth_mode = st.radio("Mode", ["Login", "Sign Up"])
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Submit"):
        if email and password:
            try:
                if auth_mode == "Sign Up":
                    uid = sign_up(email, password)
                    st.success("Account created. Data saved.")
                else:
                    uid = "user:" + email
                    st.success("Logged in. Data saved.")
                log_emission(uid, st.session_state["latest_breakdown"])
                st.session_state["user_id"] = uid
                st.session_state.show_login = False
            except Exception as e:
                st.error(f"Auth failed: {e}")
        else:
            st.warning("Please enter email and password")

# ------------------------ Emission History & Graphs ------------------------ #
if st.session_state.get("user_id") and st.button("Show My Emission Charts"):
    history = get_user_emissions(st.session_state["user_id"])
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