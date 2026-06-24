# Memory index

This file explains what belongs in each memory folder and when to write to it.

---

## Folder guide

### `memory/decisions/`

**What:** Key architectural and modeling decisions.
**When:** After any session that commits to an approach — model family, feature strategy, validation scheme, library choice.
**Format:** One file per decision. Include: what was decided, why, what alternatives were considered, and who (or what) influenced the choice.

Example filename: `2026-06-23-use-hierarchical-bayesian-for-churn.md`

---

### `memory/failed-approaches/`

**What:** Approaches that were tried and abandoned.
**When:** After ruling something out — a model that underperformed, a feature that caused leakage, a CV scheme that was found to be invalid.
**Format:** What was tried, what the outcome was, and why it was abandoned. Include enough detail that a future session won't repeat the same mistake.

Example filename: `2026-07-01-gradient-boosting-overfit-on-sparse-ids.md`

---

### `memory/workflows/`

**What:** Repeatable runbooks and procedures.
**When:** After establishing a repeatable process — how to retrain, how to promote a model, how to regenerate features.
**Format:** Step-by-step instructions. Reference specific scripts and config files.

Example filename: `retrain-procedure.md`

---

### `memory/session-logs/`

**What:** Brief summaries of significant work sessions.
**When:** At the end of any session that made progress worth preserving — not every session, only those that moved something important forward.
**Format:** Date, what was accomplished, open questions for next session.
**Note:** Session logs are ephemeral — archive or delete after the decisions they contain have been captured in `decisions/`.

Example filename: `2026-06-23-poc-notebook-baseline.md`

---

### `memory/project-context/` *(create if needed)*

**What:** Background knowledge that informs modeling decisions but is not a decision itself.
**When:** When you learn something about the domain, the data source, the stakeholders, or the business context that would otherwise be lost.
**Format:** Free-form notes. Keep them factual, not speculative.

Example filename: `domain-glossary.md`, `stakeholder-requirements.md`

---

## What does NOT belong in memory

- Secrets, API keys, tokens, or passwords
- Raw row-level data or PII
- Output that duplicates what MLflow already captures (metrics, params, artifacts)
- Ephemeral debugging notes that are not useful after the bug is fixed
- Anything that would be a security risk if this directory were accidentally committed or shared
