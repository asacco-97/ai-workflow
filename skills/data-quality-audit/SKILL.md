---
name: data-quality-audit
description: "Systematically profile a dataset for quality issues: nulls, duplicates, type mismatches, outliers, distribution anomalies, and time-series gaps. Use when the user wants to: understand a new dataset before modeling, detect data quality problems that may affect model training, produce a DQ report to share with a data producer, or establish a quality baseline before writing a data contract. Trigger when the user says 'profile this data', 'check data quality', 'audit this dataset', 'what's wrong with my data', 'before I model this I want to understand it', or shares a dataframe path/description and asks for a quality check."
---

# Data Quality Audit

Profile a dataset systematically for quality issues before it enters a model or pipeline. The goal is to surface problems early, when they're cheap to fix, not after a model has been trained on bad data.

---

## When to Use

- First contact with a new dataset before exploratory analysis or modeling
- After a pipeline breaks or produces surprising model outputs
- Before writing a `data-contract` — auditing first tells you what the constraints actually are
- When handing off data QA findings to a data engineering team

---

## Step 1: Establish Context

Before auditing, confirm:

1. **Data location** — Redshift table, S3 path, local CSV/parquet, DataFrame already in memory?
2. **Primary grain** — what does one row represent?
3. **Time column** — is there a timestamp or date column? What's the expected cadence?
4. **Primary key** — which column(s) should be unique?
5. **Target variable** — if this feeds a model, what is the target? (Audit it separately with extra scrutiny)

If the user can run Python locally, generate an audit script to execute against the data. If not, ask for a `df.info()`, `df.describe()`, and a sample of rows to work from.

---

## Step 2: Generate the Audit Script

Produce a self-contained Python script that runs all checks and writes a structured report. The user should be able to run `python audit.py --input <path>` and get a report.

```python
# scripts/audit_<dataset_name>.py
import pandas as pd
import numpy as np
from pathlib import Path

def audit(df: pd.DataFrame, grain_cols: list[str], time_col: str | None = None) -> dict:
    report = {}

    # --- Shape ---
    report["shape"] = {"rows": len(df), "cols": len(df.columns)}

    # --- Nulls ---
    null_summary = (df.isnull().mean() * 100).round(2)
    report["nulls"] = null_summary[null_summary > 0].to_dict()  # only non-zero

    # --- Duplicates ---
    n_dupes = df.duplicated(subset=grain_cols).sum()
    report["duplicates"] = {"n_duplicate_rows": int(n_dupes), "on_columns": grain_cols}

    # --- Type summary ---
    report["dtypes"] = df.dtypes.astype(str).to_dict()

    # --- Numeric distributions ---
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    desc = df[numeric_cols].describe(percentiles=[0.01, 0.25, 0.5, 0.75, 0.99])
    report["numeric_summary"] = desc.to_dict()

    # --- Outliers (IQR method) ---
    outlier_flags = {}
    for col in numeric_cols:
        q1, q3 = df[col].quantile(0.25), df[col].quantile(0.75)
        iqr = q3 - q1
        n_outliers = int(((df[col] < q1 - 1.5 * iqr) | (df[col] > q3 + 1.5 * iqr)).sum())
        if n_outliers > 0:
            outlier_flags[col] = n_outliers
    report["outliers"] = outlier_flags

    # --- Categorical cardinality ---
    cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
    report["categoricals"] = {
        col: {"n_unique": df[col].nunique(), "top_5": df[col].value_counts().head(5).to_dict()}
        for col in cat_cols
    }

    # --- Time-series gaps (if time_col provided) ---
    if time_col and time_col in df.columns:
        ts = pd.to_datetime(df[time_col]).sort_values()
        deltas = ts.diff().dropna()
        mode_delta = deltas.mode()[0]
        n_gaps = int((deltas > mode_delta * 1.5).sum())
        report["time_gaps"] = {
            "time_col": time_col,
            "min_date": str(ts.min()),
            "max_date": str(ts.max()),
            "expected_cadence": str(mode_delta),
            "n_gaps_detected": n_gaps,
        }

    return report


if __name__ == "__main__":
    import json, argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--grain", nargs="+", default=["id"])
    parser.add_argument("--time-col", default=None)
    args = parser.parse_args()

    df = pd.read_parquet(args.input) if args.input.endswith(".parquet") else pd.read_csv(args.input)
    report = audit(df, grain_cols=args.grain, time_col=args.time_col)

    out_path = Path("reports/dq_audit.json")
    out_path.parent.mkdir(exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(report, f, indent=2, default=str)
    print(f"Audit written to {out_path}")
    print(json.dumps(report, indent=2, default=str))
```

---

## Step 3: Interpret Results

After the user runs the script (or pastes `df.info()` / `df.describe()` output), analyze and categorize findings:

### Severity Tiers

| Tier | Meaning | Examples |
|------|---------|---------|
| **Blocker** | Will corrupt model training or pipeline output | Duplicate rows on grain, target leakage via a proxy column, >30% nulls on the target |
| **Warning** | Likely to degrade model performance if not addressed | >5% nulls on key features, outliers at implausible scale (revenue = -$99M), time gaps in a time-series model |
| **Info** | Worth knowing but low immediate impact | High cardinality categoricals, minor skew, sparse categories |

---

## Step 4: Structured Report

Produce the audit summary in this format:

---

### DQ Audit: `<dataset-name>`

**Grain:** `<what one row represents>`
**Rows:** N | **Columns:** M | **Date range:** YYYY-MM-DD → YYYY-MM-DD

#### Blockers
- [ ] `<column>`: `<issue>` — `<why it's a blocker>`

#### Warnings
- [ ] `<column>`: `<issue>` — `<recommended action>`

#### Info
- `<observation>`

#### Recommended next steps
1. Fix blockers before any modeling
2. [Specific action for the most impactful warning]
3. Consider writing a `data-contract` to lock down these expectations

---

## Output Artifacts

| Artifact | Suggested Path |
|----------|---------------|
| Audit script | `scripts/audit_<dataset>.py` |
| JSON report | `reports/dq_audit.json` |
| Human summary | This conversation (paste into ticket or doc) |

---

## Quality Gates

Before delivering the audit:

- [ ] Grain is confirmed and duplicates checked against it
- [ ] Target variable (if known) is audited separately
- [ ] Time-series gaps checked if a time column exists
- [ ] Findings are tiered (Blocker / Warning / Info), not just listed flat
- [ ] At least one recommended next step is specific and actionable

---

## Common Failure Modes

- **Auditing without knowing the grain** — aggregate statistics are meaningless without knowing what one row is
- **Flagging everything as a warning** — untriaged findings don't help; tier them so blockers are obvious
- **Missing the target** — the target column is the most important column in the dataset; audit it first
- **Skipping time-gap analysis** — for time-series data, gaps are often the most damaging issue and the easiest to miss in summary statistics

---

## Example Invocation

```
/data-quality-audit

Data: s3://my-bucket/features/churn_features_2024.parquet
Grain: one row per account_id per week
Time column: week_start_date
Target: churned (0/1)
```

Expected output: audit script + severity-tiered findings report.
