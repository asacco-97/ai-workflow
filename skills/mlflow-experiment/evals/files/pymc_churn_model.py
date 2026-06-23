"""
Bayesian hierarchical churn model for PE portfolio companies.
Predicts 12-month churn probability at the company level.
No MLflow logging yet — needs to be added.
"""
import pymc as pm
import arviz as az
import numpy as np
import pandas as pd

# Data: 42 portfolio companies, 24 months of history
# company_idx: integer index 0..41
# churned: 0/1 per company per month
# n_at_risk: companies at risk each month

np.random.seed(42)
n_companies = 42
n_months = 24

company_idx = np.repeat(np.arange(n_companies), n_months)
months = np.tile(np.arange(n_months), n_companies)
churned = np.random.binomial(1, 0.08, size=n_companies * n_months)
n_at_risk = np.ones(n_companies * n_months, dtype=int)

with pm.Model() as churn_model:
    # Hyperpriors
    mu_alpha = pm.Normal("mu_alpha", mu=-2.5, sigma=1.0)
    sigma_alpha = pm.HalfNormal("sigma_alpha", sigma=0.5)

    # Company-level random intercepts (partial pooling)
    alpha_company = pm.Normal("alpha_company", mu=mu_alpha, sigma=sigma_alpha, shape=n_companies)

    # Monthly trend
    beta_time = pm.Normal("beta_time", mu=0, sigma=0.1)

    # Likelihood
    p = pm.math.sigmoid(alpha_company[company_idx] + beta_time * months)
    obs = pm.Bernoulli("obs", p=p, observed=churned)

    # Sample
    trace = pm.sample(
        draws=1000,
        tune=1000,
        chains=4,
        target_accept=0.9,
        random_seed=42,
        progressbar=False,
    )

    # Posterior predictive
    ppc = pm.sample_posterior_predictive(trace, progressbar=False)

az.concat([trace, ppc], inplace=True)

print("Sampling complete.")
print(az.summary(trace, var_names=["mu_alpha", "sigma_alpha", "beta_time"]))
