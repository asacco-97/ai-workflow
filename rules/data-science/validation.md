---
description: Define the evaluation strategy before any model is trained.
---

# Validation

Before training any model:

1. State the primary metric and the threshold that defines success.
2. Choose the CV scheme (k-fold, time-series split, group k-fold, etc.) and justify it.
3. Identify the holdout set and commit to never tuning on it.
4. Run `validation-reviewer` to check the scheme for leakage, appropriate metric choice, and correct split logic.

After training:
- Report confidence intervals or standard deviations across folds, not just the mean.
- If performance looks surprisingly good, investigate leakage before celebrating.
- Do not adjust the metric or threshold after seeing holdout results.

Validation strategy goes in `docs/validation/`. One document per experiment or model version.
