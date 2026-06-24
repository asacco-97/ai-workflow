from pathlib import Path
import re
import json

ROOTS = [
    Path("third_party/anthropic-skills"),
    Path("third_party/awesome-claude-skills"),
]

def parse_frontmatter(text: str):
    if not text.startswith("---"):
        return {}
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}
    fm = parts[1]
    out = {}
    for line in fm.splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            out[k.strip()] = v.strip().strip('"').strip("'")
    return out

items = []
for root in ROOTS:
    for path in root.rglob("SKILL.md"):
        text = path.read_text(errors="ignore")
        fm = parse_frontmatter(text)
        items.append({
            "path": str(path),
            "name": fm.get("name", path.parent.name),
            "description": fm.get("description", ""),
            "has_allowed_tools": "allowed-tools" in text,
            "has_scripts": (path.parent / "scripts").exists(),
            "line_count": len(text.splitlines()),
        })

Path("third_party_skill_inventory.json").write_text(json.dumps(items, indent=2))
print(f"Wrote {len(items)} skills to third_party_skill_inventory.json")
