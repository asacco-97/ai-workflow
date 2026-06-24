---
description: Record hypothesis and expected outcome before running any experiment.
---

# Experiment design

Before running any training run:

1. Write the hypothesis: "If we do X, we expect metric Y to change by Z because of reason R."
2. Add it to the experiment backlog with `/experiment-backlog`.
3. Record the expected direction (higher is better / lower is better) and the minimum meaningful improvement.

After the run:
- Log results back to the backlog entry.
- Record what was learned, not just the number.
- If the hypothesis was wrong, record why — this is more valuable than a result that confirms expectations.

Experiments without a prior hypothesis cannot be interpreted reliably. Do not run a training run just to "see what happens."
