---
description: Define a data contract before building pipelines or features.
---

# Data contracts

Before writing any pipeline or feature engineering code:

- Run `/data-contract` to define the schema: column names, types, nullability, valid value ranges, and join keys.
- The contract is the source of truth. Downstream code must not assume anything about the schema that is not in the contract.
- If a column is not in the contract, it must not be used in a feature.
- If real data does not match the contract at runtime, fail loudly — do not silently coerce or drop.

Contracts live in `docs/data-contracts/`. One contract per dataset (or per pipeline input boundary). The contract must be committed before the pipeline code that depends on it.
