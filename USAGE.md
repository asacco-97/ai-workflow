# Usage

## Skills vs. subagents

**Skills** (`/skill-name`) are triggered inline in the main conversation. They read the current context and produce output directly in the chat. Use skills when you want Claude to do something and see the result immediately — run an evaluation, write a model card, design a config.

**Subagents** are named agents that Claude spawns to handle a bounded, research-heavy, or parallel task. They run in their own context and report back. Use subagents when you want a focused expert to investigate something without polluting the main conversation — auditing data, reviewing a diff, scouting literature.

**Rule of thumb:** If you want a result in the conversation, use a skill. If you want independent research or review, use a subagent.

---

## Workflow sequence

### Phase 1 — Plan the project

Before writing any code, get a concrete plan with verifiable checkpoints.

**Skills:**
- `/research-to-plan` — converts a fuzzy objective into an actionable implementation plan

**Subagents:**
- `project-planner` — scopes work, defines milestones, surfaces open questions
- `modeling-architect` — recommends modeling framework (Bayesian vs. frequentist, model family, hierarchy)
- `data-auditor` — flags leakage risk, PII, and quality problems before feature engineering
- `validation-reviewer` — sanity-checks the proposed CV scheme and metrics

**Example prompts:**
```
/research-to-plan I need to predict 30-day customer churn using transaction history and support tickets.

Spawn project-planner. Objective: predict monthly revenue per product line. We have 3 years of weekly sales data. Identify milestones and surface blockers.

Spawn modeling-architect. Should we use a hierarchical Bayesian model or gradient boosting for this churn problem? Give me tradeoffs.
```

---

### Phase 2 — Stress-test the plan

Challenge the plan before committing to an approach.

**Skills:**
- `/grill-me-with-docs` — adversarial review of a plan or design doc; finds hidden assumptions and weak points
- `/ds-model-evaluator` — evaluates the proposed model for leakage, validation, framework fit, and feasibility

**Example prompts:**
```
/grill-me-with-docs docs/plans/churn-model-plan.md

/ds-model-evaluator Here is our proposed approach: [paste plan]. What are the biggest risks?
```

---

### Phase 3 — Define the data contract

Lock down what the input data is expected to look like before writing feature engineering code.

**Skills:**
- `/data-contract` — produces a formal schema with types, constraints, nullability, and SLAs

**Subagents:**
- `data-auditor` — inspects the actual data loading code to validate the contract
- `security-privacy-reviewer` — checks for PII, raw row-level data, or sensitive fields that should not be used

**Example prompts:**
```
/data-contract Define a data contract for the features table at data/processed/features.parquet.

Spawn data-auditor. Check scripts/build_features.py for leakage risk and missing-value patterns.

Spawn security-privacy-reviewer. Review data/raw/customers.csv and the feature pipeline for PII exposure.
```

---

### Phase 4 — Build data sourcing and transformations

Write and validate the pipeline that gets data from source to model-ready.

**Subagents:**
- `data-auditor` — verify the output of each transformation step
- `debugger` — diagnose failures in pipeline scripts or data loading
- `code-reviewer` — review transformation code for correctness and maintainability

**Example prompts:**
```
Spawn data-auditor. The pipeline ran. Check scripts/transform.py and the output at data/processed/ for quality issues.

Spawn debugger. scripts/build_features.py raises KeyError on 'customer_tenure'. Here is the traceback: [paste].

Spawn code-reviewer. Review the diff for scripts/transform.py.
```

---

### Phase 5 — POC notebook

Build a proof-of-concept model, track it in MLflow, and evaluate it.

**Skills:**
- `/mlflow-experiment` — sets up experiment tracking, logs parameters and metrics
- `/ds-model-evaluator` — evaluates the model for leakage, validation gaps, and framework correctness

**Subagents:**
- `experiment-runner` — executes the training script end-to-end and returns a structured summary
- `validation-reviewer` — checks that the CV scheme, metrics, and reported performance are trustworthy

**Example prompts:**
```
/mlflow-experiment Set up MLflow tracking for notebooks/churn_poc.ipynb. Log AUROC, log-loss, and feature importance.

Spawn experiment-runner. Run scripts/train_poc.py and return a structured summary of outputs and MLflow metrics.

/ds-model-evaluator The POC notebook is at notebooks/churn_poc.ipynb. Check for leakage and validate the CV scheme.

Spawn validation-reviewer. Review the train/test split and CV strategy in notebooks/churn_poc.ipynb.
```

---

### Phase 6 — Convert notebook to framework code

Refactor the notebook into production-ready scripts with config-driven parameters.

**Skills:**
- `/notebook-to-pipeline` — converts a notebook into a reproducible pipeline script
- `/yaml-config-designer` — designs a YAML config schema for the pipeline

**Subagents:**
- `mlflow-engineer` — adds proper MLflow logging, model registry, and stage transitions
- `notebook-refactorer` — cleans up dead cells, extracts reusable modules, standardizes imports

**Example prompts:**
```
/notebook-to-pipeline Convert notebooks/churn_poc.ipynb into a pipeline script at scripts/train_churn.py.

/yaml-config-designer Design a YAML config for scripts/train_churn.py covering model hyperparameters, data paths, and MLflow settings.

Spawn mlflow-engineer. Add model registry logging and stage transition to scripts/train_churn.py.
```

---

### Phase 7 — Build the validation framework

Formalize how the model will be evaluated before it can ship.

**Skills:**
- `/validation-framework` — defines a validation strategy with metrics, thresholds, and pass/fail criteria

**Subagents:**
- `validation-reviewer` — audits the framework for leakage, metric appropriateness, and trustworthiness
- `code-reviewer` — reviews the validation code for correctness

**Example prompts:**
```
/validation-framework Build a validation framework for the churn model. Thresholds: AUROC > 0.78, precision@10% > 0.45.

Spawn validation-reviewer. Review scripts/validate_churn.py. Is the holdout isolated? Are metrics appropriate for class imbalance?
```

---

### Phase 8 — Suggest next experiments

Capture what to try next before context is lost.

**Skills:**
- `/experiment-backlog` — maintains a structured backlog of experiments with hypothesis, expected outcome, and status

**Subagents:**
- `literature-scout` — finds relevant papers or prior art for a modeling decision
- `modeling-architect` — recommends what to change and why based on current results

**Example prompts:**
```
/experiment-backlog Add: try calibrated probabilities with isotonic regression. Hypothesis: improves log-loss by 5-10%. Priority: high.

Spawn literature-scout. Find relevant literature on hierarchical Bayesian models for customer churn with sparse data.

Spawn modeling-architect. POC AUROC is 0.74. We're seeing high variance across folds. What should we try next?
```

---

### Phase 9 — Summarize for stakeholders

Produce a model card before sharing results.

**Skills:**
- `/model-card` — generates a model card covering intended use, performance, limitations, and risks

**Example prompts:**
```
/model-card Generate a model card for the churn model. MLflow run ID: abc123. Target audience: product team.
```

---

### Phase 10 — Pre-PR review

Review everything before opening a pull request or handing off.

**Skills:**
- `/review-own-branch` — reviews all changes on the current branch

**Subagents:**
- `code-reviewer` — focused review of modeling code for correctness and statistical validity
- `security-privacy-reviewer` — final check for secrets, PII, and unsafe data patterns

**Example prompts:**
```
/review-own-branch

Spawn code-reviewer. Review the diff for the churn model branch. Focus on modeling correctness and potential leakage.

Spawn security-privacy-reviewer. Final check before PR: scan all changed files for secrets, PII, or raw data that should not be committed.
```

---

## Memory discipline

Memory files (`memory/`, `docs/`, `reports/`) persist durable knowledge across sessions. Write to them deliberately.

**Preserve:**
- Key architectural decisions and why they were made (`memory/decisions/`)
- Failed approaches and why they failed (`memory/failed-approaches/`)
- Modeling assumptions and their sources (`memory/decisions/`)
- Validation decisions (metric choices, threshold rationale, split design) (`docs/validation/`)

**Do not preserve:**
- Secrets, tokens, API keys, or passwords
- Confidential row-level data or PII
- Ephemeral task state that is only relevant to the current session
- Output that duplicates what git history already captures

If you are unsure whether something belongs in memory, ask: "Would a new collaborator joining this project find this useful, and is it safe to store?" If yes to both, write it. If no to either, skip it.
