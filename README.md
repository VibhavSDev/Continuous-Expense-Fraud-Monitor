# Continuous Expense Fraud Monitor (Audit Analytics Pipeline)

An automated data pipeline and visualization suite designed to detect fraudulent corporate expenditures, policy violations, and threshold evasion in Travel & Expense (T&E) data. This project mimics the functionality of enterprise audit software (like CaseWare IDEA) using Python, Pandas, and Tableau.

## 🏗️ Architecture & Workflow
1. **Data Ingestion & Simulation**: Processes a 48,000+ row dataset of real municipal procurement data, simulating real-world anomalies.
2. **Audit Analytics Engine (Python)**: Analyzes transactions programmatically to detect statistical anomalies without manual sampling.
3. **Automated Reporting (OpenPyXL)**: Compiles flagged exceptions into a production-ready, highly formatted Advanced Excel checklist for manual field auditor review.
4. **Executive Dashboard (Tableau)**: Visualizes fraud risk distribution across departments and mathematical deviations from expected statistical models.

## 🔍 Core Audit Tests Implemented
* **Benford’s Law Distribution**: Identifies artificial manipulation of transaction amounts by comparing first-digit frequencies against logarithmic expectations, flagging deviations >3%.
* **Split Transactions (Threshold Evasion)**: Groups historical records by `Cardholder` and `Merchant` and calculates time deltas to flag consecutive purchases designed to bypass standard $1,000 approval limits.
* **Weekend/Holiday Abuse**: Evaluates `datetime` objects to isolate unapproved procurement activity outside of operating hours.

## 📊 Visualizations
*Interactive Tableau Dashboard includes:*
* **Dual-Axis Benford Curve**: Actual vs. Expected statistical distribution.
* **Department Risk Heatmap**: Concentration of policy violations by department and merchant category.
* **Evasion Scatter Plot**: Granular view of individual transactions clustering directly beneath the $1,000 threshold line.

## 🚀 Quick Start
```bash
pip install -r requirements.txt
python src/audit_engine.py
python src/generate_excel_report.py