#!/usr/bin/env python3
"""PreToolUse hook for Bash: block destructive/risky commands.

Reads the hook JSON payload from stdin. For Bash tool calls, checks the command
against an ordered blocklist of risky regex patterns. On a match, writes an
explanation to stderr and exits 2 (Claude Code blocks the call and shows the
feedback). Otherwise exits 0 silently.

Fail-open: any parse error exits 0 so the hook never blocks Claude on a bug.
"""

import json
import re
import sys

# Ordered (pattern, human-readable description) blocklist. Case-insensitive.
BLOCKLIST = [
    (r"rm\s+-rf\s+[~/]", "recursive delete targeting home or root"),
    (r"rm\s+-rf\s+\*", "recursive delete with glob"),
    (r"chmod\s+-R\s+777", "world-writable recursive chmod"),
    (r">\s*/etc/", "overwrite to /etc"),
    (r"dd\s+.*of=/dev/", "dd to a block device"),
    (r"curl\s+.*\|\s*(bash|sh|python)", "piped remote execution (curl)"),
    (r"wget\s+.*\|\s*(bash|sh|python)", "piped remote execution (wget)"),
    (r":\(\)\s*\{.*\}", "fork bomb pattern"),
]


def main():
    try:
        raw = sys.stdin.read()
        payload = json.loads(raw) if raw.strip() else {}
    except Exception:
        # Fail open — don't block on a parse error.
        return 0

    if payload.get("tool_name") != "Bash":
        return 0

    command = payload.get("tool_input", {}).get("command", "")
    if not command:
        return 0

    for pattern, description in BLOCKLIST:
        if re.search(pattern, command, re.IGNORECASE):
            sys.stderr.write(
                f"Blocked by pre_tool_use hook: {description}.\n"
                f"Matched pattern: {pattern}\n"
                f"Command: {command}\n"
                f"If this is intentional, run it manually or rephrase the command."
            )
            return 2

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        # Fail open on any unexpected error.
        sys.exit(0)
