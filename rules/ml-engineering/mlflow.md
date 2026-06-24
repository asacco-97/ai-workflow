---
description: Every training run must be logged to MLflow.
---

# MLflow

- Every training run is logged. No silent runs.
- Log at minimum: all hyperparameters, primary metric per fold/epoch, final evaluation metrics, model artifact, and the config file used.
- Use a consistent experiment name per project: `<project>/<model-family>` (e.g., `churn/bayesian-logistic`).
- Tag each run with: `model_type`, `dataset_version`, `split_strategy`, `git_sha`.
- Use `/mlflow-experiment` to scaffold logging or `mlflow-engineer` to fix broken logging.

Do not log PII, raw data rows, or credentials to MLflow. Artifact names must not contain usernames, emails, or account IDs.
