---
name: mlflow-experiment
description: "Set up, log, and manage MLflow experiments for data science and Bayesian models. Use this skill when the user wants to: scaffold a new MLflow experiment with naming conventions and artifact structure, generate logging boilerplate for params, metrics, and artifacts, log PyMC or ArviZ traces and MCMC diagnostics (R-hat, ESS, divergences) as MLflow artifacts and metrics, register a model in the MLflow Model Registry, transition a model between Staging and Production or Archived, or compare metrics and diagnostics across experiment runs. Invoke proactively when the user is building or evaluating a model that will go to production — tracking is almost always needed even when the user does not mention MLflow explicitly."
---

# MLflow Experiment

Help the user set up, log, and manage MLflow experiments with consistent conventions that make runs searchable and comparable over time.

## Step 1: Identify what's needed

Determine which mode applies — the user's message usually makes it clear. If the user is starting fresh, combine Scaffold and Log in the same response.

- **Scaffold**: starting a new project, no existing tracking, "set up MLflow", "create an experiment"
- **Log a run**: "add logging to this script", "how do I track my PyMC model", "what should I log"
- **Register/transition**: "register this model", "promote to production", "archive the old version"
- **Compare runs**: "compare these two runs", "which run performed better", "summarize my experiment"

Before generating code, confirm the experiment name and model type if not clear from context.

---

## Naming and tag conventions

Consistent naming is what makes MLflow useful at scale — one-off names mean you can't filter or query runs 3 months later.

**Experiment name**: `{project-slug}/{model-type}`
- `churn-prediction/bayesian-hierarchical`
- `deal-scoring/xgboost-baseline`
- `revenue-forecast/arima`

**Run tags** — categorical metadata shown in the UI filter sidebar:
```python
mlflow.set_tag("model_type", "bayesian_hierarchical")  # bayesian_hierarchical | xgboost | arima | linear
mlflow.set_tag("data_vintage", "2024-Q4")              # what data window the model was trained on
mlflow.set_tag("status", "experimental")               # experimental | validated | production-candidate
mlflow.set_tag("reviewer", "<your-name>")              # last human reviewer of this run
```

**Run params** — numeric/config values that vary across runs (queryable and plottable in MLflow UI):
```python
mlflow.log_param("n_chains", 4)
mlflow.log_param("n_draws", 2000)
mlflow.log_param("n_tune", 1000)
# Add any model-specific configs: prior_scale, n_features, target_name, etc.
```

The distinction matters: tags filter (categorical), params plot (numeric). Don't put strings in params or floats in tags.

---

## Mode A: Scaffold

Generate the experiment setup and recommend the artifact layout. Ask for the project name and model type if not provided.

```python
import mlflow

# Local tracking is the default (saves to ./mlruns in your working directory).
# For a remote server: mlflow.set_tracking_uri("http://your-server:5000")
# or set the env var: MLFLOW_TRACKING_URI=http://your-server:5000

EXPERIMENT_NAME = "{project-slug}/{model-type}"
mlflow.set_experiment(EXPERIMENT_NAME)
```

Recommend this artifact layout within each run — consistent structure means you know where to look:
```
artifacts/
├── model/         # pickled model object (for reproducibility and reloading)
├── traces/        # ArviZ InferenceData (.nc files)
├── plots/         # posterior plots, PPC, trace plots
├── data/          # summary tables, feature importance, predictions
└── review/        # model review notes, evaluator verdicts
```

---

## Mode B: Log a Run

Generate a complete logging wrapper. There are two templates — use the Bayesian extension whenever the model uses PyMC, Stan, NumPyro, or Bambi.

### Standard template

```python
import mlflow

with mlflow.start_run(run_name="{descriptive-run-name}") as run:
    # Tags
    mlflow.set_tag("model_type", "{model_type}")
    mlflow.set_tag("data_vintage", "{data_vintage}")
    mlflow.set_tag("status", "experimental")
    mlflow.set_tag("reviewer", "{your_name}")

    # Params
    mlflow.log_param("key_param", value)

    # --- your model training here ---

    # Metrics
    mlflow.log_metric("metric_name", value)

    # Artifacts
    mlflow.log_artifact("path/to/output_file", artifact_path="data/")

    print(f"Run ID: {run.info.run_id}")
```

### Bayesian extension (PyMC / ArviZ)

Add this block after sampling. The diagnostic metrics are the critical part — log them as MLflow metrics (not just into the trace) so you can sort and filter runs by convergence quality without opening netCDF files.

```python
import arviz as az

# MCMC config params
mlflow.log_param("n_chains", trace.posterior.dims["chain"])
mlflow.log_param("n_draws", trace.posterior.dims["draw"])
mlflow.log_param("n_tune", n_tune)

# Diagnostic metrics — non-negotiable for Bayesian runs
summary = az.summary(trace)
mlflow.log_metric("max_rhat", float(summary["r_hat"].max()))
mlflow.log_metric("min_bulk_ess", float(summary["ess_bulk"].min()))
mlflow.log_metric("min_tail_ess", float(summary["ess_tail"].min()))
mlflow.log_metric("n_divergences", int(trace.sample_stats["diverging"].sum()))

# Model comparison metrics (compute if comparing models)
# loo = az.loo(trace)
# mlflow.log_metric("elpd_loo", float(loo.elpd_loo))
# mlflow.log_metric("elpd_loo_se", float(loo.se))

# Log the PyMC model object — required for reloading the model structure and priors
import cloudpickle
model_path = "model.pkl"
with open(model_path, "wb") as f:
    cloudpickle.dump(model, f)  # replace `model` with your pm.Model() variable name
mlflow.log_artifact(model_path, artifact_path="model/")

# Log full trace as netCDF — required for downstream PPC and LOO.
# If you ran sample_posterior_predictive and used az.concat([trace, ppc], inplace=True),
# the combined InferenceData keeps them in separate named groups internally:
#   idata.posterior         — MCMC samples
#   idata.posterior_predictive — PPC samples
# All groups are preserved in the .nc file and accessible via az.from_netcdf("trace.nc").
trace_path = "trace.nc"
az.to_netcdf(trace, trace_path)
mlflow.log_artifact(trace_path, artifact_path="traces/")

# Log ArviZ summary table
summary_path = "summary.csv"
summary.to_csv(summary_path)
mlflow.log_artifact(summary_path, artifact_path="data/")

# Log trace plot
import matplotlib.pyplot as plt
az.plot_trace(trace)
plt.savefig("trace_plot.png", bbox_inches="tight", dpi=100)
plt.close()
mlflow.log_artifact("trace_plot.png", artifact_path="plots/")

# Log PPC plot (if prior/posterior predictive checks were run)
# az.plot_ppc(trace)
# plt.savefig("ppc.png", bbox_inches="tight", dpi=100)
# plt.close()
# mlflow.log_artifact("ppc.png", artifact_path="plots/")
```

After generating boilerplate, remind the user to keep `status: experimental` until the model passes a `ds-model-evaluator` or `bayesian-reviewer` review.

---

## Mode C: Register and Transition

Registration is for models that are ready to move toward deployment. It creates a versioned, named entry in the Model Registry — separate from the experiment run that produced it.

```python
import mlflow
from mlflow import MlflowClient

client = MlflowClient()
run_id = "{run-id}"         # from run.info.run_id or the MLflow UI
model_name = "{model-name}" # e.g., "churn-predictor", "deal-scorer"

# Register the model from the run
result = mlflow.register_model(f"runs:/{run_id}/model", model_name)
version = result.version
print(f"Registered: {model_name} v{version}")
```

**Stage transitions:**

```python
# → Staging: run is complete, diagnostics clean, ready for human review
client.transition_model_version_stage(
    name=model_name, version=version, stage="Staging",
    archive_existing_versions=False  # keep old Staging visible during review
)

# → Production: passed all reviews, stakeholders signed off
client.transition_model_version_stage(
    name=model_name, version=version, stage="Production",
    archive_existing_versions=True  # retire the previous Production version
)

# → Archived: keep for reproducibility, no longer active
client.transition_model_version_stage(
    name=model_name, version=old_version, stage="Archived"
)
```

**When to use each stage:**
- **Staging**: diagnostics pass (max_rhat < 1.01, zero divergences), ready for `ds-model-evaluator` four-pillar review. Update `status` tag to `validated` after review passes.
- **Production**: four-pillar review passed, business stakeholder sign-off done. Set `archive_existing_versions=True` to automatically retire the previous version.
- **Archived**: old versions you want to preserve for reproducibility (traces still accessible) but no longer serve predictions from.

---

## Mode D: Compare Runs

Pull run metrics and params programmatically, then render a side-by-side table with an interpretation. Always emit the `client.get_run()` retrieval code — even when the user pastes metric values directly, they will need this snippet for future comparisons and shouldn't have to look it up.

```python
from mlflow.tracking import MlflowClient
import pandas as pd

client = MlflowClient()
run_ids = ["{run-id-1}", "{run-id-2}"]

rows = []
for run_id in run_ids:
    run = client.get_run(run_id)
    rows.append({
        "run_id": run_id[:8],
        "run_name": run.data.tags.get("mlflow.runName", "—"),
        "status": run.data.tags.get("status", "—"),
        **run.data.metrics,
        **run.data.params,
    })

df = pd.DataFrame(rows).set_index("run_id")
print(df.to_markdown())
```

After printing the table, add a short interpretation paragraph covering:
1. Which run wins on the primary metric (specify which metric matters for this problem)
2. Convergence flags: any `max_rhat > 1.01`, `n_divergences > 0`, or low ESS
3. Whether config differences (n_draws, n_chains) explain metric differences
4. Recommended next step: promote the winner, re-sample with more draws, or investigate further

---

## Integration notes

- **Before registering**: run `/ds-model-evaluator` on the model script or design doc to catch leakage, split issues, and framework problems first. Promote to Staging only after it passes.
- **For Bayesian models**: run the `bayesian-reviewer` agent and log its verdict as a text artifact so the review is attached to the run: `mlflow.log_text(verdict_text, "review/bayesian_review.txt")`
- **After production**: set up input drift and prediction drift monitoring as a next step — model ownership means catching distribution shift before it silently degrades performance.
