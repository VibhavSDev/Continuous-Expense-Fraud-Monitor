import pandas as pd
import numpy as np
from datetime import timedelta

print("Loading original dataset...")
# 1. Load the data
df = pd.read_csv("2017.csv/2017.csv")

# 2. Clean the data types for manipulation
# Remove the '$' and spaces, convert to float
df['Transaction Amount'] = (
    df['Transaction Amount']
    .replace(r'[\$, ]', '', regex=True)          # Remove $, commas, and spaces
    .replace(r'^\((.*)\)$', r'-\1', regex=True)  # Convert (123.45) to -123.45
    .astype(float)
)
df['Transaction Date'] = pd.to_datetime(df['Transaction Date'])

new_fraud_rows = []

print("Injecting Weekend Anomalies...")
# ANOMALY 1: WEEKEND TRANSACTIONS
# Pick 250 random transactions and force them to fall on a weekend
weekend_idx = np.random.choice(df.index, size=250, replace=False)

def shift_to_weekend(date):
    # weekday() returns 0-4 for Mon-Fri, 5 for Sat, 6 for Sun
    while date.weekday() < 5:  
        date += timedelta(days=1)
    return date

df.loc[weekend_idx, 'Transaction Date'] = df.loc[weekend_idx, 'Transaction Date'].apply(shift_to_weekend)


print("Injecting Split Transactions (Threshold Evasion)...")
# ANOMALY 2: SPLIT TRANSACTIONS
# Simulate 50 instances where a user splits a large purchase to avoid a $1,000 approval limit
for _ in range(50):
    # Grab a random existing transaction to copy the employee and merchant details
    base_row = df.sample(1).iloc[0].copy()
    
    # Create Part 1 of the split (e.g., $745.50)
    row1 = base_row.copy()
    row1['Transaction Amount'] = round(np.random.uniform(500, 950), 2)
    
    # Create Part 2 of the split (e.g., $610.25)
    row2 = base_row.copy()
    row2['Transaction Amount'] = round(np.random.uniform(500, 950), 2)
    row2['Transaction Date'] = row1['Transaction Date'] + timedelta(days=int(np.random.choice([0, 1]))) # Same day or next day
    
    new_fraud_rows.extend([row1, row2])


print("Injecting Benford's Law Anomalies...")
# ANOMALY 3: BENFORD'S LAW MANIPULATION
# Inject 1,500 transactions starting with 8 or 9 (e.g., $850.00, $999.99)
# This will heavily skew the natural Benford curve for Tableau visualization
for _ in range(1500):
    fraud_row = df.sample(1).iloc[0].copy()
    # Generate an amount starting with 8 or 9
    fraud_row['Transaction Amount'] = round(np.random.uniform(800.00, 999.99), 2)
    new_fraud_rows.append(fraud_row)

# Combine the original data with our new fraudulent rows
dirty_df = pd.concat([df, pd.DataFrame(new_fraud_rows)], ignore_index=True)

# Sort chronologically so the injected data blends in seamlessly
dirty_df = dirty_df.sort_values(by='Transaction Date').reset_index(drop=True)

# Export the new "dirty" dataset
output_filename = "2017_audit_dataset_dirty.csv"
dirty_df.to_csv(output_filename, index=False)

print(f"Success! Dirty dataset saved as '{output_filename}'.")
print(f"Total rows increased from {len(df)} to {len(dirty_df)}.")