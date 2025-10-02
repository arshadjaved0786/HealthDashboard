import pandas as pd
import numpy as np

# Number of records
n = 100

# Seed for reproducibility
np.random.seed(42)

# Generate random data
names = [f"Person_{i+1}" for i in range(n)]
ages = np.random.randint(18, 60, n)
genders = np.random.choice(['M', 'F'], n)
sleep_hours = np.random.randint(4, 10, n)
activity_levels = np.random.choice(['Low', 'Medium', 'High'], n)
bmi = np.round(np.random.uniform(15, 35, n), 1)
temperatures = np.round(np.random.normal(36.8, 0.7, n), 1)
heart_rate = np.random.randint(60, 101, n)  # Heart rate (bpm)
blood_pressure = [f"{np.random.randint(90, 141)}/{np.random.randint(60, 91)}" for _ in range(n)]  # BP

# Function to categorize temperature
def categorize_temp(temp):
    if temp < 36.0:
        return "Low"
    elif 36.0 <= temp <= 37.5:
        return "Normal"
    else:
        return "High"

categories = [categorize_temp(t) for t in temperatures]

# Create DataFrame
df = pd.DataFrame({
    'Name': names,
    'Age': ages,
    'Gender': genders,
    'SleepHours': sleep_hours,
    'ActivityLevel': activity_levels,
    'BMI': bmi,
    'Temperature': temperatures,
    'HeartRate': heart_rate,
    'BloodPressure': blood_pressure,
    'Category': categories
})

# Save to CSV
df.to_csv("health_dataset.csv", index=False)
print("✅ 'health_dataset.csv' updated with HeartRate and BloodPressure")
