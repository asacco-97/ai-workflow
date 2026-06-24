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

SENSITIVE_PATTERNS = re.compile(
    r"\.env|api[_-]?key|secret[_-]?key|private[_-]?key|password|passwd|token|credential|aws_access|aws_secret",
    re.IGNORECASE,
)

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

    for rule_file in sorted(rules_dir.iterdir()):
        if not rule_file.is_file():
            continue
        issues = []
        text = rule_file.read_text(errors="ignore")
        if SENSITIVE_PATTERNS.search(text):
            issues.append("possible sensitive reference (secret/token/key/credential)")
        results.append({"type": "rule", "name": rule_file.name, "issues": issues})

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
            print("Note: third_party/ not found, skipping.")

    all_results: list[dict] = []
    for root in roots:
        prefix = f"[third_party] " if root != REPO_ROOT else ""
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
