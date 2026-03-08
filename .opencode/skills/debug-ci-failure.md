---
name: debug-ci-failure
description: Diagnose CI pipeline failures.
---

Purpose:
Diagnose CI pipeline failures.

Used By:
- code-reviewer
- backend-engineer
- test-engineer

Inputs:
- CI logs
- failing test output
- recent code changes

Steps:

1. Identify failing stage:

- build
- lint
- test
- integration test

2. Analyze error message.

3. Locate relevant code changes.

4. Determine root cause.

Common Causes:

- missing dependency
- incorrect environment variable
- test flakiness
- schema mismatch

5. Suggest minimal fix.

Output:

Root Cause
Fix Recommendation
Affected Files
