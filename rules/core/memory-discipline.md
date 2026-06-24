---
description: What to write to memory after a session, and when.
---

# Memory discipline

Write to memory only when the information would be lost without it and is not already captured in MLflow, the data contract, or the code.

| What happened | Where to write |
|---|---|
| Key architectural or modeling decision | `memory/decisions/` |
| Approach tried and abandoned | `memory/failed-approaches/` |
| Repeatable runbook or procedure | `memory/workflows/` |
| Domain or business context | `memory/project-context/` |
| Session summary with open questions | `memory/session-logs/` (ephemeral) |

Never write to memory: secrets, tokens, credentials, raw row-level data, PII, or anything already captured in MLflow.

When the user says "remember this," identify which folder applies and write a file there. Do not write the same information to both `memory/` and `docs/` — pick the right home once.
