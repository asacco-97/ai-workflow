#!/usr/bin/env python3
"""SessionStart hook: inject a context briefing into Claude's context.

Reads the hook JSON payload from stdin and prints a structured context block
to stdout. Claude Code injects stdout into the session context on exit 0.

Memory location is resolved relative to this script's own `.claude` directory
(``<.claude>/hooks/session_start.py`` -> ``<.claude>/memory``), so the same
file works whether installed globally (``~/.claude``) or into a project's
``.claude`` directory.

Defensive by design: any failure falls back to printing just the date line
and exiting 0, so the hook can never block or break a session start.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path


def memory_dir():
    """Resolve the memory directory relative to this script's .claude parent."""
    # <.claude>/hooks/session_start.py -> parent.parent == <.claude>
    claude_dir = Path(__file__).resolve().parent.parent
    return claude_dir / "memory"


def read_file_lines(path, max_lines):
    """Return up to max_lines of a file's contents, or None if unavailable."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            lines = f.read().splitlines()
        if len(lines) > max_lines:
            lines = lines[:max_lines] + ["... (truncated)"]
        return "\n".join(lines)
    except Exception:
        return None


def main():
    # Read and parse the payload; tolerate empty or malformed input.
    try:
        raw = sys.stdin.read()
        payload = json.loads(raw) if raw.strip() else {}
    except Exception:
        payload = {}

    source = payload.get("source", "unknown")
    cwd = payload.get("cwd", os.getcwd())
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    mem = memory_dir()
    priorities = read_file_lines(mem / "priorities.md", 40)
    questions = read_file_lines(mem / "open-questions.md", 20)

    lines = []
    lines.append("--- session context ---")
    lines.append(f"Date/time: {now}")
    lines.append(f"Working directory: {cwd}")
    lines.append(f"Session source: {source}")

    if priorities:
        lines.append("")
        lines.append(f"## Priorities ({mem / 'priorities.md'})")
        lines.append(priorities)

    if questions:
        lines.append("")
        lines.append(f"## Open Questions ({mem / 'open-questions.md'})")
        lines.append(questions)

    if not priorities and not questions:
        lines.append("")
        lines.append("(No personal memory files found yet.)")

    lines.append("")
    lines.append("--- end session context ---")

    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        # Last-resort fallback: never hard-fail.
        try:
            print(f"--- session context ---\nDate/time: "
                  f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                  f"--- end session context ---")
        except Exception:
            pass
        sys.exit(0)
