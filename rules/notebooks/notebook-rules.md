---
globs: notebooks/**/*.ipynb, notebooks/**/*.py
description: Rules for Jupyter notebooks.
---

# Notebook rules

- Notebooks are for exploration and proof-of-concept only. Do not put production logic in a notebook.
- Every cell must be runnable in order from a clean kernel. Cells that depend on out-of-order execution are invalid.
- Before committing a notebook that informs a decision, clear all outputs. Do not commit notebooks with embedded data, credentials, or large output blobs.
- Do not hardcode file paths, credentials, or hyperparameters in notebook cells. Use a config file or environment variables.
- If a notebook contains a conclusion that drives a modeling decision, write that decision to `memory/decisions/`. The notebook itself is not the memory.
