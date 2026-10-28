import pandas as pd
import numpy as np

print("Starting Continuous Audit Engine...")

# 1. Load the dirty dataset
df = pd.read_csv("2017_audit_dataset_dirty.csv")
df['Transaction Date'] = pd.to_datetime(df['Transaction Date'])

# Ensure amount is a float (handling any leftover formatting)
if df['Transaction Amount'].dtype == 'O':
    df['Transaction Amount'] = df['Transaction Amount'].replace(r'[\$, ]', '', regex=True).replace(r'^\((.*)\)$', r'-\1', regex=True).astype(float)

# TEST 1: WEEKEND TRANSACTIONS
print("Running Test 1: Weekend Transaction Analysis...")
# dayofweek returns 0-4 for Mon-Fri, 5 for Sat, 6 for Sun
df['Flag_Weekend'] = df['Transaction Date'].dt.dayofweek.isin([5, 6])


# TEST 2: SPLIT TRANSACTIONS (Threshold Evasion)
print("Running Test 2: Split Transaction Detection...")
# Sort chronologically by employee and merchant
df = df.sort_values(by=['Cardholder Name', 'Merchant Name', 'Transaction Date'])

# Calculate the days between transactions for the same employee at the same merchant
df['Prev_Tx_Date'] = df.groupby(['Cardholder Name', 'Merchant Name'])['Transaction Date'].shift(1)
df['Days_Since_Last_Tx'] = (df['Transaction Date'] - df['Prev_Tx_Date']).dt.days

# Flag if a transaction occurs within 2 days of another at the same merchant
# We flag both the current row and the previous row using shift(-1)
is_split_forward = df['Days_Since_Last_Tx'] <= 2
is_split_backward = df.groupby(['Cardholder Name', 'Merchant Name'])['Days_Since_Last_Tx'].shift(-1) <= 2

df['Flag_Split'] = is_split_forward | is_split_backward


# TEST 3: BENFORD'S LAW ANOMALIES
print("Running Test 3: Benford's Law Distribution...")
# Extract the first non-zero digit of the transaction amount
df['First_Digit'] = df['Transaction Amount'].astype(str).str.extract(r'([1-9])').astype(float)

# Calculate actual distribution vs expected Benford distribution
actual_dist = df['First_Digit'].value_counts(normalize=True).sort_index()
expected_dist = pd.Series({d: np.log10(1 + 1/d) for d in range(1, 10)})

# Find digits where actual frequency exceeds expected by more than 3%
suspicious_digits = []
for digit in range(1, 10):
    actual = actual_dist.get(digit, 0)
    expected = expected_dist.get(digit, 0)
    if actual > expected + 0.03: # 3% variance threshold
        suspicious_digits.append(digit)
        print(f"   -> ALARM: Digit {digit} frequency ({actual:.1%}) exceeds Benford expectation ({expected:.1%})")

# Flag transactions starting with the suspicious digits
df['Flag_Benford'] = df['First_Digit'].isin(suspicious_digits)


# EXPORT EXCEPTIONS FOR AUDIT REVIEW
print("Consolidating Exception Report...")
# Filter for rows that triggered ANY of the audit flags
exceptions_df = df[df['Flag_Weekend'] | df['Flag_Split'] | df['Flag_Benford']].copy()

# Clean up temporary calculation columns
exceptions_df = exceptions_df.drop(columns=['Prev_Tx_Date', 'Days_Since_Last_Tx', 'First_Digit'])

# Reorder columns to put the flags at the front for the auditors
cols = ['Flag_Weekend', 'Flag_Split', 'Flag_Benford', 'Cardholder Name', 'Transaction Date', 'Transaction Amount', 'Merchant Name', 'Department']
# Add any remaining original columns
cols += [c for c in exceptions_df.columns if c not in cols]
exceptions_df = exceptions_df[cols]

exceptions_df.to_csv("Audit_Exceptions_Report.csv", index=False)

print(f"Audit Complete! {len(exceptions_df)} high-risk transactions flagged.")
print("Exceptions saved to 'Audit_Exceptions_Report.csv'.")