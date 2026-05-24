"""
GCTU WiFi Security Framework - Synthetic Data Generator
Generates realistic campus WiFi traffic with anomalies
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os

# Configuration
np.random.seed(42)
random.seed(42)


def generate_wifi_data(days=7, devices=500, access_points=20):
    """
    Generate synthetic WiFi network data

    Parameters:
    - days: number of days to generate
    - devices: number of unique client devices
    - access_points: number of APs on campus

    Returns:
    - DataFrame with WiFi traffic records
    """

    # Define AP locations
    ap_locations = {
        f"AP_{i:02d}": random.choice([
            "Library", "Lecture_Hall", "Admin_Block",
            "Hostel_A", "Hostel_B", "Cafeteria", "Lab"
        ]) for i in range(1, access_points + 1)
    }

    records = []
    total_records = days * 24 * 12  # 12 records per hour (every 5 min)

    print(f"Generating {total_records} records for {days} days...")

    for day in range(days):
        current_date = datetime(2025, 5, 23, 0, 0, 0) + timedelta(days=day)

        for hour in range(24):
            for minute in [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55]:
                timestamp = current_date + timedelta(hours=hour, minutes=minute)

                # Determine activity level based on time
                if 8 <= hour <= 17:  # Class hours
                    active_ratio = 0.8
                    data_multiplier = 2.0
                elif 18 <= hour <= 22:  # Evening
                    active_ratio = 0.6
                    data_multiplier = 1.5
                else:  # Night
                    active_ratio = 0.2
                    data_multiplier = 0.5

                # Number of active devices this interval
                n_active = int(devices * active_ratio)
                active_devices = random.sample(range(1, devices + 1), n_active)

                for device_id in active_devices:
                    # Select AP (with location bias)
                    ap_id = f"AP_{random.randint(1, access_points):02d}"
                    ap_loc = ap_locations[ap_id]

                    # Time-based location bias
                    if 12 <= hour <= 14:  # Lunch time -> Cafeteria bias
                        if random.random() < 0.4:
                            ap_id = "AP_05"  # Cafeteria AP

                    # Base metrics
                    signal_strength = np.random.randint(-75, -35)
                    data_up = np.random.exponential(50) * data_multiplier
                    data_down = np.random.exponential(200) * data_multiplier
                    duration = np.random.exponential(300)  # seconds

                    # Determine if this is an anomaly (5% probability)
                    is_anomaly = False
                    anomaly_type = "Normal"

                    if random.random() < 0.05:
                        is_anomaly = True
                        anomaly_choice = random.choice(["bruteforce", "rogue_ap", "scanning", "dos"])

                        if anomaly_choice == "bruteforce":
                            anomaly_type = "BruteForce"
                            signal_strength = -85
                            duration = 5
                            data_up = 10
                            data_down = 10

                        elif anomaly_choice == "rogue_ap":
                            anomaly_type = "RogueAP"
                            ap_id = f"Rogue_{random.randint(1, 5):02d}"
                            signal_strength = -65

                        elif anomaly_choice == "scanning":
                            anomaly_type = "PortScan"
                            data_up = data_up * 0.1
                            data_down = data_down * 0.1
                            duration = 60

                        elif anomaly_choice == "dos":
                            anomaly_type = "DDoS"
                            data_up = data_up * 50
                            data_down = data_down * 50
                            duration = 10

                    records.append({
                        'timestamp': timestamp,
                        'device_id': f"DEV_{device_id:04d}",
                        'ap_id': ap_id,
                        'ap_location': ap_loc,
                        'signal_rssi': signal_strength,
                        'data_up_mb': round(data_up, 2),
                        'data_down_mb': round(data_down, 2),
                        'duration_sec': round(duration, 2),
                        'anomaly_type': anomaly_type,
                        'is_anomaly': 1 if is_anomaly else 0
                    })

    df = pd.DataFrame(records)
    print(f"Generated {len(df)} records")
    print(f"Anomalies: {df['is_anomaly'].sum()} ({100 * df['is_anomaly'].mean():.1f}%)")

    return df


def save_data(df, filename="gctu_wifi_data.csv"):
    """Save dataframe to CSV"""
    os.makedirs("data/synthetic", exist_ok=True)
    filepath = f"data/synthetic/{filename}"
    df.to_csv(filepath, index=False)
    print(f"Saved to {filepath}")
    return filepath


if __name__ == "__main__":
    # Generate data
    print("=" * 50)
    print("GCTU WiFi Security Framework - Data Generator")
    print("=" * 50)

    df = generate_wifi_data(days=3, devices=200, access_points=15)
    save_data(df)

    # Display sample
    print("\nSample data:")
    print(df.head(10))
    print("\nColumn names:", df.columns.tolist())