---
description: Review code changes for correctness, maintainability, tests, and risk. Use when asked to review a diff, PR, implementation, or recent code changes.
---

# Code Review Skill

Review the code like a senior engineer and data scientist.

## Process

1. Inspect the changed files and surrounding context.
2. Identify correctness issues first.
3. Identify maintainability, style, and architecture issues.
4. Check whether tests should be added or updated.
5. Flag risky assumptions and edge cases.
6. Avoid nitpicks unless they materially improve quality.

## Output format

Use this structure:

## Summary

Briefly state whether the change is safe, risky, or needs revision.

## Blocking issues

List issues that should be fixed before merging.

## Non-blocking improvements

List worthwhile improvements that are not required.

## Tests to add

Suggest concrete tests.

## Suggested patch

Only include code when the fix is clear.
