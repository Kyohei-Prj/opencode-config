---
description: Implement a task using test-first development.
agent: build
---

Goal:
Implement a task using test-first development.

Input:
$ARGUMENTS

Example:
/implement docs/tasks/ws1-task1.md

Steps:

1. Read:
- @docs/architecture.md
- @contracts/
- task file

2. Plan the implementation.

3. Write failing tests first.

Types of tests:
- unit tests
- contract tests

4. Implement feature.

5. Ensure all checks pass:

- tests
- lint
- type checks

6. Update documentation if necessary.

7. Commit changes.

Commit format:

feat(scope): description

Rules:
- do not modify unrelated code
- respect architecture boundaries
- follow contracts strictly
- use backend-engineer or frontend-engineer agent or implementation
- use test-engineer agent for testing
- use security-reviewer agent for security analysis
- use code-reviewer agent for overall code review
