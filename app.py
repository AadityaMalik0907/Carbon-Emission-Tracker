import streamlit as st
import matplotlib.pyplot as plt
from carbon_database import log_emission, get_user_emissions
from datetime import datetime, timedelta

# Emission factors
EMISSION_FACTORS = {
    'electricity': 0.277,
    'petrol': 2.31,
    'diesel': 2.68,
    'natural_gas': 2.75,
    'organic_waste': 0.9,
    'paper': 1.7,
    'plastic': 6.0,
}

def calculate_emissions(user_data):
    total_emission = 0
    breakdown = {}
    for activity, amount in user_data.items():
        if activity not in EMISSION_FACTORS:
            raise ValueError(f"Unknown activity: {activity}")
        if amount < 0:
            raise ValueError(f"Amount cannot be negative: {amount}")
        emission = amount * EMISSION_FACTORS[activity]
        breakdown[activity] = emission
        total_emission += emission
    return total_emission, breakdown

def plot_carbon(breakdown):
    st.subheader("Carbon Emission Graphs")

    non_zero_breakdown = {k: v for k, v in breakdown.items() if v > 0}
    if not non_zero_breakdown:
        st.warning("No emissions to display.")

    # Bar chart
    fig1, ax1 = plt.subplots(figsize=(6, 4))
    bars = ax1.bar(non_zero_breakdown.keys(), non_zero_breakdown.values(), color="red")
    ax1.set_title("Carbon Emission per Activity")
    ax1.set_ylabel("CO2 Emission (kg)")
    ax1.set_xlabel("Activity")
    ax1.tick_params(axis='x', rotation=45)
    for bar in bars:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width() / 2, height + 0.05, f"{height:.1f}", ha='center')
    st.pyplot(fig1)

    # Pie chart
    fig2, ax2 = plt.subplots(figsize=(5, 5))
    ax2.pie(non_zero_breakdown.values(), labels=non_zero_breakdown.keys(), autopct='%1.1f%%', startangle=140)
    ax2.set_title('Carbon Emission Share by Activity')
    ax2.axis('equal')
    st.pyplot(fig2)

def comparisons(user_id):
    data = get_user_emissions(user_id)
    if not data:
        st.warning("No emission data available for comparison.")
        return

    today = datetime.now()
    week1_dates = [(today - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(0, 7)]
    week2_dates = [(today - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7, 14)]

    week1_total = sum(data.get(d, {}).get('total_emission', 0) for d in week1_dates)
    week2_total = sum(data.get(d, {}).get('total_emission', 0) for d in week2_dates)

    weeks = ['This Week', 'Last Week']
    values = [week1_total, week2_total]

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(weeks, values, color=['orange', 'green'])
    ax.set_title('Weekly Carbon Emission Comparison')
    ax.set_ylabel('CO2 Emission (kg)')
    for i, val in enumerate(values):
        ax.text(i, val + 0.1, f"{val:.1f}", ha='center')
    st.pyplot(fig)

def get_ideal_comparison_graph(user_total):
    ideal = 70  # kg/day target
    categories = ['Ideal Emission', 'Your Emission']
    values = [ideal, user_total]

    fig, ax = plt.subplots(figsize=(4, 3))
    ax.bar(categories, values, color=['green', 'red'])
    ax.set_title('Ideal vs Your Daily Emission')
    ax.set_ylabel('CO2 (kg)')
    for i, val in enumerate(values):
        ax.text(i, val + 1, f"{val:.1f}", ha='center')
    st.pyplot(fig)

def main():
    st.title("🌿 Carbon Emission Tracker")

    st.header("Enter Your Daily Activity Data")
    inputs = {}
    cols = st.columns(3)
    for i, (activity, factor) in enumerate(EMISSION_FACTORS.items()):
        with cols[i % 3]:
            qty = st.number_input(f"{activity.title()} ({factor} kg CO2/unit)", min_value=0.0, step=0.1, key=f"{activity}_input")
            inputs[activity] = qty

    if st.button("Calculate Emissions"):
        try:
            total_emission, breakdown = calculate_emissions(inputs)
            st.metric("Total Emissions", f"{total_emission:.2f} kg CO₂")

            st.session_state["latest_breakdown"] = breakdown
            st.session_state["latest_total"] = total_emission

            plot_carbon(breakdown)
            get_ideal_comparison_graph(total_emission)

            if st.button("Save Data (Login Required)"):
                st.session_state.show_login = True

        except ValueError as e:
            st.error(f"Error: {e}")

    if st.session_state.get("show_login", False):
        st.subheader("Login or Sign Up to Save Data")
        mode = st.radio("Mode", ["Login", "Sign Up"])
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        if st.button("Submit"):
            if email and password:
                try:
                    uid = f"user:{email}" if mode == "Login" else "signup_placeholder"
                    st.success(f"{mode} successful. Data saved.")
                    if "latest_breakdown" in st.session_state:
                        log_emission(uid, st.session_state["latest_breakdown"])
                    st.session_state["user_id"] = uid
                    st.session_state.show_login = False
                except Exception as e:
                    st.error(f"Authentication failed: {e}")
            else:
                st.warning("Please enter both email and password.")

    if st.session_state.get("user_id") and st.button("Show Weekly Comparison"):
        comparisons(st.session_state["user_id"])

if __name__ == "__main__":
    main()
