---
description: Rules for preventing data leakage and invalid train/test splits.
---

# Leakage and splits

These checks must pass before any model is evaluated:

**Feature timing:**
- No feature can be computed using data from after the prediction timestamp.
- For rolling aggregates, confirm the window closes at or before the prediction point.
- For join-based features, confirm the join key does not encode the target.

**Split integrity:**
- For time-series data, split must be temporal — no shuffled k-fold.
- No preprocessing (scaling, encoding, imputation) that uses statistics from the full dataset before splitting. Fit transformers on train, apply to val/test.
- No entity overlap between train and test when the task is per-entity prediction (e.g., user churn).

**Target leakage:**
- The target must be computed independently of the features. If the target and a feature use the same source table, verify the time windows do not overlap.

If any check fails, stop. Leakage invalidates all reported results.
