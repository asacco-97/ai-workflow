# Churn Model Plan — Customer Success Team

## Goal
Predict which customers will churn in the next 30 days so we can target them with retention outreach.

## Data
- CRM export: ~12,000 customers, 18 months of monthly snapshots
- Features we're thinking about:
  - Days since last login
  - Number of support tickets (last 90 days)
  - Plan tier (basic/pro/enterprise)
  - MRR
  - Contract type (month-to-month vs annual)
  - NPS score (collected at signup)
  - Usage metrics: API calls/month, active seats, features used
  - Account age
  - Assigned CSM (200+ unique values)

## Approach
- Label: churned = 1 if customer cancelled in the observation period, else 0
- Model: XGBoost classifier
- Split: 80/20 train/test, stratified by churn label
- Eval metric: AUC-ROC
- Class balance: ~8% churn rate in the dataset

## Open questions
- Should we include customers who churned during the feature window to build their features?
- NPS was only collected for ~40% of customers — plan to impute with the mean.
