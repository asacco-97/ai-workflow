"""
Sales forecast pipeline - weekly store-level revenue prediction.
Training data: 3 years of weekly POS data across 50 stores.
Target: next_week_revenue
"""

import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, cross_val_score
import numpy as np

df = pd.read_csv("data/weekly_store_sales.csv")

# Feature engineering
df["rolling_4wk_avg"] = df.groupby("store_id")["revenue"].transform(
    lambda x: x.rolling(4).mean()
)
df["rolling_4wk_std"] = df.groupby("store_id")["revenue"].transform(
    lambda x: x.rolling(4).std()
)
df["month"] = pd.to_datetime(df["week_start"]).dt.month
df["quarter"] = pd.to_datetime(df["week_start"]).dt.quarter
df["year_revenue_avg"] = df.groupby(["store_id", "year"])["revenue"].transform("mean")

# Drop rows with NaN from rolling
df = df.dropna()

features = [
    "store_id", "month", "quarter", "promo_flag", "holiday_flag",
    "rolling_4wk_avg", "rolling_4wk_std", "year_revenue_avg",
    "store_size_sqft", "region_code"
]
target = "next_week_revenue"

X = df[features]
y = df[target]

# Scale
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Split
X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y, test_size=0.2, random_state=42
)

# Train
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Evaluate
cv_scores = cross_val_score(model, X_scaled, y, cv=5, scoring="r2")
print(f"CV R² scores: {cv_scores}")
print(f"Mean CV R²: {cv_scores.mean():.3f}")
print(f"Test R²: {model.score(X_test, y_test):.3f}")
