---
name: yaml-config-designer
description: "Design a well-structured YAML configuration file for a modeling pipeline, training job, or data workflow. Use when the user wants to: externalize hardcoded values from a script into config, design a config schema for a new pipeline, add environment overrides (dev/staging/prod), or make a model's hyperparameters and paths configurable without code changes. Trigger when the user says 'make this configurable', 'create a config file', 'I want YAML config for this', 'externalize the parameters', or shows a script with hardcoded paths or hyperparameters."
---

# YAML Config Designer

Design a clean, environment-aware YAML configuration file that externalizes a script's constants without overcomplicating the structure.

---

## When to Use

- Script has hardcoded paths, hyperparameters, or environment-specific values
- A pipeline needs to run in dev/staging/prod with different settings
- Multiple team members need to tune parameters without touching source code
- The model is moving from POC to production and configs should be version-controlled

Do **not** create a config file for a one-off analysis script that will never run again.

---

## Step 1: Extract Configuration Candidates

Ask the user to share the script (or paste the relevant constants). Scan for:

- **Paths**: file paths, S3 URIs, table names, output directories
- **Data config**: date ranges, feature lists, train/test split ratios, target column
- **Model hyperparameters**: learning rates, tree depth, n_estimators, prior scales, number of MCMC chains
- **Runtime settings**: random seeds, verbosity, number of workers, timeout
- **Environment-specific values**: credentials, endpoints, AWS region, cluster settings

Group them into sections before drafting. Constants that never change across environments (e.g., column names fixed by the data contract) should stay in code.

---

## Step 2: Draft the Config

Generate a `config/config.yaml` (base config) plus environment override files.

### Base config structure

```yaml
# config/config.yaml
# Base configuration — all environments inherit from this.
# Override specific keys in config/config.<env>.yaml

project:
  name: "<project-slug>"
  version: "1.0"

data:
  source:
    type: <redshift | s3 | local>
    location: "<table-name or s3://bucket/prefix>"
  target_col: "<column-name>"
  date_range:
    start: "2023-01-01"
    end: null               # null = use latest available
  features:
    include: []             # empty = use all non-target columns
    exclude: []

split:
  strategy: <random | time_based | group>
  test_size: 0.2
  val_size: 0.1
  random_seed: 42
  time_col: null            # required if strategy: time_based
  group_col: null           # required if strategy: group

model:
  type: "<xgboost | logistic_regression | bayesian_hierarchical | arima>"
  params: {}                # model-specific hyperparameters

training:
  random_seed: 42
  n_jobs: -1

output:
  model_dir: "models/"
  predictions_dir: "outputs/predictions/"
  reports_dir: "reports/"

mlflow:
  experiment_name: "<project-slug>/<model-type>"
  tracking_uri: null        # null = local ./mlruns
```

### Environment override files

Only include keys that differ from base. Keep override files small.

```yaml
# config/config.dev.yaml
data:
  source:
    location: "dev_schema.account_events"
  date_range:
    start: "2024-01-01"   # smaller window for fast iteration

mlflow:
  tracking_uri: null       # local tracking in dev
```

```yaml
# config/config.prod.yaml
data:
  source:
    location: "prod_schema.account_events"

mlflow:
  tracking_uri: "http://mlflow-server:5000"
```

---

## Step 3: Config Loader

Generate a minimal Python loader that merges base + environment override.

```python
# src/config.py
import os
import yaml
from pathlib import Path

_CONFIG_DIR = Path(__file__).parent.parent / "config"

def load_config(env: str | None = None) -> dict:
    env = env or os.getenv("ENV", "dev")
    base = _load_yaml(_CONFIG_DIR / "config.yaml")
    override_path = _CONFIG_DIR / f"config.{env}.yaml"
    if override_path.exists():
        base = _deep_merge(base, _load_yaml(override_path))
    return base

def _load_yaml(path: Path) -> dict:
    with open(path) as f:
        return yaml.safe_load(f) or {}

def _deep_merge(base: dict, override: dict) -> dict:
    result = base.copy()
    for key, val in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(val, dict):
            result[key] = _deep_merge(result[key], val)
        else:
            result[key] = val
    return result

# Usage: cfg = load_config()  or  load_config("prod")
```

---

## Step 4: Annotate the Design

Note:

- **What was kept in code** (not config) and why — fixed constants do not need to be configurable
- **Which keys the user should confirm** — anything inferred from context, not stated explicitly
- **Secrets policy** — credentials and API keys must not be in YAML files. Reference environment variables instead: `location: "${REDSHIFT_HOST}"` and document them in `.env.example`

---

## Output Artifacts

| Artifact | Suggested Path |
|----------|---------------|
| Base config | `config/config.yaml` |
| Dev override | `config/config.dev.yaml` |
| Prod override | `config/config.prod.yaml` |
| Config loader | `src/config.py` |

Write files if the user confirms the structure.

---

## Quality Gates

Before finalizing:

- [ ] Paths are in override files, not the base config
- [ ] Secrets are referenced as env vars, not hardcoded
- [ ] Random seeds are in config (reproducibility)
- [ ] MLflow experiment name follows `{project}/{model-type}` convention
- [ ] All inferred values annotated with `# TODO: confirm`

---

## Common Failure Modes

- **Over-configuring** — putting logic (not values) in YAML. Config holds *values*, code holds *behavior*.
- **Flat config without sections** — 30 top-level keys is hard to navigate. Group into `data`, `model`, `output`, `mlflow`.
- **Secrets in YAML** — credentials in version-controlled YAML files are a security incident waiting to happen.
- **No environment override pattern** — a single config for all environments forces manual edits before every run.

---

## Example Invocation

```
/yaml-config-designer

This script has hardcoded Redshift table names and XGBoost hyperparameters.
I want to run it in dev (small date window, local MLflow) and prod (full data,
remote MLflow at http://mlflow.internal:5000). Here's the script: [paste]
```

Expected output: `config/config.yaml`, `config/config.dev.yaml`, `config/config.prod.yaml`, `src/config.py`.
