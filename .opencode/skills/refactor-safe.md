---
name: refactor-safe
description: Refactor code safely without changing behavior.
---

Purpose:
Refactor code safely without changing behavior.

Used By:
- backend-engineer
- frontend-engineer
- code-reviewer

When To Use:
- improving readability
- reducing duplication
- restructuring modules

Steps:

1. Identify target code.

2. Verify tests exist for the functionality.

If tests do not exist:
- create tests first using write-tests skill.

3. Refactor incrementally.

Examples:

- extract functions
- rename variables
- simplify conditionals
- modularize code

4. Run tests after each change.

5. Confirm behavior remains unchanged.

Rules:

- no logic changes
- small incremental commits
- maintain API compatibility
