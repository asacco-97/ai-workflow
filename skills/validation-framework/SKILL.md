---
name: validation-framework
description: "Design a validation strategy for a modeling problem: choose the right train/val/test split, cross-validation approach, metrics, and baseline comparisons before writing any model code. Use when the user is about to train a model and hasn't settled on a validation approach, when they're unsure whether k-fold or walk-forward CV is appropriate, or when they want to define evaluation metrics that align with the business problem. Trigger when the user says 'how should I validate this', 'what metrics should I use', 'is k-fold correct here', 'design my validation', or starts model training without a documented validation plan."
---

# Validation Framework

Design a rigorous, problem-appropriate validation strategy before model code is written. A validation framework is the spec for how you will know if your model works — and the most common place data science projects fail silently.

---

## When to Use

- At the start of a modeling project, before any training code
- When a model is showing unrealistically good or bad metrics
- When switching model types and the validation approach needs to change
- Before presenting model results to a stakeholder

Do **not** use this skill to design validation for a model already in production being evaluated live — that is a monitoring problem, not a validation design problem.

---

## Step 1: Gather Problem Context

Ask for any that are missing:

1. **Problem type** — classification (binary/multi-class), regression, forecasting, ranking, survival, clustering, or Bayesian estimation
2. **Data structure** — i.i.d., grouped (panel, accounts with multiple rows), or time-ordered?
3. **Business decision** — what action does the model output drive? This determines what metrics matter.
4. **Target distribution** — positive rate (classification) or target skew (regression)?

---

## Step 2: Choose the Split Strategy

| Data structure | Recommended split |
|----------------|-------------------|
| i.i.d., no time structure | Random stratified 70/15/15 |
| Panel data (same entity repeated) | Group-based — all rows for an entity in one split only |
| Time-ordered | Chronological — most recent N% as test, never shuffle |
| Time-ordered + grouped | Time-blocked group split |

**For time-based splits, specify the boundary as a date, not a ratio:**

```
Train:      all data before 2024-01-01
Validation: 2024-01-01 – 2024-06-30
Test:       2024-07-01 – present  (held out until final evaluation only)
```

Never split time-series data on a ratio alone.

---

## Step 3: Choose the Cross-Validation Strategy

CV is for model selection and hyperparameter tuning on the train+val portion only. The test set is never touched during CV.

| Problem type | CV strategy |
|-------------|-------------|
| i.i.d. | 5-fold stratified (classification) or standard 5-fold (regression) |
| Panel / grouped | Group k-fold — all rows for an entity stay in one fold |
| Time-ordered | Walk-forward (expanding window) |
| Time-ordered + constrained data | Rolling window (fixed-size train window) |

**Walk-forward CV:**
```
Fold 1: train [t0, t1), validate [t1, t2)
Fold 2: train [t0, t2), validate [t2, t3)
Fold 3: train [t0, t3), validate [t3, t4)
```

**Never use shuffled k-fold on time-series data.** It allows future data to appear in training folds.

---

## Step 4: Select Primary and Secondary Metrics

Specify exactly one **primary metric** (the decision metric) and up to three **secondary metrics** (for characterization).

### Classification

| Scenario | Primary metric | Why |
|----------|---------------|-----|
| Missing positives costly (churn, fraud) | Recall @ fixed threshold | Missing a true positive has higher cost than a false alarm |
| False alarms costly (outbound sales) | Precision @ fixed threshold | Don't waste effort on non-churners |
| Threshold unclear | AUC-PR | Threshold-free ranking quality |
| Severe imbalance (>10:1) | AUC-PR (not AUC-ROC) | ROC is misleading at high imbalance |

Do not use accuracy as a primary metric for imbalanced classification.

### Regression / Forecasting

| Scenario | Primary metric |
|----------|---------------|
| Symmetric errors | RMSE (penalizes large errors) or MAE (robust to outliers) |
| Percentage-based KPI | MAPE or SMAPE |
| Revenue-weighted | Weighted MAE |
| Forecast by horizon | Metric per forecast horizon, not aggregate |

### Bayesian Models

Primary metrics are posterior diagnostics, not prediction metrics:
- R-hat < 1.01 (convergence)
- Bulk ESS and Tail ESS ≥ 400 per parameter
- Divergences = 0 after tuning
- PPC coverage — posterior predictive intervals contain observed data

---

## Step 5: Define Baselines

A model that cannot beat a naive baseline is not adding value. Define at least one baseline before training.

| Problem type | Naive baseline |
|-------------|----------------|
| Binary classification | Predict majority class; or threshold-based rule on a single feature |
| Regression | Predict mean of training target |
| Forecasting | Last-value carry-forward; or seasonal naive (same period last year) |
| Ranking | Random ranking |

If the model cannot beat the baseline on the primary metric, stop and investigate the data or target definition before iterating on the model.

---

## Step 6: Produce the Validation Plan

Output a concise plan. Offer to write to `docs/validation_plan.md` if the user wants it saved.

```markdown
## Validation Plan: <model-name>

**Problem type:** <classification | regression | ...>
**Data structure:** <i.i.d. | panel | time-ordered>

### Train / Val / Test Split
- Strategy: <random stratified | group-based | chronological>
- Train: <date range or %>
- Validation: <date range or %>
- Test: <held until final eval — do not touch during development>

### Cross-Validation (on Train+Val only)
- Strategy: <5-fold stratified | group k-fold | walk-forward>
- N folds: <N>
- Note: <caveats>

### Metrics
- **Primary**: <metric> — <why it maps to the business decision>
- Secondary: <metric>, <metric>
- Not used: <metric> — <reason>

### Baselines
1. <name>: <description> — target primary metric ≥ <threshold>

### Quality Gate
Model is ready for staging when:
- Primary metric on held-out test ≥ <threshold>
- Beats all baselines on primary metric
- Leakage confirmed absent (via /ds-model-evaluator)
```

---

## Output Artifacts

| Artifact | Suggested Path |
|----------|---------------|
| Validation plan | `docs/validation_plan.md` |
| CV code stub | Inline in this conversation |

---

## Quality Gates

Before delivering the framework:

- [ ] Split strategy is appropriate for the data structure
- [ ] Primary metric is one named metric aligned to the business decision
- [ ] At least one naive baseline is defined
- [ ] Test set is chronologically last (if time-ordered) and never touched during CV
- [ ] Leakage risks for this specific split are called out

---

## Common Failure Modes

- **Shuffled k-fold on time-series** — the most common mistake; allows future data into training folds
- **AUC-ROC on severe imbalance** — inflates at high imbalance; use AUC-PR instead
- **No baseline** — without a baseline you cannot know if the model adds value
- **Aggregate forecast metric hiding per-horizon decay** — a single RMSE masks degradation at longer horizons
- **Preprocessing outside the CV loop** — fitting a scaler before running CV contaminates validation folds

---

## Example Invocation

```
/validation-framework

Binary classification: predict which accounts will churn in the next 30 days.
Data: one row per account per week, 3 years of history, ~2% churn rate.
Output feeds the CS team — they can act on about 50 accounts per week.
```

Expected output: time-based split with explicit date boundary, walk-forward CV, AUC-PR as primary metric, precision@50 as secondary, last-value baseline.
