import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import joblib

# ------------------------
# Step 1: Load / Create Data
# ------------------------
n = 100
np.random.seed(42)

names = [f"Person_{i+1}" for i in range(n)]
ages = np.random.randint(18, 60, n)
genders = np.random.choice(['M', 'F'], n)

# Generate realistic BP depending on age and gender
systolic = []
diastolic = []

for age, gender in zip(ages, genders):
    base_sys = 110
    base_dia = 70
    
    # Age effect
    age_sys = base_sys + (age - 18) * 0.5      # systolic increases with age
    age_dia = base_dia + (age - 18) * 0.2      # slight increase
    
    # Gender effect
    if gender == 'M':
        age_sys += 5
        age_dia += 2
    
    # Random small variation
    sys = np.random.randint(int(age_sys)-5, int(age_sys)+6)
    dia = np.random.randint(int(age_dia)-5, int(age_dia)+6)
    
    # Clip to normal human range
    sys = np.clip(sys, 90, 180)
    dia = np.clip(dia, 60, 120)
    
    systolic.append(sys)
    diastolic.append(dia)

# Target: temperature category ("Low", "Normal", "High") for classification
# Randomly assigning categories for this example
temp_categories = ["Low", "Normal", "High"]
target = np.random.choice(temp_categories, n)

# Create DataFrame
df = pd.DataFrame({
    'Name': names,
    'Age': ages,
    'Gender': genders,
    'Systolic': systolic,
    'Diastolic': diastolic,
    'Target': target
})

# ------------------------
# Step 2: Preprocessing
# ------------------------
# Encode Gender
df['Gender'] = df['Gender'].map({'M': 0, 'F': 1})

# Drop Name column
df = df.drop(['Name'], axis=1)

# ------------------------
# Step 3: Train/Test Split
# ------------------------
X = df.drop('Target', axis=1)  # Features: Age, Gender, Systolic, Diastolic
y = df['Target']               # Target: Low / Normal / High
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# ------------------------
# Step 4: Model Training
# ------------------------
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# ------------------------
# Step 5: Evaluate & Save
# ------------------------
accuracy = model.score(X_test, y_test)
print(f"Model Accuracy: {accuracy:.2f}")

# Save the trained model
joblib.dump(model, 'health_model.pkl')
print("Model saved as 'health_model.pkl'")
