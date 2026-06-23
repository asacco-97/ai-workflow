---
name: review-own-branch
description: "Review the changes on the current git branch before opening a pull request: check for correctness, modeling soundness, config hygiene, test coverage, and MLflow integration completeness. Use when the user wants to self-review before requesting a code review, catch issues before a PR, or do a final quality pass on a modeling branch. Trigger when the user says 'review my branch', 'check my changes before PR', 'self-review', 'am I ready to open a PR', or 'what did I miss'."
---

# Review Own Branch

Do a structured self-review of the current branch's changes before opening a pull request. Catch issues now, when they are cheap to fix, rather than in a peer review or after merging.

---

## When to Use

- Before opening a PR on a modeling, pipeline, or data science branch
- After a sprint of exploratory work to find what should be cleaned up before merging
- When you want a second set of eyes but a colleague isn't available immediately

Do **not** use this skill as a substitute for peer review — it is a pre-flight check, not a replacement.

---

## Step 1: Get the Diff

Read the current branch's changes:

```bash
git diff main...HEAD --stat        # summary of changed files
git diff main...HEAD               # full diff
git log main...HEAD --oneline      # commit history on this branch
```

Ask the user to paste the output or run these commands if the shell is available. If the diff is large (>500 lines), ask the user which files or areas to prioritize.

---

## Step 2: Categorize Changes

Map each changed file to a category:

| Category | Examples |
|----------|---------|
| `data` | Loader, query, S3 path changes |
| `features` | Feature engineering functions |
| `model` | Training code, hyperparameters |
| `config` | YAML config files |
| `pipeline` | Orchestrator, CLI, scheduling |
| `tests` | Unit or integration tests |
| `mlflow` | Logging, registration, transitions |
| `docs` | Model card, validation plan, ADRs |
| `infra` | Dockerfile, requirements, CI config |
| `notebook` | POC notebooks (flag if in main src/) |

---

## Step 3: Run the Review Checklist

Work through each applicable section. Skip sections with no relevant changes.

---

### Correctness

- [ ] Feature engineering produces the same output as the notebook/prior version (verify with a unit test or spot check)
- [ ] Train/test split is correct for the data structure (time-based if time-ordered, group-based if panel data)
- [ ] No target leakage: features do not encode the target or use post-event information
- [ ] Preprocessing (scaling, encoding) is fit on training data only, not the full dataset
- [ ] No data is loaded inside feature engineering functions

---

### Config Hygiene

- [ ] No hardcoded paths, table names, or S3 URIs in `.py` files — they should come from config
- [ ] No secrets (passwords, API keys, connection strings) in YAML files or committed `.env` files
- [ ] Dev and prod configs are separate and the right one is used in each environment
- [ ] MLflow experiment name follows `{project}/{model-type}` convention

---

### MLflow Integration

- [ ] All changed hyperparameters are logged with `mlflow.log_param()`
- [ ] Primary metric is logged with `mlflow.log_metric()`
- [ ] Model artifact is saved with `mlflow.log_model()` or `mlflow.log_artifact()`
- [ ] Run status tag is set (`status: experimental` until review passes)
- [ ] If promoting: MLflow stage transition is in the PR or done separately with justification

---

### Test Coverage

- [ ] Any new or changed feature engineering function has at least one unit test
- [ ] Tests are not importing from notebooks (`from notebooks import ...` is a red flag)
- [ ] Tests do not depend on external data sources (mock or fixture data only)
- [ ] Existing tests still pass (run `pytest` if available)

---

### Data Science Soundness (for modeling changes)

- [ ] Baseline comparison is included or referenced — the new model beats something
- [ ] Validation metrics are on a held-out set, not the training set
- [ ] If Bayesian: R-hat < 1.01, zero divergences, ESS ≥ 400 are confirmed and logged
- [ ] If a new feature was added: its impact was measured in isolation before combining with others

---

### Documentation

- [ ] Commit messages describe *why* the change was made, not just what
- [ ] If a modeling decision was made: is it captured in `docs/experiment_backlog.md` or an ADR?
- [ ] If the model is being promoted: is a model card at `docs/model_card_*.md` up to date?
- [ ] If config structure changed: is `config/config.yaml` updated and consistent with the loader?

---

### Cleanup

- [ ] No dead code from abandoned experiments left in `.py` files
- [ ] No `print()` debug statements that should be logging calls
- [ ] No large binary files (model artifacts, data files) committed — these belong in S3 or MLflow artifacts
- [ ] No `.ipynb_checkpoints/` or `__pycache__/` directories committed

---

## Step 4: Produce the Review Report

Structure the output:

---

### Branch Review: `<branch-name>`

**Files changed:** N | **Commits:** N

#### Blockers
Issues that must be fixed before merging:
- [ ] `<file>:<line>` — `<issue>`

#### Warnings
Issues worth fixing but not blocking:
- [ ] `<file>` — `<issue>`

#### Passed
Checks that look good (brief list):
- Feature engineering unit tests present
- No hardcoded credentials
- MLflow run ID and metrics logged

#### Suggested PR description
_Draft a one-paragraph PR description based on the diff:_
> <what changed, why it was changed, how it was tested>

---

## Output Artifacts

| Artifact | Notes |
|----------|-------|
| Review report | This conversation — paste into PR description or ticket |
| No files written by default | If blockers are found, offer to fix them |

---

## Quality Gates

Before declaring the branch review complete:

- [ ] At least the Correctness and Config Hygiene sections were checked
- [ ] Every Blocker has a specific file and line reference, not just a category
- [ ] A PR description draft is provided

---

## Common Failure Modes

- **Only checking style** — a branch review that catches formatting but misses a train/test split bug is worse than no review (gives false confidence)
- **Blocking on trivial issues** — classify findings accurately; a missing docstring is not a Blocker
- **No PR description draft** — the PR description is part of the work; include it

---

## Example Invocation

```
/review-own-branch

I've been working on adding account age as a feature and retraining the churn model.
Branch is `feat/account-age-feature`. Ready to open a PR but want a quick check first.
```

Expected output: diff read, checklist run against the changed files, any blockers called out with file:line references, PR description draft.
