---
description: Rules for refactoring existing code.
---

# Refactoring

- Refactor only what is necessary for the current task. Do not improve adjacent code that is not broken.
- Confirm tests pass before and after the refactor. If tests do not exist, write them first.
- Match the existing abstraction level. Do not introduce new abstractions for code that is called in one place.
- Remove only the dead code your refactor creates (unused imports, variables, functions). Leave pre-existing dead code for a dedicated cleanup PR.
- Do not change behavior during a refactor. If behavior must change, that is a feature change — separate it.
