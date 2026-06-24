---
description: Data privacy rules. Always on.
---

# Data privacy

- Do not store raw data files in the repo. Store data paths, schemas, and sample sizes only.
- Do not log PII (names, emails, phone numbers, account IDs, IP addresses) to MLflow, notebooks, memory files, or console output.
- If a dataset contains PII, confirm with the user that it is appropriately anonymized or pseudonymized before proceeding with any analysis.
- Do not include real row-level data in examples, tests, or documentation. Use synthetic data.
- If you discover PII in a committed file, flag it immediately and do not analyze or redistribute it.
