import matplotlib.pyplot as plt
from carbon_database import log_emission,get_user_emissions
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
    categories = list(breakdown.keys())
    emissions = list(breakdown.values())
    plt.figure(figsize=(10, 6))
    plt.bar(categories, emissions, color="red")
    plt.title("Carbon Emission per Activity")
    plt.ylabel("CO2 Emission (kg)")
    plt.xlabel("Activity")
    for i, val in enumerate(emissions):
        plt.text(i, val + 0.5, f"{val:.1f}", ha='center')
    plt.tight_layout()
    plt.show()
    plt.figure(figsize=(8, 8))
    plt.pie(emissions, labels=categories, autopct='%1.1f%%', startangle=140)
    plt.title('Carbon Emission Share by Activity')
    plt.axis('equal')
    plt.tight_layout()
    plt.show()
def comparions(user_id,week1_dates,week2_dates):
    data=get_user_emissions(user_id)
    week1_total=sum(data[d]['total_emission'] for d in data if d in week1_dates)
    week2_total=sum(data[d]['total_emission'] for d in data if d in week2_dates)
    plt.bar(['Week 1','Week 2','Week 3','Week 4'],[week1_total,week2_total],color=['yellow','orange'])
    plt.title('Weekly carbon emission compariosn')
    plt.ylabel('Co2 emission per kg')
    plt.xlabel('Week')
    plt.show()

def main():
    user_data = {
        'electricity': 100,
        'petrol': 50,
        'diesel': 0,
        'natural_gas': 15,
        'organic_waste': 10,
        'paper': 5,
        'plastic': 2
    }
    try:
        total_emission, breakdown = calculate_emissions(user_data)
        print('Total carbon emission:', total_emission, 'kg CO2')
        print('Emission breakdown:', breakdown)
        plot_carbon(breakdown)
    except ValueError as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
