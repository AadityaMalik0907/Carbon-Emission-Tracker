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

# Session state defaults
for key in ["show_login", "user_id", "latest_breakdown", "latest_total"]:
    if key not in st.session_state:
        st.session_state[key] = None if key == "user_id" else False if key == "show_login" else None

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
    st.subheader("📊 Carbon Emission Graphs")

    non_zero_breakdown = {k: v for k, v in breakdown.items() if v > 0}
    if not non_zero_breakdown:
        st.info("No emissions to display.")
        return

    # Bar chart
    fig1, ax1 = plt.subplots(figsize=(5, 3))
    bars = ax1.bar(non_zero_breakdown.keys(), non_zero_breakdown.values(), color="#FF6F61")
    ax1.set_title("Carbon Emission by Activity", fontsize=12)
    ax1.set_ylabel("CO₂ (kg)")
    ax1.set_xlabel("Activity")
    ax1.tick_params(axis='x', rotation=45)
    for bar in bars:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width() / 2, height + 0.2, f"{height:.1f}", ha='center', fontsize=8)
    st.pyplot(fig1)

    # Pie chart
    fig2, ax2 = plt.subplots(figsize=(4, 3))
    ax2.pie(non_zero_breakdown.values(), labels=non_zero_breakdown.keys(), autopct='%1.1f%%',
            startangle=140, textprops={'fontsize': 7}, colors=plt.cm.Paired.colors)
    ax2.set_title("Emission Share by Activity", fontsize=11)
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

    fig, ax = plt.subplots(figsize=(4, 2.5))
    ax.bar(weeks, values, color=['#FFA726', '#66BB6A'])
    ax.set_title("Weekly Emission Comparison", fontsize=11)
    ax.set_ylabel("CO₂ (kg)")
    for i, val in enumerate(values):
        ax.text(i, val + 0.5, f"{val:.1f}", ha='center', fontsize=9)
    st.pyplot(fig)

def get_ideal_comparison_graph(user_total):
    ideal = 70
    categories = ['Ideal', 'You']
    values = [ideal, user_total]

    fig, ax = plt.subplots(figsize=(3.5, 2.5))
    ax.bar(categories, values, color=['#81C784', '#E57373'])
    ax.set_title("Your Emission vs Ideal", fontsize=11)
    ax.set_ylabel("CO₂ (kg)")
    for i, val in enumerate(values):
        ax.text(i, val + 0.8, f"{val:.1f}", ha='center', fontsize=9)
    st.pyplot(fig)

def main():
    st.title("🌿 Carbon Emission Tracker")

    st.header("Enter Your Daily Activity Data")
    inputs = {}
    cols = st.columns(3)
    for i, (activity, factor) in enumerate(EMISSION_FACTORS.items()):
        with cols[i % 3]:
            qty = st.number_input(f"{activity.title()} ({factor} kg CO₂/unit)", min_value=0.0, step=0.1, key=f"{activity}_input")
            inputs[activity] = qty

    if st.button("Calculate Emissions"):
        try:
            total_emission, breakdown = calculate_emissions(inputs)
            st.metric("Total Emissions", f"{total_emission:.2f} kg CO₂")
            st.session_state.latest_breakdown = breakdown
            st.session_state.latest_total = total_emission
            plot_carbon(breakdown)
            get_ideal_comparison_graph(total_emission)

            if st.button("Save Data (Login Required)"):
                st.session_state.show_login = True

        except ValueError as e:
            st.error(f"Error: {e}")

    # Show last results if present
    if st.session_state.latest_breakdown:
        st.subheader("Previous Results")
        st.metric("Last Total Emissions", f"{st.session_state.latest_total:.2f} kg CO₂")
        plot_carbon(st.session_state.latest_breakdown)
        get_ideal_comparison_graph(st.session_state.latest_total)

    # Login section
    if st.session_state.show_login:
        st.subheader("Login / Sign Up to Save Data")
        mode = st.radio("Mode", ["Login", "Sign Up"])
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        if st.button("Submit Login"):
            if email and password:
                try:
                    uid = f"user:{email}" if mode == "Login" else "signup_placeholder"
                    st.success(f"{mode} successful. Data saved.")
                    if st.session_state.latest_breakdown:
                        log_emission(uid, st.session_state.latest_breakdown)
                    st.session_state.user_id = uid
                    st.session_state.show_login = False
                except Exception as e:
                    st.error(f"Authentication failed: {e}")
            else:
                st.warning("Please enter both email and password.")

    # Weekly comparison
    if st.session_state.user_id and st.button("Show Weekly Comparison"):
        comparisons(st.session_state.user_id)

if __name__ == "__main__":
    main()
