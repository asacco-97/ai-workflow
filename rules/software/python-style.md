---
globs: src/**/*.py, tests/**/*.py, scripts/**/*.py
description: Python style rules for source, test, and script files.
---

# Python style

- Type-annotate all function signatures. No `def foo(x):` without types.
- Use `pathlib.Path` for file paths. No `os.path.join`.
- Do not use mutable default arguments.
- Prefer explicit returns over side-effect-only functions when the result is meaningful.
- No commented-out code blocks. Remove dead code or use a feature branch.
- One logical operation per line — do not chain assignments with side effects.
- Match existing style in the file you are editing. Do not reformat surrounding code unless asked.
