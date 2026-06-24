---
description: Gates required before promoting a model to Staging or Production.
---

# Model registry

Before promoting a model to **Staging:**
- Validation strategy is documented in `docs/validation/`.
- All evaluation metrics meet the defined threshold.
- The model artifact is registered in MLflow with a run that has a `git_sha` tag.
- No unresolved leakage warnings from `validation-reviewer`.

Before promoting to **Production:**
- Staging performance has been confirmed on a recent data slice (not only the original holdout).
- A model card exists at `reports/model-cards/`.
- `security-privacy-reviewer` has been run and no blockers remain.
- A rollback plan is documented.

Use `mlflow-engineer` to set stage transitions. Never promote directly from an ad-hoc notebook run.
