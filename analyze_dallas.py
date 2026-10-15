import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# 1. Load dataset
df = pd.read_excel('dallas_trucking_companies.xlsx')

# 2. Clean numeric columns
df['Trucks_Clean'] = pd.to_numeric(df['Trucks'], errors='coerce')
df['Drivers_Clean'] = pd.to_numeric(df['Drivers'], errors='coerce')

# 3. Compute Summary Statistics
max_trucks_company = df.loc[df['Trucks_Clean'].idxmax()]
min_trucks_company = df.loc[df['Trucks_Clean'].idxmin()]

max_drivers_company = df.loc[df['Drivers_Clean'].idxmax()]

print('=== DALLAS TRUCKING FLEET ANALYSIS ===')
print(
    f"Total Companies Analyzed: {len(df.dropna(subset=['Trucks_Clean']))}\n"
)

print('--- Trucks Statistics ---')
print(
    f"Largest Fleet: {max_trucks_company['Company Name']} ({int(max_trucks_company['Trucks_Clean'])} Trucks)"
)
print(
    f"Smallest Fleet: {min_trucks_company['Company Name']} ({int(min_trucks_company['Trucks_Clean'])} Truck)"
)
print(f"Average Trucks per Company: {df['Trucks_Clean'].mean():.2f}")
print(f"Median Trucks: {df['Trucks_Clean'].median():.2f}\n")

print('--- Drivers Statistics ---')
print(
    f"Most Drivers: {max_drivers_company['Company Name']} ({int(max_drivers_company['Drivers_Clean'])} Drivers)"
)
print(f"Average Drivers per Company: {df['Drivers_Clean'].mean():.2f}")
print(f"Median Drivers: {df['Drivers_Clean'].median():.2f}\n")

# 4. Generate Top 10 Fleets Chart
top10_trucks = df.nlargest(10, 'Trucks_Clean')

plt.figure(figsize=(12, 6))
sns.barplot(
    data=top10_trucks, y='Company Name', x='Trucks_Clean', palette='viridis'
)
plt.title('Top 10 Trucking Companies in Dallas by Fleet Size (Trucks)')
plt.xlabel('Number of Trucks')
plt.ylabel('Company Name')
plt.tight_layout()

# Save chart
plt.savefig('dallas_fleet_analysis.png')
plt.close()

print('Chart saved successfully as dallas_fleet_analysis.png 🟢')