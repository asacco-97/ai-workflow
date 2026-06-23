---
name: notebook-to-pipeline
description: "Convert a POC Jupyter notebook into a structured, production-ready Python pipeline with modular scripts, YAML config, MLflow logging, and input validation. Use when the user wants to: ship a notebook to production, refactor notebook code into reusable functions, separate data loading from feature engineering from model training, or make a notebook schedulable on AWS (Glue, Step Functions, Batch). Trigger when the user says 'productionize this notebook', 'convert notebook to script', 'make this schedulable', 'clean up this POC', or shares a .ipynb file and asks what to do next."
---

# Notebook to Pipeline

Refactor a POC notebook into a structured Python pipeline that is testable, schedulable, and properly tracked in MLflow.

---

## When to Use

- Notebook has proven the approach and now needs to run reliably on a schedule
- Notebook mixes data loading, feature engineering, modeling, and evaluation in a single linear file
- Output needs to be tracked in MLflow with artifacts in S3 or local artifact store
- Pipeline needs to run on AWS (Glue, Step Functions, Batch, or Lambda)

Do **not** run this skill on exploratory notebooks that are still evolving. Productionizing too early locks in decisions before they're ready.

---

## Step 1: Read and Map the Notebook

Ask the user to share the notebook path or paste key cells. Map each cell into one of these stages:

| Stage | What it does |
|-------|-------------|
| `data_loading` | Reads raw data from source (Redshift, S3, local) |
| `feature_engineering` | Transforms, filters, encodes, creates features |
| `model_training` | Fits the model |
| `evaluation` | Computes metrics, runs cross-validation, plots |
| `output` | Writes predictions, saves model, exports report |
| `config` | Hardcoded constants to extract (paths, params, seeds) |
| `scratch` | Exploratory cells with no permanent value — flag for deletion |

Produce the mapping table before touching any code. Confirm with the user before proceeding.

---

## Step 2: Target File Structure

Propose this structure. Adjust if the project already has a layout.

```
<project-root>/
├── config/
│   ├── config.yaml           # base config (see /yaml-config-designer)
│   └── config.dev.yaml
├── src/
│   ├── config.py             # config loader
│   ├── data/
│   │   └── loader.py         # data loading functions
│   ├── features/
│   │   └── engineering.py    # feature construction
│   ├── models/
│   │   └── train.py          # training and evaluation
│   └── pipeline.py           # orchestrator
├── scripts/
│   └── run_pipeline.sh       # CLI entry point
├── tests/
│   └── test_features.py      # unit tests for feature engineering
└── notebooks/
    └── archive/
        └── poc_<name>.ipynb  # original notebook, archived not deleted
```

---

## Step 3: Refactor Each Stage

### Data Loading (`src/data/loader.py`)

- Single function `load_data(cfg: dict) -> pd.DataFrame`
- Parameterize source, date range, and column selection from config
- Basic validation: shape > 0, required columns present, no all-null columns

### Feature Engineering (`src/features/engineering.py`)

- Single function `engineer_features(df: pd.DataFrame, cfg: dict) -> pd.DataFrame`
- Must be a **pure function** — same input always produces same output
- No data loading inside this function
- Flag any transformation that must be fit on train only (scaling, encoding, imputation) — call out explicitly so the user handles fit/transform separation

### Model Training (`src/models/train.py`)

- `train(X_train, y_train, cfg: dict) -> model` — hyperparameters from `cfg["model"]["params"]`
- `evaluate(model, X_test, y_test) -> dict` — returns a plain metrics dict
- MLflow logging follows `/mlflow-experiment` conventions

### Pipeline Orchestrator (`src/pipeline.py`)

```python
# src/pipeline.py
import mlflow
from src.config import load_config
from src.data.loader import load_data
from src.features.engineering import engineer_features
from src.models.train import train, evaluate

def run(env: str = "dev") -> None:
    cfg = load_config(env)
    mlflow.set_experiment(cfg["mlflow"]["experiment_name"])

    with mlflow.start_run():
        mlflow.log_params(cfg["model"]["params"])
        mlflow.set_tag("status", "experimental")
        mlflow.set_tag("env", env)

        df = load_data(cfg)
        df = engineer_features(df, cfg)

        # split — extract from notebook, parameterize via cfg["split"]
        # X_train, X_test, y_train, y_test = split(df, cfg)

        model = train(X_train, y_train, cfg)
        metrics = evaluate(model, X_test, y_test)
        mlflow.log_metrics(metrics)
        mlflow.sklearn.log_model(model, artifact_path="model/")

if __name__ == "__main__":
    import sys
    run(env=sys.argv[1] if len(sys.argv) > 1 else "dev")
```

---

## Step 4: Tests

Generate at least one test for feature engineering. It is the most error-prone stage and the easiest to test in isolation.

```python
# tests/test_features.py
import pandas as pd
from src.features.engineering import engineer_features

def test_output_columns_present():
    raw = pd.DataFrame({"account_id": [1], "event_ts": ["2024-01-01"], "revenue": [100.0]})
    cfg = {}
    result = engineer_features(raw, cfg)
    expected = ["account_id", "revenue_30d_sum"]  # replace with actual expected columns
    assert all(col in result.columns for col in expected)

def test_no_nulls_in_required_features():
    raw = pd.DataFrame({"account_id": [1, 2], "revenue": [100.0, None]})
    cfg = {}
    result = engineer_features(raw, cfg)
    assert result["revenue"].notna().all()  # adjust to match actual fill logic
```

---

## Step 5: Archive the Notebook

Move the original notebook to `notebooks/archive/poc_<name>.ipynb`. Do not delete it — it is the reference for design decisions made during exploration.

---

## Output Artifacts

| Artifact | Path |
|----------|------|
| Data loader | `src/data/loader.py` |
| Feature engineering | `src/features/engineering.py` |
| Training module | `src/models/train.py` |
| Pipeline orchestrator | `src/pipeline.py` |
| Config files | `config/config.yaml`, `config/config.dev.yaml` |
| Tests | `tests/test_features.py` |
| Archived notebook | `notebooks/archive/poc_<name>.ipynb` |

---

## Quality Gates

Before declaring the refactor complete:

- [ ] No data loading inside feature engineering functions
- [ ] All hyperparameters come from config, not hardcoded
- [ ] MLflow logging in place: params, metrics, model artifact, status tag
- [ ] At least one unit test covers feature engineering
- [ ] `src/pipeline.py` runs end-to-end without importing from the notebook
- [ ] Original notebook archived, not deleted

---

## Common Failure Modes

- **Monolithic script** — dumping all notebook code into a single `pipeline.py` function. The orchestrator should call other modules, not contain their logic.
- **Hardcoded paths surviving the refactor** — the most common notebook smell. Push everything into config.
- **Leaky feature engineering** — fit-transform logic (scaling, encoding) applied to the full dataset before splitting. Call this out explicitly when you see it.
- **No tests** — the refactor is not safe to ship if there's no way to verify the feature logic still produces what the notebook produced.

---

## Example Invocation

```
/notebook-to-pipeline notebooks/churn_model_poc.ipynb

Loads from Redshift, engineers 12 features, trains XGBoost, evaluates on a holdout set.
Goal: run weekly on AWS Batch.
```

Expected output: stage mapping for user confirmation, then each module generated in sequence.
