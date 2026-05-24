import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import joblib
import os

# Load data
df = pd.read_csv('synthetic_data/gctu_wifi_data.csv')
print(f"Loaded {len(df)} records")

# Select features
features = ['signal_rssi', 'data_up_mb', 'data_down_mb', 'duration_sec']
X = df[features].copy()

# Handle missing values
X = X.fillna(X.median())

# Scale features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Train model
model = IsolationForest(
    n_estimators=100,
    contamination=0.1,
    random_state=42
)

model.fit(X_scaled)

# Save model and scaler
os.makedirs('models', exist_ok=True)
joblib.dump(model, 'models/isolation_forest.pkl')
joblib.dump(scaler, 'models/scaler.pkl')

print("Model and scaler saved successfully!")

# Test on same data
predictions = model.predict(X_scaled)
anomaly_count = sum(predictions == -1)
print(f"Detected {anomaly_count} anomalies ({100*anomaly_count/len(df):.1f}%)")