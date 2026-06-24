#!/usr/bin/env bash
# Install skills, agents, and rules into ~/.claude
# Usage: bash scripts/install-global.sh [copy|symlink]
# Default: copy

set -euo pipefail

MODE="${1:-copy}"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CLAUDE_DIR="${HOME}/.claude"

if [[ "$MODE" != "copy" && "$MODE" != "symlink" ]]; then
  echo "Usage: $0 [copy|symlink]" >&2
  exit 1
fi

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
    if [[ -L "$dest" ]]; then
      rm "$dest"
    fi
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
else
  echo "WARN: skills/ not found in repo root, skipping."
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
else
  echo "WARN: agents/ not found in repo root, skipping."
fi

# --- rules (recursive, preserves subdirectory structure) ---------------------

RULES_SRC="${REPO_ROOT}/rules"
RULES_DEST="${CLAUDE_DIR}/rules"

if [[ -d "$RULES_SRC" ]]; then
  while IFS= read -r -d '' rule_file; do
    rel="${rule_file#${RULES_SRC}/}"
    dest="${RULES_DEST}/${rel}"
    mkdir -p "$(dirname "$dest")"
    if [[ "$MODE" == "symlink" ]]; then
      [[ -L "$dest" ]] && rm "$dest"
      ln -s "$rule_file" "$dest"
    else
      cp "$rule_file" "$dest"
    fi
    installed_rules+=("$rel")
  done < <(find "$RULES_SRC" -name "*.md" -print0 | sort -z)
else
  echo "WARN: rules/ not found in repo root, skipping."
fi

# --- summary -----------------------------------------------------------------

echo ""
echo "Install complete (mode: ${MODE})"
echo ""
echo "Skills  → ${SKILLS_DEST} (${#installed_skills[@]})"
for s in "${installed_skills[@]}"; do echo "  $s"; done

echo ""
echo "Agents  → ${AGENTS_DEST} (${#installed_agents[@]})"
for a in "${installed_agents[@]}"; do echo "  $a"; done

if [[ ${#installed_rules[@]} -gt 0 ]]; then
  echo ""
  echo "Rules   → ${RULES_DEST} (${#installed_rules[@]})"
  for r in "${installed_rules[@]}"; do echo "  $r"; done
fi

echo ""
echo "Run 'bash scripts/verify-install.sh' to confirm."
