---
description: Convert workstreams into executable development tasks.
agent: build
---

Goal:
Convert workstreams into executable development tasks.

Inputs:
- @docs/workstreams.md
- @docs/architecture.md
- @contracts/

Steps:

1. For each workstream create tasks.

2. Each task must contain:

- description
- acceptance criteria
- dependencies
- test strategy

3. Store tasks in:

docs/tasks/

File naming:

ws1-task1.md
ws1-task2.md

Example task structure:

Task: Implement login endpoint

Description:
Create API endpoint for user login.

Dependencies:
auth service
database schema

Acceptance Criteria:
- endpoint matches OpenAPI spec
- unit tests pass
- authentication token returned

Test Strategy:
- unit tests
- contract tests

Definition of Done:
- tests passing
- lint passing
- code committed
