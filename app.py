
import streamlit as st
import matplotlib.pyplot as plt
import pdfkit
from io import BytesIO
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
for key in ["show_login", "user_id", "latest_breakdown", "latest_total", "theme"]:
    if key not in st.session_state:
        st.session_state[key] = None if key in ["user_id", "theme"] else False if key == "show_login" else None

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
    non_zero_breakdown = {k: v for k, v in breakdown.items() if v > 0}
    if not non_zero_breakdown:
        st.info("No emissions to display.")
        return

    fig1, ax1 = plt.subplots(figsize=(5, 3))
    bars = ax1.bar(non_zero_breakdown.keys(), non_zero_breakdown.values(), color="#FF6F61")
    ax1.set_ylabel("CO₂ (kg)")
    ax1.set_xlabel("Activity")
    ax1.tick_params(axis='x', rotation=45)
    for bar in bars:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width() / 2, height + 0.2, f"{height:.1f}", ha='center', fontsize=8)
    st.pyplot(fig1)

    fig2, ax2 = plt.subplots(figsize=(4, 3))
    ax2.pie(non_zero_breakdown.values(), labels=non_zero_breakdown.keys(), autopct='%1.1f%%', startangle=140,
            textprops={'fontsize': 7}, colors=plt.cm.Paired.colors)
    ax2.axis('equal')
    st.pyplot(fig2)

def suggest_ways(breakdown, total_emission):
    ideal_limit = 70
    if total_emission > ideal_limit:
        st.error(f" Total emissions ({total_emission:.2f} kg CO₂) exceed ideal {ideal_limit} kg/day.")
    top_activities = sorted(breakdown.items(), key=lambda x: x[1], reverse=True)[:2]
    for activity, emission in top_activities:
        if emission == 0:
            continue
        st.write(f"**{activity.title()}**: Consider reducing this activity.")

def rank_emissions(breakdown):
    st.subheader(" Emission Ranking")
    sorted_activities = sorted(breakdown.items(), key=lambda x: x[1], reverse=True)
    for activity, emission in sorted_activities:
        st.write(f"**{activity.title()}**: {emission:.2f} kg CO₂")

def generate_pdf_report(total_emission, breakdown):
    html_content = "<h2>Daily Emission Report</h2>"
    html_content += f"<p><strong>Total Emission:</strong> {total_emission:.2f} kg CO₂</p>"
    html_content += "<ul>"
    for k, v in breakdown.items():
        html_content += f"<li>{k.title()}: {v:.2f} kg CO₂</li>"
    html_content += "</ul>"
    pdf_bytes = pdfkit.from_string(html_content, False)
    return BytesIO(pdf_bytes)

def main():
    st.title("Carbon Emission Tracker")

    theme_choice = st.selectbox("Select Theme", ["Light", "Dark"])
    st.session_state.theme = theme_choice

    inputs = {}
    cols = st.columns(3)
    for i, (activity, factor) in enumerate(EMISSION_FACTORS.items()):
        with cols[i % 3]:
            qty = st.number_input(f"{activity.title()} ({factor} kg CO₂/unit)", min_value=0.0, step=0.1, key=f"{activity}_input")
            inputs[activity] = qty

    if st.button("Calculate Emissions"):
        total_emission, breakdown = calculate_emissions(inputs)
        st.metric("Total Emissions", f"{total_emission:.2f} kg CO₂")
        st.session_state.latest_breakdown = breakdown
        st.session_state.latest_total = total_emission
        plot_carbon(breakdown)
        suggest_ways(breakdown, total_emission)
        rank_emissions(breakdown)

        if st.button("Export PDF Report"):
            pdf = generate_pdf_report(total_emission, breakdown)
            st.download_button(" Download PDF Report", data=pdf, file_name="emission_report.pdf")

    if st.session_state.show_login:
        st.subheader("Login / Sign Up")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        if st.button("Submit"):
            uid = f"user:{email}"
            st.session_state.user_id = uid
            st.session_state.show_login = False

if __name__ == "__main__":
    main()
