# .claude/rules/

Rule files in this directory are loaded by Claude Code when working in this project.

## Structure

Rules are organized by domain. Each subdirectory is a category; each `.md` file is a rule set.

```
rules/
  core/           workflow sequence, planning, memory discipline, tool use
  data-science/   contracts, quality, validation, leakage, Bayesian modeling
  ml-engineering/ MLflow, configs, reproducibility, AWS, model registry
  software/       Python style, testing, PRs, refactoring, error handling
  notebooks/      notebook conventions and pipeline conversion
  docs/           stakeholder communication, model cards, research notes
  security/       data privacy, secrets, MCP tool use
```

## Path-scoped rules

Some rules apply only when editing specific file types (set via `globs:` in frontmatter):

| Rule file | Applies to |
|---|---|
| `software/python-style.md` | `src/**/*.py`, `tests/**/*.py`, `scripts/**/*.py` |
| `software/testing.md` | `tests/**/*.py` |
| `software/error-handling.md` | `src/**/*.py`, `scripts/**/*.py` |
| `notebooks/notebook-rules.md` | `notebooks/**/*.ipynb`, `notebooks/**/*.py` |
| `notebooks/notebook-to-pipeline.md` | `notebooks/**/*.ipynb` |
| `docs/stakeholder-communication.md` | `docs/**/*.md`, `reports/**/*.md`, `*.md` |
| `docs/model-cards.md` | `reports/model-cards/**/*.md`, `docs/model-cards/**/*.md` |
| `docs/research-notes.md` | `docs/**/*.md` |

All other rules are always on.

## Updating rules

These files are installed from the `ai-workflow` repo. To update:

```bash
bash <path-to-ai-workflow>/scripts/install-project.sh . copy
```

Do not edit rules here directly — edit the source in `ai-workflow/rules/` and reinstall.
