import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from scipy.stats import ttest_ind

# ------------------------
# 0. Load Data
# ------------------------
customers = pd.read_csv('data/customers.csv')
transactions = pd.read_csv('data/transactions.csv')
sessions = pd.read_csv('data/sessions.csv')
campaigns = pd.read_csv('data/campaigns.csv')

# Convert date columns
customers['signup_date'] = pd.to_datetime(customers['signup_date'])
transactions['transaction_date'] = pd.to_datetime(transactions['transaction_date'])
sessions['session_date'] = pd.to_datetime(sessions['session_date'])

print("✅ Data loaded successfully")
print(customers.head())

# ------------------------
# 1. Customer Lifetime Value (LTV)
# ------------------------
ltv = transactions.groupby('customer_id')['amount'].sum().reset_index()
ltv.columns = ['customer_id', 'lifetime_value']
print("\n🔹 Top 5 LTV customers:")
print(ltv.sort_values(by='lifetime_value', ascending=False).head())

# Plot LTV histogram
plt.figure(figsize=(8, 5))
ltv['lifetime_value'].hist(bins=30)
plt.title("Customer Lifetime Value Distribution")
plt.xlabel("LTV")
plt.ylabel("Number of Customers")
plt.tight_layout()
plt.grid(False)
plt.show()
print("✅ LTV chart displayed\n")

# ------------------------
# 2. Repeat Purchase Rate
# ------------------------
txn_counts = transactions.groupby('customer_id').size().reset_index(name='txn_count')
repeat_rate = len(txn_counts[txn_counts['txn_count'] > 1]) / len(txn_counts)
print(f"🔹 Repeat Purchase Rate: {repeat_rate:.2%}\n")

# ------------------------
# 3. Revenue by Country
# ------------------------
merged = transactions.merge(customers, on='customer_id')
country_revenue = merged.groupby('country')['amount'].sum().reset_index()
print("🔹 Revenue by Country:")
print(country_revenue.sort_values(by='amount', ascending=False), "\n")

# ------------------------
# 4. Revenue by Acquisition Channel
# ------------------------
channel_revenue = merged.groupby('acquisition_channel')['amount'].sum().reset_index()
print("🔹 Revenue by Acquisition Channel:")
print(channel_revenue.sort_values(by='amount', ascending=False), "\n")

# ------------------------
# 5. Cohort Analysis
# ------------------------
transactions = transactions.merge(customers[['customer_id', 'signup_date']], on='customer_id')
transactions['cohort_month'] = transactions['signup_date'].dt.to_period('M')
transactions['active_month'] = transactions['transaction_date'].dt.to_period('M')

cohort = transactions.groupby(['cohort_month', 'active_month'])['customer_id'].nunique().reset_index()
cohort_pivot = cohort.pivot(index='cohort_month', columns='active_month', values='customer_id').fillna(0)

# Plot cohort heatmap
plt.figure(figsize=(10, 6))
sns.heatmap(cohort_pivot, cmap="YlGnBu", annot=True, fmt=".0f")
plt.title("Cohort Analysis: Monthly Active Users")
plt.tight_layout()
plt.show()
print("✅ Cohort heatmap displayed\n")

# ------------------------
# 6. A/B Test Simulation
# ------------------------
customers['test_group'] = customers['customer_id'].apply(lambda x: 'A' if x % 2 == 0 else 'B')
ab_merged = transactions.merge(customers[['customer_id', 'test_group']], on='customer_id')

group_revenue = ab_merged.groupby('test_group')['amount'].mean()
print("🔹 Average Revenue per Test Group:")
print(group_revenue, "\n")

# Perform T-test
group_a = ab_merged[ab_merged['test_group'] == 'A']['amount']
group_b = ab_merged[ab_merged['test_group'] == 'B']['amount']
t_stat, p_val = ttest_ind(group_a, group_b, equal_var=False)
print(f"🔹 T-Test Results: t-stat = {t_stat:.3f}, p-value = {p_val:.4f}\n")

# ------------------------
# 7. Churn Check (Last transaction > 30 days ago)
# ------------------------
latest_txn = transactions.groupby('customer_id')['transaction_date'].max().reset_index()
latest_txn['days_since_txn'] = (datetime(2025, 5, 20) - latest_txn['transaction_date']).dt.days
latest_txn['churned'] = latest_txn['days_since_txn'] > 30

churn_rate = latest_txn['churned'].mean()
print(f"🔹 Estimated Churn Rate (>30 days inactive): {churn_rate:.2%}\n")

# ------------------------
# Done
# ------------------------
print("✅ All analysis completed successfully!")

# ------------------------
# Export results to CSV for GitHub
# ------------------------

# Create output folder (optional: add a folder to keep things clean)
import os
if not os.path.exists('outputs'):
    os.makedirs('outputs')

ltv.to_csv('outputs/ltv_customers.csv', index=False)
country_revenue.to_csv('outputs/revenue_by_country.csv', index=False)
channel_revenue.to_csv('outputs/revenue_by_channel.csv', index=False)
cohort_pivot.to_csv('outputs/cohort_matrix.csv')
group_revenue.to_csv('outputs/ab_group_revenue.csv')
latest_txn.to_csv('outputs/churn_flagged_customers.csv', index=False)

print("✅ All result files saved to /outputs folder.")





