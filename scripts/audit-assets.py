#!/usr/bin/env python3
"""
Audit local skills, agents, and rules for completeness and safety issues.

Usage:
    python scripts/audit-assets.py
    python scripts/audit-assets.py --include-third-party
"""

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent

# Broad pattern for skills/agents (any mention of sensitive terms in code/config context)
SENSITIVE_PATTERNS = re.compile(
    r"\.env|api[_-]?key|secret[_-]?key|private[_-]?key|password|passwd|token|credential|aws_access|aws_secret",
    re.IGNORECASE,
)

# Narrow pattern for rule files: only flag actual assignments or literal values,
# not instructional text that discusses these concepts.
RULE_SENSITIVE_PATTERNS = re.compile(
    r'(?:api[_-]?key|secret[_-]?key|private[_-]?key|password|aws_access|aws_secret)\s*=\s*["\'][^"\']{4,}["\']',
    re.IGNORECASE,
)

RULE_MAX_LINES = 100

SUSPICIOUS_TOOLS = {"Bash", "Write", "Edit"}


def parse_frontmatter(text: str) -> dict:
    if not text.startswith("---"):
        return {}
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}
    fm: dict = {}
    for line in parts[1].splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip().strip('"').strip("'")
    return fm


def audit_skills(root: Path) -> list[dict]:
    results = []
    skills_dir = root / "skills"
    if not skills_dir.is_dir():
        return results

    for skill_dir in sorted(skills_dir.iterdir()):
        if not skill_dir.is_dir():
            continue
        skill_md = skill_dir / "SKILL.md"
        issues = []

        if not skill_md.exists():
            issues.append("missing SKILL.md")
            results.append({"type": "skill", "name": skill_dir.name, "issues": issues})
            continue

        text = skill_md.read_text(errors="ignore")
        fm = parse_frontmatter(text)

        if not fm:
            issues.append("missing frontmatter")
        else:
            if "name" not in fm:
                issues.append("frontmatter missing 'name'")
            if "description" not in fm:
                issues.append("frontmatter missing 'description'")

        if SENSITIVE_PATTERNS.search(text):
            issues.append("possible sensitive reference (secret/token/key/credential)")

        results.append({
            "type": "skill",
            "name": skill_dir.name,
            "issues": issues,
            "fm": fm,
        })

    return results


def audit_agents(root: Path) -> list[dict]:
    results = []
    agents_dir = root / "agents"
    if not agents_dir.is_dir():
        return results

    for agent_file in sorted(agents_dir.glob("*.md")):
        issues = []
        text = agent_file.read_text(errors="ignore")
        fm = parse_frontmatter(text)

        if not fm:
            issues.append("missing frontmatter")
        else:
            if "name" not in fm:
                issues.append("frontmatter missing 'name'")
            if "description" not in fm:
                issues.append("frontmatter missing 'description'")

            tools_raw = fm.get("tools", "")
            tools = {t.strip() for t in tools_raw.split(",") if t.strip()}
            flagged = tools & SUSPICIOUS_TOOLS
            if flagged:
                issues.append(f"has write/execute tools: {', '.join(sorted(flagged))}")

        if SENSITIVE_PATTERNS.search(text):
            issues.append("possible sensitive reference (secret/token/key/credential)")

        results.append({
            "type": "agent",
            "name": agent_file.stem,
            "issues": issues,
            "fm": fm,
        })

    return results


def audit_rules(root: Path) -> list[dict]:
    results = []
    rules_dir = root / "rules"
    if not rules_dir.is_dir():
        return results

    # Collect all rule files with their relative paths
    rule_files = sorted(rules_dir.rglob("*.md"))
    if not rule_files:
        return results

    # First pass: gather content and per-file issues, collect headings for dup detection
    heading_index: dict[str, list[str]] = {}  # normalized heading → [rel paths]
    file_data: list[tuple[str, list]] = []

    for rule_file in rule_files:
        rel = str(rule_file.relative_to(rules_dir))
        issues: list[str] = []
        text = rule_file.read_text(errors="ignore")

        # Narrow sensitive-content check (rules discuss these topics by design)
        if RULE_SENSITIVE_PATTERNS.search(text):
            issues.append("possible literal credential assignment")

        # Line length check
        lines = text.splitlines()
        if len(lines) > RULE_MAX_LINES:
            issues.append(f"long rule file ({len(lines)} lines; consider splitting at {RULE_MAX_LINES})")

        # Collect headings for cross-file duplicate detection
        headings = re.findall(r"^#{1,3}\s+(.+)$", text, re.MULTILINE)
        for h in headings:
            normalized = h.strip().lower()
            heading_index.setdefault(normalized, []).append(rel)

        file_data.append((rel, issues))

    # Second pass: flag files that share a heading with another file
    for rel, issues in file_data:
        for heading, locations in heading_index.items():
            if rel in locations and len(locations) > 1:
                others = ", ".join(loc for loc in locations if loc != rel)
                issues.append(f"heading '{heading}' also appears in: {others}")

    for rel, issues in file_data:
        results.append({"type": "rule", "name": rel, "issues": issues})

    return results


def print_table(results: list[dict]) -> int:
    col_type = max(len(r["type"]) for r in results) if results else 5
    col_name = max(len(r["name"]) for r in results) if results else 4

    header = f"{'TYPE':<{col_type}}  {'NAME':<{col_name}}  STATUS"
    print(header)
    print("-" * len(header))

    total_issues = 0
    for r in results:
        status = "OK" if not r["issues"] else "WARN: " + "; ".join(r["issues"])
        print(f"{r['type']:<{col_type}}  {r['name']:<{col_name}}  {status}")
        total_issues += len(r["issues"])

    return total_issues


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit local Claude Code assets.")
    parser.add_argument(
        "--include-third-party",
        action="store_true",
        help="Also scan third_party/ (read-only reference; issues are informational only)",
    )
    args = parser.parse_args()

    roots = [REPO_ROOT]
    if args.include_third_party:
        tp = REPO_ROOT / "third_party"
        if tp.is_dir():
            roots.append(tp)
        else:
            print("Note: third_party/ not found (submodule not initialized), skipping.")

    all_results: list[dict] = []
    for root in roots:
        prefix = "[third_party] " if root != REPO_ROOT else ""
        skills = audit_skills(root)
        for r in skills:
            r["name"] = prefix + r["name"]
        agents = audit_agents(root)
        for r in agents:
            r["name"] = prefix + r["name"]
        rules = audit_rules(root)
        for r in rules:
            r["name"] = prefix + r["name"]
        all_results.extend(skills + agents + rules)

    if not all_results:
        print("No assets found to audit.")
        sys.exit(0)

    total_issues = print_table(all_results)

    ok_count = sum(1 for r in all_results if not r["issues"])
    warn_count = sum(1 for r in all_results if r["issues"])

    print()
    print(f"Total: {len(all_results)} assets — {ok_count} OK, {warn_count} with warnings")

    if total_issues > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
