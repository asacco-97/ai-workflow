---
globs: notebooks/**/*.ipynb
description: Rules for converting notebooks to production pipelines.
---

# Notebook to pipeline

Use `/notebook-to-pipeline` or spawn `notebook-refactorer` when moving from POC to production.

A notebook is ready for conversion when:
- It runs end-to-end without errors on a clean kernel.
- The logic is linear — no cells that must be run out of order.
- The target variable, data paths, and key parameters are identified and separated from the logic.

When converting:
- Extract reusable logic into functions in `src/`. Do not copy-paste notebook cells into a script.
- Replace hardcoded values with YAML config parameters.
- Write at least one unit test per extracted function before deleting the notebook cell.
- The notebook may be archived but must not be the production code path.
