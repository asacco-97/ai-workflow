---
name: data-contract
description: "Define a formal data contract (schema, constraints, SLAs) for a dataset used in modeling or pipelines. Use when the user wants to: document what a dataset is expected to look like, create a machine-readable schema that validation code can enforce, establish shared expectations between a data producer and consumer, or prevent pipeline failures from silent schema drift. Trigger when the user says 'define the schema', 'what columns do we expect', 'write a data contract', 'document this dataset', or is about to build a pipeline or model and hasn't formalized the input spec."
---

# Data Contract

Produce a formal, machine-enforceable data contract for a dataset. A data contract is the authoritative spec for what a dataset must look like — its schema, constraints, and quality expectations. It lives alongside the pipeline or model that consumes the data.

---

## When to Use

- Before building a model or pipeline that depends on a specific dataset structure
- When a dataset crosses a team boundary (producer ≠ consumer)
- When you've had a pipeline break due to an unexpected schema change
- To capture what your `data-quality-audit` found as the expected baseline

Do **not** create a data contract for exploratory, one-off analysis. Contracts are for anything that runs repeatedly or feeds production.

---

## Step 1: Gather Context

Ask for these if not present in the user's message:

1. **Dataset name and source** — what is it, where does it come from (Redshift table, S3 path, API response, upstream pipeline output)?
2. **Update frequency** — how often does this data arrive or refresh?
3. **Primary grain** — what does one row represent? (one event, one account per day, one transaction)
4. **Consumer** — what model or pipeline reads this data?
5. **Existing sample** — can the user paste a few rows, a schema dump, or a `df.describe()` output?

---

## Step 2: Draft the Contract

Produce a YAML contract following this structure. Fill in every field you can infer; use `# TODO` for anything the user must supply.

```yaml
# data-contracts/<dataset-name>.yaml
contract:
  name: <dataset-name>
  version: "1.0"
  owner: "<team-or-person>"           # who is responsible for this data
  source:
    type: <redshift | s3 | postgres | api | pipeline>
    location: "<table-name or s3://bucket/prefix>"
    refresh_cadence: "<daily | hourly | event-driven>"

  grain: "<what one row represents>"   # e.g., "one account per calendar day"

  schema:
    - name: <column_name>
      type: <string | integer | float | boolean | date | timestamp>
      nullable: <true | false>
      description: "<what this column means>"
      constraints:
        min: <value>                   # omit if not applicable
        max: <value>
        allowed_values: []             # omit if not a categorical
        regex: "<pattern>"            # omit if not string-typed

  quality:
    row_count:
      min_expected: <N>               # minimum rows per delivery
    freshness:
      max_age_hours: <N>              # how stale is too stale
    completeness:                     # columns that must not have nulls above a threshold
      - column: <column_name>
        max_null_pct: 0.0             # 0.0 = no nulls allowed
    uniqueness:
      - columns: [<col1>, <col2>]     # combination that must be unique (primary key)

  sla:
    availability: "99%"               # expected uptime/delivery reliability
    support_contact: "<email or channel>"
```

---

## Step 3: Annotate Decisions

Below the YAML, write a short `## Notes` section explaining:

- Any constraints that are inferred (not stated by the user) — flag these for confirmation
- Any columns where the constraint is approximate or may need tuning after seeing real data
- Known exceptions (e.g., "nulls are allowed in `revenue` for free-tier accounts")

---

## Step 4: Validation Stub

Generate a Python snippet using `pandera` (preferred) or `great_expectations` that enforces the schema and key constraints from the contract. Keep it minimal — the contract YAML is the source of truth, not the code.

```python
import pandera as pa
from pandera import Column, DataFrameSchema, Check

schema = DataFrameSchema(
    {
        "<column_name>": Column(
            dtype="<int64 | float64 | str | bool | datetime64[ns]>",
            nullable=<True | False>,
            checks=[
                Check.ge(<min>),   # omit if no min constraint
                Check.le(<max>),   # omit if no max constraint
            ],
        ),
        # ... repeat for each constrained column
    },
    checks=[
        Check(lambda df: df.duplicated(subset=["<pk_col1>", "<pk_col2>"]).sum() == 0,
              error="Primary key uniqueness violated"),
    ],
)

# Run: schema.validate(df)  — raises SchemaError on violation
```

---

## Output Artifacts

| Artifact | Suggested Path |
|----------|---------------|
| Data contract YAML | `data-contracts/<dataset-name>.yaml` |
| Validation stub | `src/validation/<dataset-name>_contract.py` |

Write both files if the user confirms the contract looks correct.

---

## Quality Gates

Before finalizing:

- [ ] Every column in the schema has a type and a `nullable` flag
- [ ] Primary key (uniqueness constraint) is identified
- [ ] Freshness SLA is specified if the data has a time component
- [ ] At least one completeness constraint is defined
- [ ] Inferred constraints are labeled `# TODO: confirm`

---

## Common Failure Modes

- **Too permissive** — contracts with `nullable: true` everywhere and no row count minimums catch nothing. Push for specific constraints.
- **Too rigid** — constraints set from a single sample that may not reflect all valid states. Ask about known exceptions before finalizing.
- **Schema without grain** — without knowing what one row represents, column-level constraints are meaningless. Always pin the grain first.
- **Skipping the validation stub** — a YAML contract without enforcement code is documentation, not a contract.

---

## Example Invocation

```
/data-contract

Dataset: `account_events` table in Redshift.
One row = one event per account (account_id, event_type, event_ts, revenue_usd).
This feeds our churn model feature pipeline. It refreshes hourly. account_id + event_ts 
should be unique. revenue_usd can be null for non-revenue events.
```

Expected output: contract YAML at `data-contracts/account-events.yaml` + pandera validation stub.
