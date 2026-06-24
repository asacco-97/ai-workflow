---
description: Do not write model or pipeline code until the objective is confirmed.
---

# Planning first

Do not write model code, pipeline code, or feature engineering until:

- The modeling objective is stated as a measurable, testable hypothesis (e.g., "Predict 30-day churn with AUC ≥ 0.80 on held-out Q3 data").
- The target variable is unambiguously defined and its source is confirmed.
- The data sources are identified and at least one sample has been inspected.
- Success criteria are written down — not just "improve performance."

Use `/research-to-plan` or spawn `project-planner` to produce a scoped plan before any implementation. If the user jumps straight to code, ask for the objective and success criteria first.
