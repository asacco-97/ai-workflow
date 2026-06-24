# ai-workflow

A portable Claude Code workflow system for data science, MLflow tracking, Bayesian/statistical modeling, project planning, validation, and stakeholder reporting.

Install it globally and it follows you to every project. Install it into a specific project and it becomes part of that project's tooling.

---

## Folder structure

```
ai-workflow/
├── agents/           # Custom subagent definitions (.md files with YAML frontmatter)
├── evals/            # Evaluation prompts for skills and subagents
├── prompts/          # Reusable standalone prompts
├── rules/            # Reusable Claude rules (copyable into ~/.claude/rules or .claude/rules)
├── scripts/          # Install, verify, and audit scripts
├── skills/           # Custom skill definitions (each skill is a folder with SKILL.md)
├── templates/        # Project templates (e.g. templates/project-claude/ for CLAUDE.md starters)
└── third_party/      # Reference material only — do not blindly install (see below)
```

---

## Global assets vs. project-level assets

**Global** assets live under `~/.claude/` and are available in every Claude Code session on your machine:

```
~/.claude/
├── agents/       ← subagent .md files
├── rules/        ← rule files
└── skills/       ← skill folders
```

**Project-level** assets live under a project's `.claude/` directory and only apply when Claude Code runs inside that project:

```
my-project/
└── .claude/
    ├── agents/
    ├── rules/
    └── skills/
```

Project-level assets override global assets of the same name. Use project-level assets for project-specific behavior; use global assets for workflow patterns you apply everywhere.

---

## Third-party assets

`third_party/` contains skills and subagents created by other people, included for reference only. Do not install them blindly. Read each file, understand what it does, and copy only what you need — manually, after review. The audit script (`scripts/audit-assets.py`) will not scan `third_party/` by default.

---

## Quick start

```bash
# 1. Clone the repo
git clone <repo-url> ~/repos/ai-workflow
cd ~/repos/ai-workflow

# 2. Install globally (copy mode — safe on Windows)
bash scripts/install-global.sh copy

# 3. Verify
bash scripts/verify-install.sh

# 4. Audit repo assets for issues
python scripts/audit-assets.py
```

To set up a specific project:

```bash
bash scripts/install-project.sh /path/to/my-project
```

---

## Recommended daily workflow

1. **Start a new task** — describe the objective in plain language. Claude will ask clarifying questions before writing code.
2. **Plan before building** — use `/research-to-plan` or spawn `project-planner` before touching notebooks or scripts.
3. **Define the data contract** — run `/data-contract` before feature engineering starts.
4. **Validate assumptions** — run `/ds-model-evaluator` after any major modeling decision.
5. **Track experiments** — use `/mlflow-experiment` so nothing gets lost.
6. **Capture decisions** — write key choices to `memory/decisions/` so future sessions have context.
7. **Review before handoff** — run `/review-own-branch` and `security-privacy-reviewer` before any PR or share.

---

## Normal modeling project sequence

| Phase | Skills | Subagents |
|-------|--------|-----------|
| 1. Plan the project | `/research-to-plan` | `project-planner`, `modeling-architect`, `data-auditor`, `validation-reviewer` |
| 2. Stress-test the plan | `/grill-me-with-docs`, `/ds-model-evaluator` | — |
| 3. Define data contract | `/data-contract` | `data-auditor`, `security-privacy-reviewer` |
| 4. Build data sourcing | — | `data-auditor`, `debugger`, `code-reviewer` |
| 5. POC notebook | `/mlflow-experiment`, `/ds-model-evaluator` | `experiment-runner`, `validation-reviewer` |
| 6. Convert to framework | `/notebook-to-pipeline`, `/yaml-config-designer` | `mlflow-engineer`, `notebook-refactorer` |
| 7. Build validation | `/validation-framework` | `validation-reviewer`, `code-reviewer` |
| 8. Next experiments | `/experiment-backlog` | `literature-scout`, `modeling-architect` |
| 9. Stakeholder summary | `/model-card` | — |
| 10. Pre-PR review | `/review-own-branch` | `code-reviewer`, `security-privacy-reviewer` |

See `USAGE.md` for example prompts at each phase.
