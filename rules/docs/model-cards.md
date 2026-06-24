---
globs:
  - reports/model-cards/**/*.md
  - docs/model-cards/**/*.md
description: Required sections for model cards.
---

# Model cards

Every model card must include:

1. **Model purpose** — what decision does this model support and for whom.
2. **Training data** — source, date range, population scope, and any known biases.
3. **Performance** — primary metric on validation and holdout sets, with confidence intervals.
4. **Limitations** — population segments or conditions where the model is known to underperform.
5. **Inputs and outputs** — feature list with types, and output schema.
6. **Fairness considerations** — whether protected attributes were analyzed and what was found.
7. **Usage guidance** — when to use the model and when not to.

Use `/model-card` to scaffold. Do not publish a model card that omits the Limitations section.
