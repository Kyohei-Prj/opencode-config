---
description: Perform an automated code review.
agent: build
---

Goal:
Perform an automated code review.

Inputs:
- current git diff

Checks:

1. Architecture compliance
2. Security vulnerabilities
3. Code complexity
4. Test coverage
5. Documentation updates

Security checks:
- injection vulnerabilities
- secrets exposure
- insecure authentication

Output:

Review report containing:

- issues
- severity
- suggested fixes

Rules:
- prioritize correctness
- flag architecture violations
- suggest refactoring opportunities
