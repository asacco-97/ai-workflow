# Bayesian Churn Model Plan

## Goal
Estimate the probability that a customer churns next month, with uncertainty quantified,
so the CS team can prioritize outreach with appropriate confidence.

## Data
- 6,000 B2B customers across 12 industry verticals
- Monthly snapshots, 24 months of history
- Features: MRR, seats, support tickets, login frequency, NPS score, industry, company size

## Proposed model
- Logistic regression in Stan
- One intercept per industry vertical (12 groups, ranging from 40 to 800 customers each)
- Priors: Normal(0, 10) on all coefficients including the group intercepts
- Likelihood: Bernoulli(logit(Xβ + α_industry))
- Fit with NUTS, 2000 samples, 4 chains
- Report posterior mean probability as the "churn score"

## Validation plan
- Hold out the final 2 months as test set
- Compare posterior mean churn score to actual churn using AUC-ROC
- If AUC > 0.75, ship it

## Open questions
- Should we include industry as a feature or as a grouping variable?
- Is there value in letting coefficients vary by industry?
