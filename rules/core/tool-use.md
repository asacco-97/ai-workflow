---
description: Which skill or subagent to invoke at each workflow stage.
---

# Tool use map

Use the right tool at the right stage. Do not substitute ad-hoc reasoning for a purpose-built skill.

| Stage | Tool |
|---|---|
| Problem scoping | `/research-to-plan` · `project-planner` |
| Data audit | `data-auditor` · `/data-quality-audit` |
| Data contract | `/data-contract` |
| Experiment planning | `/experiment-backlog` |
| Model architecture | `modeling-architect` |
| MLflow logging | `/mlflow-experiment` · `mlflow-engineer` |
| Config scaffolding | `/yaml-config-designer` |
| Model evaluation | `/ds-model-evaluator` |
| Validation review | `validation-reviewer` · `/validation-framework` |
| Bayesian diagnostics | `bayesian-reviewer` |
| Notebook refactor | `notebook-refactorer` · `/notebook-to-pipeline` |
| PR review | `/review-own-branch` · `code-reviewer` |
| Security review | `security-privacy-reviewer` |
| Literature / prior art | `literature-scout` |
| Debugging failures | `debugger` |
| Model card | `/model-card` |
| Domain modeling | `/domain-modeling` |
