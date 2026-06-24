---
description: Standard modeling workflow sequence. Follow this order for every non-trivial task.
---

# Standard workflow

For any non-trivial modeling task, follow this order. Do not skip steps.

1. **Plan** — state the objective as a testable hypothesis with "done when" criteria before writing code.
2. **Audit data** — profile the dataset for quality issues, nulls, duplicates, and distributional anomalies before feature engineering.
3. **Define the contract** — specify column names, types, nullability, and valid ranges before building the pipeline.
4. **Design the experiment** — record the hypothesis, metric, and expected direction in the experiment backlog before training.
5. **Define validation** — choose the CV scheme, metric, and holdout policy before any model is fit.
6. **Train and log** — log all parameters, metrics, and artifacts to MLflow. No silent runs.
7. **Evaluate** — run `/ds-model-evaluator` after any significant modeling change.
8. **Review** — run `/review-own-branch` and `security-privacy-reviewer` before any PR.
