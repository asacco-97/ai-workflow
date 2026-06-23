---
name: model-card
description: "Generate a stakeholder-facing model card documenting a model's intended use, training data, evaluation metrics, limitations, and caveats. Use when the user wants to: communicate a model's design to non-technical stakeholders, document a model before handing it off or promoting to production, satisfy an internal governance or review requirement, or create a reference that survives the original author leaving the project. Trigger when the user says 'write a model card', 'document this model', 'what should we tell stakeholders about this model', 'model report', or is about to promote a model to production."
---

# Model Card

Produce a concise, honest model card that communicates what a model does, how it was built, where it works, and where it does not. Model cards are for humans — stakeholders, reviewers, and future maintainers — not for ML practitioners who can read the code.

---

## When to Use

- Before promoting a model to production
- When presenting model results to a business stakeholder or executive
- When handing off a model to another team or engineer
- As a governance artifact for internal model review

Do **not** write a model card for POC or experimental models that haven't passed a `/ds-model-evaluator` review. A model card implies production-readiness.

---

## Step 1: Gather Input

Ask the user for any of these that aren't available from context:

1. **Model name and version**
2. **MLflow experiment name and winning run ID** (to pull metrics from)
3. **Problem type and target** — what is the model predicting?
4. **Training data** — source, date range, grain, size
5. **Primary and secondary metrics** — with values from the final evaluation
6. **Known limitations** — what the model does not work well on
7. **Intended use** — how will predictions be used, by whom, and how often?
8. **Out-of-scope use** — how should this model NOT be used?

If the user has a `/validation-framework` plan or `/ds-model-evaluator` review in context, pull facts from there rather than re-asking.

---

## Step 2: Generate the Model Card

Write to `docs/model_card_<model-name>_v<version>.md`.

```markdown
# Model Card: <Model Name> v<version>

**Date:** YYYY-MM-DD
**Author:** <name>
**Status:** Staging | Production
**MLflow experiment:** <experiment-name>
**MLflow run ID:** <run-id>

---

## Intended Use

**Primary use:** <1-2 sentences describing the decision this model supports and who uses it>
e.g., "Weekly batch scoring of accounts to surface the top 50 at-risk accounts for the Customer Success team's outreach queue."

**Users:** <who receives or acts on model output>

**Out-of-scope use:** <what this model should NOT be used for>
e.g., "Do not use to score individual transactions in real-time — the model was trained on weekly account-level aggregates and will produce unreliable output on event-level data."

---

## Model Description

**Model type:** <XGBoost classifier | Bayesian hierarchical | ARIMA | ...>
**Problem type:** <binary classification | regression | forecasting | ...>
**Prediction target:** <what the model predicts, in plain English>
**Output:** <probability score / numeric value / category — and what it means>
**Prediction cadence:** <real-time | daily batch | weekly batch>

---

## Training Data

| Property | Value |
|----------|-------|
| Source | <Redshift table / S3 path / ...> |
| Grain | <what one row represents> |
| Date range | YYYY-MM-DD – YYYY-MM-DD |
| Training rows | N |
| Positive rate | <% for classification> |
| Features | N features (<list key ones>) |

**Known data limitations:**
- <e.g., "Accounts created in the last 30 days have sparse features and are excluded from scoring.">
- <e.g., "Revenue data is missing for ~8% of accounts and imputed with 0.">

---

## Evaluation

**Validation approach:** <time-based split | group k-fold | ...>
**Test set:** <date range or description — held out, never used during development>

| Metric | Value | Baseline |
|--------|-------|---------|
| <Primary metric> | <value> | <baseline value> |
| <Secondary metric> | <value> | — |
| <Secondary metric> | <value> | — |

**Performance by segment** *(if evaluated — list key cuts)*:

| Segment | Primary Metric |
|---------|---------------|
| <e.g., Enterprise accounts> | <value> |
| <e.g., Accounts < 90 days old> | <value> |

---

## Limitations and Caveats

- **<Limitation 1>:** <plain-English description of what the model does not handle well>
- **<Limitation 2>:** <...>
- **Distribution shift:** The model was trained on data through <date>. Performance may degrade if account behavior, product features, or the definition of churn changes after that date.

---

## Fairness and Bias Considerations

*(Complete if the model makes decisions that affect individuals or regulated groups.)*

- Protected attributes excluded from features: <yes/no — list if yes>
- Disparate impact analysis: <done / not applicable / pending>
- Notes: <any relevant observations>

---

## Model Governance

| Checkpoint | Status | Date |
|------------|--------|------|
| `/ds-model-evaluator` review | Pass / Fail | YYYY-MM-DD |
| Bayesian diagnostics (if applicable) | Pass / Fail | YYYY-MM-DD |
| Stakeholder sign-off | <name> | YYYY-MM-DD |
| MLflow stage | Staging / Production | YYYY-MM-DD |

---

## Monitoring and Refresh

- **Input drift monitoring:** <in place / pending / not applicable>
- **Prediction drift monitoring:** <in place / pending / not applicable>
- **Scheduled retraining:** <cadence or trigger>
- **Owner:** <name or team responsible for monitoring and refresh>

---

## Contact

| Role | Name / Channel |
|------|---------------|
| Model owner | <name> |
| Data owner | <name or team> |
| Questions / issues | <Slack channel or email> |
```

---

## Output Artifacts

| Artifact | Suggested Path |
|----------|---------------|
| Model card | `docs/model_card_<model-name>_v<version>.md` |

Also log the model card as an MLflow artifact on the production run:

```python
mlflow.log_artifact("docs/model_card_<model-name>_v<version>.md", artifact_path="review/")
```

---

## Quality Gates

Before delivering the model card:

- [ ] Intended use is written in plain English — no ML jargon
- [ ] Out-of-scope use is explicitly stated
- [ ] Primary metric is reported with a baseline comparison
- [ ] At least two limitations are documented (if none exist, the author hasn't looked hard enough)
- [ ] Distribution shift risk is acknowledged with a training data cutoff date
- [ ] Owner and refresh plan are named

---

## Common Failure Modes

- **Overpromising** — model cards that only list strengths and hide limitations erode stakeholder trust when the model fails in a predictable way. Be honest about where it doesn't work.
- **Jargon without translation** — "AUC-PR of 0.63" means nothing to a CS manager. Add a plain-English interpretation: "The model correctly identifies about 70% of accounts that will churn in the next 30 days."
- **No out-of-scope use** — without this section, stakeholders will use the model for things it wasn't designed for.
- **Missing owner** — a model card with no named owner is an orphan. Someone must be responsible for monitoring and refresh.

---

## Example Invocation

```
/model-card

Model: churn-predictor v1.2
MLflow run: abc123
Problem: binary churn classification, weekly batch scoring
Primary metric: AUC-PR 0.64 (baseline: 0.51)
Training data: account_events table, 2022-01-01 – 2024-06-30, 120k accounts
Limitations: poor performance on accounts < 90 days old, no signal for enterprise tier
```

Expected output: complete model card written to `docs/model_card_churn-predictor_v1.2.md`.
