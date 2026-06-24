---
globs: tests/**/*.py
description: Testing rules for test files.
---

# Testing

- Unit tests must not hit the network, a real database, or the filesystem by default. Use fixtures and mocks for external dependencies.
- Integration tests that hit real infrastructure must be marked `@pytest.mark.integration` and excluded from the default test run.
- Each test function tests one logical behavior. Do not put multiple unrelated assertions in one test.
- Test names describe the behavior being tested: `test_missing_target_column_raises_value_error`, not `test_pipeline_1`.
- Do not test private methods directly. Test through the public interface.
- Write the test before the fix when resolving a bug. The failing test is the reproduction case.
