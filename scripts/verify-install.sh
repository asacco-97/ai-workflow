#!/usr/bin/env bash
# Verify that skills, agents, and rules are correctly installed in ~/.claude
# Prints warnings for issues; exits 0 unless a hard error is found.

CLAUDE_DIR="${HOME}/.claude"
SKILLS_DIR="${CLAUDE_DIR}/skills"
AGENTS_DIR="${CLAUDE_DIR}/agents"
RULES_DIR="${CLAUDE_DIR}/rules"

warn=0
ok=0

pass() { echo "  OK   $1"; ((ok++)) || true; }
fail() { echo "  WARN $1"; ((warn++)) || true; }

echo "Verifying ~/.claude install..."
echo ""

# --- skills ------------------------------------------------------------------

echo "Skills (${SKILLS_DIR}):"
if [[ ! -d "$SKILLS_DIR" ]]; then
  fail "skills/ directory does not exist"
else
  found=0
  for skill_dir in "${SKILLS_DIR}"/*/; do
    [[ -d "$skill_dir" ]] || continue
    name="$(basename "$skill_dir")"
    ((found++)) || true
    if [[ -f "${skill_dir}/SKILL.md" ]]; then
      pass "${name}/SKILL.md"
    else
      fail "${name}/ — missing SKILL.md"
    fi
  done
  if [[ $found -eq 0 ]]; then
    fail "No skill directories found in ${SKILLS_DIR}"
  fi
fi

echo ""

# --- agents ------------------------------------------------------------------

echo "Agents (${AGENTS_DIR}):"
if [[ ! -d "$AGENTS_DIR" ]]; then
  fail "agents/ directory does not exist"
else
  found=0
  for agent_file in "${AGENTS_DIR}"/*.md; do
    [[ -f "$agent_file" ]] || continue
    name="$(basename "$agent_file")"
    ((found++)) || true
    content="$(cat "$agent_file")"
    has_name=false
    has_desc=false
    if echo "$content" | grep -q '^name:'; then has_name=true; fi
    if echo "$content" | grep -q '^description:'; then has_desc=true; fi

    if $has_name && $has_desc; then
      pass "${name}"
    elif ! $has_name && ! $has_desc; then
      fail "${name} — missing frontmatter 'name' and 'description'"
    elif ! $has_name; then
      fail "${name} — missing frontmatter 'name'"
    else
      fail "${name} — missing frontmatter 'description'"
    fi
  done
  if [[ $found -eq 0 ]]; then
    fail "No agent .md files found in ${AGENTS_DIR}"
  fi
fi

echo ""

# --- rules -------------------------------------------------------------------

echo "Rules (${RULES_DIR}):"
if [[ ! -d "$RULES_DIR" ]]; then
  echo "  INFO rules/ not installed (optional)"
else
  found=0
  for rule_file in "${RULES_DIR}"/*; do
    [[ -f "$rule_file" ]] || continue
    name="$(basename "$rule_file")"
    ((found++)) || true
    pass "${name}"
  done
  if [[ $found -eq 0 ]]; then
    echo "  INFO rules/ exists but is empty (optional)"
  fi
fi

echo ""
echo "----"
echo "Result: ${ok} OK, ${warn} warnings"

if [[ $warn -gt 0 ]]; then
  echo "Re-run 'bash scripts/install-global.sh copy' to fix missing files."
fi
