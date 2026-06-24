#!/usr/bin/env bash
# Install skills, agents, rules, and project scaffolding into a target project.
# Usage: bash scripts/install-project.sh <project-path> [copy|symlink]
# Default mode: copy

set -euo pipefail

PROJECT_DIR="${1:-}"
MODE="${2:-copy}"

if [[ -z "$PROJECT_DIR" ]]; then
  echo "Usage: $0 <project-path> [copy|symlink]" >&2
  exit 1
fi

if [[ "$MODE" != "copy" && "$MODE" != "symlink" ]]; then
  echo "Mode must be 'copy' or 'symlink'" >&2
  exit 1
fi

if [[ ! -d "$PROJECT_DIR" ]]; then
  echo "Project directory does not exist: $PROJECT_DIR" >&2
  exit 1
fi

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROJECT_DIR="$(cd "$PROJECT_DIR" && pwd)"
CLAUDE_DIR="${PROJECT_DIR}/.claude"

installed_skills=()
installed_agents=()
installed_rules=()

# --- helpers -----------------------------------------------------------------

install_item() {
  local src="$1"
  local dest_dir="$2"
  local name
  name="$(basename "$src")"
  local dest="${dest_dir}/${name}"

  if [[ "$MODE" == "symlink" ]]; then
    if [[ -L "$dest" ]]; then rm "$dest"; fi
    ln -s "$src" "$dest"
  else
    if [[ -d "$src" ]]; then
      cp -r "$src" "$dest_dir/"
    else
      cp "$src" "$dest"
    fi
  fi
}

# --- skills ------------------------------------------------------------------

SKILLS_SRC="${REPO_ROOT}/skills"
SKILLS_DEST="${CLAUDE_DIR}/skills"

if [[ -d "$SKILLS_SRC" ]]; then
  mkdir -p "$SKILLS_DEST"
  for skill_dir in "${SKILLS_SRC}"/*/; do
    [[ -d "$skill_dir" ]] || continue
    name="$(basename "$skill_dir")"
    install_item "$skill_dir" "$SKILLS_DEST"
    installed_skills+=("$name")
  done
fi

# --- agents ------------------------------------------------------------------

AGENTS_SRC="${REPO_ROOT}/agents"
AGENTS_DEST="${CLAUDE_DIR}/agents"

if [[ -d "$AGENTS_SRC" ]]; then
  mkdir -p "$AGENTS_DEST"
  for agent_file in "${AGENTS_SRC}"/*.md; do
    [[ -f "$agent_file" ]] || continue
    name="$(basename "$agent_file")"
    install_item "$agent_file" "$AGENTS_DEST"
    installed_agents+=("$name")
  done
fi

# --- rules -------------------------------------------------------------------

RULES_SRC="${REPO_ROOT}/rules"
RULES_DEST="${CLAUDE_DIR}/rules"

if [[ -d "$RULES_SRC" ]]; then
  has_rules=false
  for f in "${RULES_SRC}"/*; do
    [[ -e "$f" ]] && has_rules=true && break
  done
  if $has_rules; then
    mkdir -p "$RULES_DEST"
    for rule_file in "${RULES_SRC}"/*; do
      [[ -f "$rule_file" ]] || continue
      name="$(basename "$rule_file")"
      install_item "$rule_file" "$RULES_DEST"
      installed_rules+=("$name")
    done
  fi
fi

# --- CLAUDE.md template ------------------------------------------------------

TEMPLATE_CLAUDE="${REPO_ROOT}/templates/project-claude/CLAUDE.md"
PROJECT_CLAUDE="${PROJECT_DIR}/CLAUDE.md"

if [[ -f "$TEMPLATE_CLAUDE" && ! -f "$PROJECT_CLAUDE" ]]; then
  cp "$TEMPLATE_CLAUDE" "$PROJECT_CLAUDE"
  echo "Copied templates/project-claude/CLAUDE.md → ${PROJECT_DIR}/CLAUDE.md"
elif [[ -f "$PROJECT_CLAUDE" ]]; then
  echo "CLAUDE.md already exists at ${PROJECT_DIR}/CLAUDE.md — skipping."
fi

# --- memory / docs / reports scaffolding -------------------------------------

DIRS=(
  "memory/decisions"
  "memory/failed-approaches"
  "memory/workflows"
  "memory/session-logs"
  "docs/plans"
  "docs/data-contracts"
  "docs/validation"
  "docs/experiments"
  "reports/model-cards"
  "reports/validation"
  "reports/data-quality"
)

created_dirs=()
for dir in "${DIRS[@]}"; do
  target="${PROJECT_DIR}/${dir}"
  if [[ ! -d "$target" ]]; then
    mkdir -p "$target"
    # Place a .gitkeep so empty dirs are tracked
    touch "${target}/.gitkeep"
    created_dirs+=("$dir")
  fi
done

# Copy memory index template if present and not already there
TEMPLATE_MEM="${REPO_ROOT}/templates/project-claude/memory/index.md"
PROJECT_MEM="${PROJECT_DIR}/memory/index.md"
if [[ -f "$TEMPLATE_MEM" && ! -f "$PROJECT_MEM" ]]; then
  cp "$TEMPLATE_MEM" "$PROJECT_MEM"
  echo "Copied templates/project-claude/memory/index.md → ${PROJECT_DIR}/memory/index.md"
fi

# --- summary -----------------------------------------------------------------

echo ""
echo "Project install complete (mode: ${MODE})"
echo "Target: ${PROJECT_DIR}"
echo ""
echo "Skills  → .claude/skills/ (${#installed_skills[@]})"
echo "Agents  → .claude/agents/ (${#installed_agents[@]})"
[[ ${#installed_rules[@]} -gt 0 ]] && echo "Rules   → .claude/rules/ (${#installed_rules[@]})"

if [[ ${#created_dirs[@]} -gt 0 ]]; then
  echo ""
  echo "Created scaffolding dirs (${#created_dirs[@]}):"
  for d in "${created_dirs[@]}"; do echo "  $d"; done
fi

echo ""
echo "Next: open ${PROJECT_DIR}/CLAUDE.md and fill in the project purpose placeholder."
