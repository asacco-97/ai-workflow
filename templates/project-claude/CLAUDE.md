# CLAUDE.md

## Project purpose

<!-- TODO: 2-3 sentences. What does this project build, what problem does it solve,
     and who are the primary users or stakeholders? -->

## Decision support

<!-- TODO: What decision does this project support?
     E.g., "This model supports the marketing team's decision on which customers to
     target for the Q3 retention campaign. The output is a weekly scored file." -->

## Stakeholders

<!-- TODO: Who needs what from this project, and on what cadence?
     E.g., "Marketing analyst: weekly predictions file by Monday 8am.
            Data science lead: model evaluation report before any promotion." -->

---

## Build and test

<!-- TODO: Fill in actual commands for this project. -->

```bash
# Install
pip install -e ".[dev]"

# Test
pytest tests/

# Lint
ruff check src/ tests/

# Train (replace with actual entry point)
python src/train.py --config configs/default.yaml
```

---

## Standard workflow

Follow this sequence for any non-trivial modeling task:

1. Plan with `/research-to-plan` or spawn `project-planner` before writing code.
2. Audit data with `data-auditor` before feature engineering.
3. Define a data contract with `/data-contract` before writing the pipeline.
4. Track every experiment with `/mlflow-experiment`.
5. Evaluate with `/ds-model-evaluator` after any major modeling change.
6. Validate with `/validation-framework` before considering a model shippable.
7. Review with `/review-own-branch` + `security-privacy-reviewer` before any PR.

---

## Skill and subagent map

| Stage | Use |
|---|---|
| Scoping / planning | `/research-to-plan` · `project-planner` |
| Data audit | `data-auditor` · `/data-quality-audit` |
| Data contract | `/data-contract` |
| Experiment tracking | `/experiment-backlog` |
| Architecture decision | `modeling-architect` |
| MLflow setup / fix | `/mlflow-experiment` · `mlflow-engineer` |
| Config schema | `/yaml-config-designer` |
| Model evaluation | `/ds-model-evaluator` |
| Validation design | `validation-reviewer` · `/validation-framework` |
| Bayesian diagnostics | `bayesian-reviewer` |
| Notebook refactor | `notebook-refactorer` · `/notebook-to-pipeline` |
| PR review | `/review-own-branch` · `code-reviewer` |
| Security review | `security-privacy-reviewer` |
| Literature / prior art | `literature-scout` |
| Debugging | `debugger` |
| Model card | `/model-card` |

---

## Rules

### Planning first

Do not write model code until the objective is stated as a testable hypothesis and the data sources are confirmed. Use `/research-to-plan` or `project-planner` to produce a plan with explicit "done when" criteria before any implementation begins.

### Data contract

Define a data contract with `/data-contract` before building features. The contract specifies column names, types, nullability, and valid ranges. No downstream code should make assumptions about schema that are not in the contract.

### Validation first

Define the evaluation strategy — metric, CV scheme, holdout split — before training. Do not tune metrics after seeing results on the holdout set. Use `validation-reviewer` to check the scheme before committing to it.

### Notebooks

- Notebooks are for exploration and POC only. Production logic goes in scripts.
- Every notebook that informs a decision must be committed with outputs cleared.
- Use `/notebook-to-pipeline` when moving from POC to production.

### MLflow and config

- Every training run is logged to MLflow. No silent runs.
- Hyperparameters live in a YAML config file, not hardcoded in scripts.
- Use `/yaml-config-designer` to scaffold the config schema.
- Use `mlflow-engineer` to add or fix logging.

### Memory protocol

After any session that makes a durable decision, write a brief note to the appropriate folder:

- `memory/decisions/` — what was decided and why
- `memory/failed-approaches/` — what was tried and why it didn't work
- `memory/workflows/` — repeatable procedures or runbooks
- `docs/validation/` — validation strategy and threshold rationale
- `docs/data-contracts/` — finalized data contracts
- `docs/experiments/` — experiment hypotheses and results

Do not write secrets, credentials, tokens, raw row-level data, or PII to any memory file.

### Security and privacy

- Run `security-privacy-reviewer` before every PR.
- Do not commit `.env` files, credential files, or config files containing secrets.
- Do not store raw data files in the repo. Store data paths and schemas instead.
- Do not log PII to MLflow artifacts or experiment notes.
