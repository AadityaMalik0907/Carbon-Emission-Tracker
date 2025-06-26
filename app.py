import streamlit as st
import matplotlib.pyplot as plt
from carbon_database import log_emission, get_user_emissions
from datetime import datetime

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
    # Debug: Check the breakdown data
    st.write("Breakdown data:", breakdown)
    non_zero_breakdown = {k: v for k, v in breakdown.items() if v > 0}
    
    if not non_zero_breakdown:
        st.warning("No non-zero emissions to display. Showing all data for debugging.")
        non_zero_breakdown = breakdown  # Fallback to show all data

    # Bar chart
    fig1, ax1 = plt.subplots(figsize=(6, 4))
    bars = ax1.bar(non_zero_breakdown.keys(), non_zero_breakdown.values(), color="red")
    ax1.set_title("Carbon Emission per Activity")
    ax1.set_ylabel("CO2 Emission (kg)")
    ax1.set_xlabel("Activity")
    ax1.tick_params(axis='x', rotation=45, labelsize=8)
    for bar in bars:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width() / 2, height + 0.1, f"{height:.1f}", ha='center', fontsize=8)
    plt.tight_layout()
    st.pyplot(fig1)
    plt.close(fig1)

    # Pie chart
    fig2, ax2 = plt.subplots(figsize=(5, 5))
    ax2.pie(non_zero_breakdown.values(), labels=non_zero_breakdown.keys(), autopct='%1.1f%%', startangle=140, textprops={'fontsize': 8})
    ax2.set_title('Carbon Emission Share by Activity')
    ax2.axis('equal')
    plt.tight_layout()
    st.pyplot(fig2)
    plt.close(fig2)

def comparisons(user_id, week1_dates, week2_dates):
    data = get_user_emissions(user_id)
    if not data:
        st.warning("No emission data available.")
        return

    week1_total = sum(data[d]['total_emission'] for d in data if d in week1_dates)
    week2_total = sum(data[d]['total_emission'] for d in data if d in week2_dates)
    weeks = ['Week 1', 'Week 2']
    values = [week1_total, week2_total]

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(weeks, values, color=['yellow', 'orange'])
    ax.set_title('Weekly Carbon Emission Comparison')
    ax.set_ylabel('CO2 Emission (kg)')
    ax.set_xlabel('Week')
    for i, val in enumerate(values):
        ax.text(i, val + 0.1, f"{val:.1f}", ha='center', fontsize=8)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

def get_ideal_comparison_graph(user_total):
    ideal = 70  # kg per day (example)
    categories = ['Ideal Emission', 'Your Emission']
    values = [ideal, user_total]

    fig, ax = plt.subplots(figsize=(4, 3))
    ax.bar(categories, values, color=['green', 'red'])
    ax.set_title('Comparison with Ideal Daily Emission')
    ax.set_ylabel('kg CO₂')
    for i, val in enumerate(values):
        ax.text(i, val + 1, f'{val:.1f}', ha='center', fontsize=8)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

def main():
    st.title("Carbon Emission Tracker")

    # User input section
    st.header("Enter Your Daily Activity Data")
    inputs = {}
    cols = st.columns(3)
    for i, (activity, factor) in enumerate(EMISSION_FACTORS.items()):
        with cols[i % 3]:
            qty = st.number_input(f"{activity.title()} ({factor} kg CO2/unit)", min_value=0.0, step=0.1, key=f"{activity}_input_{i}")
            inputs[activity] = qty

    if st.button("Calculate Emissions"):
        try:
            total_emission, breakdown = calculate_emissions(inputs)
            st.metric("Total Emissions", f"{total_emission:.2f} kg CO₂")
            st.session_state["latest_breakdown"] = breakdown
            st.session_state["latest_total"] = total_emission

            # Display plots
            st.write("Attempting to plot carbon data...")
            plot_carbon(breakdown)
            get_ideal_comparison_graph(total_emission)

            # Save data option
            if st.button("Save Data (Requires Login)"):
                st.session_state.show_login = True

        except ValueError as e:
            st.error(f"Error: {e}")
        except Exception as e:
            st.error(f"Unexpected error: {e}")

    # Login section
    if st.session_state.get("show_login", False):
        st.subheader("Login or Sign Up to Save Data")
        auth_mode = st.radio("Mode", ["Login", "Sign Up"])
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        if st.button("Submit"):
            if email and password:
                try:
                    # Placeholder for actual auth (replace with Firebase logic)
                    uid = f"user:{email}" if auth_mode == "Login" else "signup_placeholder"
                    st.success(f"{auth_mode} successful. Data saved.")
                    if "latest_breakdown" in st.session_state:
                        log_emission(uid, st.session_state["latest_breakdown"])
                    st.session_state["user_id"] = uid
                    st.session_state.show_login = False
                except Exception as e:
                    st.error(f"Authentication failed: {str(e)}")
            else:
                st.warning("Please enter both email and password.")

    # Emission history section
    if st.session_state.get("user_id") and st.button("Show Weekly Comparison"):
        try:
            # Define sample weeks based on current date (June 26, 2025)
            current_date = datetime.now().strftime("%Y-%m-%d")
            week1_dates = [current_date]
            week2_dates = [(datetime.now() - datetime.timedelta(days=7)).strftime("%Y-%m-%d")]
            comparisons(st.session_state["user_id"], week1_dates, week2_dates)
        except Exception as e:
            st.error(f"Error fetching comparison data: {e}")

if __name__ == "__main__":
    main()