---
name: experiment-backlog
description: "Maintain a structured backlog of modeling experiments: add, prioritize, and update experiments with hypothesis, expected outcome, status, and results. Use when the user wants to: track what experiments are queued vs. running vs. done, capture the rationale for an experiment before running it, prioritize which experiment to run next, or record results and learnings after a run completes. Trigger when the user says 'add this to the backlog', 'what should we try next', 'log the results of this experiment', 'prioritize our experiments', or asks to organize their modeling work."
---

# Experiment Backlog

Maintain a running log of modeling experiments — what to try, why, and what was learned. The backlog prevents duplicate work, surfaces prioritization gaps, and creates an audit trail for modeling decisions.

---

## When to Use

- Starting iterative model development (more than one run planned)
- After a run completes and you want to capture the outcome before moving on
- When deciding what to try next (forces explicit hypothesis before starting)
- During a project review to show the reasoning behind the modeling path taken

Do **not** use for one-off analyses that will never be revisited.

---

## Backlog File

Maintain the backlog at `docs/experiment_backlog.md`. Create it on first use.

---

## Backlog Entry Format

Each experiment entry follows this template:

```markdown
### EXP-<NNN>: <Short name>

**Status:** `queued` | `in-progress` | `done` | `abandoned`
**Priority:** `high` | `medium` | `low`
**Added:** YYYY-MM-DD
**Completed:** YYYY-MM-DD  ← fill in when done

**Hypothesis**
_What do you believe will happen and why?_
e.g., "Adding account age as a feature will improve AUC-PR by ~2pp because newer accounts have different churn patterns than tenured accounts."

**What to try**
_Concrete description of what changes in this experiment._
- Feature set: [list changes]
- Model config: [list changes]
- Data: [any data changes]

**Success criterion**
_How will you know this worked? Use a specific, measurable threshold._
e.g., AUC-PR on val set ≥ baseline + 0.02

**MLflow run ID**
`<run-id>` ← fill in after starting

**Result**
_Fill in after completion. What actually happened?_
- Primary metric: <value>
- vs. baseline: <+/- delta>
- Unexpected findings: <anything surprising>
- Verdict: `improved` | `no improvement` | `degraded` | `inconclusive`

**Learnings**
_What does this tell us about the data or the model? What should we try next as a result?_
```

---

## Modes

### Mode A: Add an Experiment

When the user describes something to try, generate a filled-out entry with:
- Auto-assigned EXP number (next sequential number in the file)
- Status: `queued`
- Hypothesis drafted from the user's description — ask for clarification if the hypothesis isn't stated explicitly
- Success criterion — do not let an experiment be added without one

Ask: "What's the hypothesis — what do you think will happen and why?" if the user just says "try X."

### Mode B: Log Results

When the user says "log the results" or "this run is done", update the matching entry:
- Set `Status` to `done` or `abandoned`
- Fill in `Completed` date
- Fill in `MLflow run ID`
- Fill in `Result` block — ask for primary metric value and comparison to baseline
- Draft `Learnings` based on the result, then ask the user to confirm

### Mode C: Prioritize

When the user asks "what should we try next?", review all `queued` entries and rank by:
1. Experiments that address a current blocker or open finding
2. Highest expected delta on the primary metric
3. Lowest implementation effort (quick wins that resolve uncertainty cheaply)

Present as a ranked list with one-sentence rationale per entry, not just a sorted table.

### Mode D: Summarize

When the user asks for a summary, produce a table:

```markdown
| ID | Name | Status | Verdict | Primary Metric | vs. Baseline |
|----|------|--------|---------|---------------|-------------|
| EXP-001 | Baseline XGBoost | done | improved | AUC-PR: 0.61 | — |
| EXP-002 | Add account age | done | improved | AUC-PR: 0.63 | +0.02 |
| EXP-003 | SMOTE resampling | done | no improvement | AUC-PR: 0.60 | -0.01 |
| EXP-004 | Log-transform revenue | queued | — | — | — |
```

Follow the table with a one-paragraph narrative: what was tried, what moved the needle, and what the current best model is.

---

## Output Artifacts

| Artifact | Path |
|----------|------|
| Backlog file | `docs/experiment_backlog.md` |

---

## Quality Gates

Before adding an experiment:

- [ ] Hypothesis is stated (what do you think will happen and why?)
- [ ] Success criterion is specific and measurable
- [ ] Experiment is meaningfully different from existing entries (no duplicate work)

Before logging results:

- [ ] MLflow run ID is recorded
- [ ] Verdict is one of the four defined categories
- [ ] Learnings section is filled in, not left blank

---

## Common Failure Modes

- **Adding experiments without hypotheses** — "try adding feature X" is not an experiment; "add feature X because we expect it to improve recall for small accounts" is. Push back and ask for the hypothesis.
- **No success criterion** — if you don't define what "worked" means before running, you'll rationalize any result as a success.
- **Never updating completed entries** — a backlog that is only ever added to and never closed degrades into noise. Always log results immediately after a run.
- **Backlog growing without pruning** — 20 queued experiments means nothing is prioritized. Prune to the top 5 queued at any time, or mark low-priority items `parked`.

---

## Example Invocations

```
/experiment-backlog add

I want to try log-transforming revenue_usd before training. I think it'll help
because raw revenue has huge outliers pulling the model toward big accounts.
```

```
/experiment-backlog log results

EXP-004 is done. AUC-PR on val was 0.64, up from 0.63 baseline. Run ID: abc123.
```

```
/experiment-backlog prioritize

What should we try next given EXP-003 didn't help and EXP-004 showed a small gain?
```
