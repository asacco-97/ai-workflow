---
description: Audit data before feature engineering.
---

# Data quality

Run `/data-quality-audit` or spawn `data-auditor` before any feature engineering or train/test split. Check for:

- **Null rates** — flag any column with > 5% nulls before deciding to impute or drop.
- **Duplicates** — confirm whether duplicates are expected (e.g., multiple events per entity) or errors.
- **Class imbalance** — report the positive rate for any classification target.
- **Distribution anomalies** — impossible values, clipped ranges, or unexpected zeros.
- **Time coverage** — for time-series data, confirm the date range and identify gaps.

Document findings in `reports/data-quality/`. Do not proceed to modeling if a critical quality issue (e.g., target leakage, > 50% nulls in key columns) is unresolved.
