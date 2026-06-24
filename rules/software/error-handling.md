---
globs: src/**/*.py, scripts/**/*.py
description: Error handling rules for source and script files.
---

# Error handling

- Validate at system boundaries: user input, external API responses, file reads, and database queries. Do not validate internal function calls between your own modules.
- Raise specific exceptions (`ValueError`, `KeyError`, `RuntimeError`) with a message that names what was wrong and what was expected.
- Do not catch broad `Exception` unless you are at a top-level entry point and intend to log-and-exit. Never silence exceptions with `except: pass`.
- Do not add error handling for scenarios that cannot occur given the code's invariants.
- Log errors at the point of detection, not at the point of catch.
