# Installation

## Prerequisites

- Claude Code installed and on your `PATH`
- Bash (Git Bash on Windows) or PowerShell
- Python 3.8+ (for `audit-assets.py`)

---

## Global install

Installs skills, agents, and rules into `~/.claude/` so they are available in every project.

**Bash / Git Bash (Mac, Linux, Windows Git Bash):**

```bash
# From the repo root — copy mode (recommended, works everywhere)
bash scripts/install-global.sh copy

# Symlink mode (Mac/Linux only — see Windows note below)
bash scripts/install-global.sh symlink
```

**PowerShell (Windows):**

```powershell
# From the repo root
pwsh scripts/install-global.ps1
```

---

## Project-level install

Installs skills, agents, and rules into a specific project's `.claude/` directory. Also scaffolds `memory/`, `docs/`, and `reports/` folders, and copies `templates/project-claude/CLAUDE.md` if the project has no `CLAUDE.md` yet.

```bash
# Usage: scripts/install-project.sh <project-path> [copy|symlink]
bash scripts/install-project.sh /path/to/my-project copy
```

---

## Copy mode vs. symlink mode

| Mode | What happens | When to use |
|------|-------------|-------------|
| **copy** | Files are copied. Changes to this repo do not auto-propagate. | Default. Safe on all platforms including Windows. |
| **symlink** | Symlinks are created. Changes to this repo take effect immediately. | Mac/Linux only. Windows requires Developer Mode or admin rights for symlinks. |

**Windows note:** Symlinks on Windows require either Developer Mode enabled (`Settings → For developers → Developer Mode`) or running the terminal as Administrator. Git Bash may silently fall back to copying. PowerShell uses directory junctions for folders, which behave like symlinks for most purposes. If you are not sure, use copy mode.

---

## Verify the install

```bash
bash scripts/verify-install.sh
```

This checks that:
- `~/.claude/skills/` exists with a `SKILL.md` in each subfolder
- `~/.claude/agents/` exists with valid frontmatter in each `.md` file
- `~/.claude/rules/` exists (warning only if absent)

---

## Security and privacy

> **Do not copy secrets, credentials, or confidential data into any Claude Code asset.**

Specifically, never place the following into memory files, rules, skills, templates, or anything tracked by git:

- API keys, tokens, or passwords
- `.env` file contents
- AWS credentials or cloud service keys
- PII or confidential row-level data
- Proprietary business logic that should not leave your machine

Memory files (`memory/`, `docs/`, `reports/`) are for durable technical decisions, not data. The `security-privacy-reviewer` subagent and `audit-assets.py` script will flag suspicious patterns, but they are not a substitute for judgment.

---

## Updating

Pull the latest repo changes and re-run the install script:

```bash
git pull
bash scripts/install-global.sh copy
```

In copy mode, re-running the install overwrites previously installed files with the latest versions.
