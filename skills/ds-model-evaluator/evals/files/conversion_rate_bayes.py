"""
Hierarchical Bayesian model for store-level conversion rates.
Goal: estimate conversion rate per store (clicks -> purchases) to
guide budget allocation. 50 stores, observation counts vary from 8 to 2,400.
"""

import pymc as pm
import numpy as np
import pandas as pd

df = pd.read_csv("data/store_conversions.csv")
# columns: store_id, clicks, purchases

store_idx = df["store_id"].astype("category").cat.codes.values
n_stores = df["store_id"].nunique()
clicks = df["clicks"].values
purchases = df["purchases"].values

with pm.Model() as conversion_model:
    # Priors on conversion rates per store — treat each store independently
    p = pm.Uniform("p", lower=0, upper=1, shape=n_stores)

    # Likelihood
    obs = pm.Binomial("obs", n=clicks, p=p[store_idx], observed=purchases)

    # Inference
    trace = pm.sample(1000, tune=1000, target_accept=0.9, random_seed=42)

# Report results
import arviz as az
summary = az.summary(trace, var_names=["p"])
print(summary)
print(f"\nStores with widest CIs: {summary.nlargest(5, 'hdi_97%')}")
