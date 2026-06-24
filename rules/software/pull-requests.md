---
description: Rules for preparing and reviewing pull requests.
---

# Pull requests

Before opening a PR:
- Run `security-privacy-reviewer` and resolve any blockers.
- Run `/review-own-branch` and address issues before requesting review.
- Confirm the diff contains only changes related to the stated purpose. Unrelated cleanup belongs in a separate PR.

PR descriptions must include:
- What changed and why (not just what).
- How to test the change.
- Any modeling or data assumptions that reviewers need to know.

Do not merge a PR that changes model logic without a validation summary attached.
