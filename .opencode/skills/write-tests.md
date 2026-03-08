---
name: write-tests
description: Create consistent releases and changelogs
---

Purpose:
Generate high-quality tests before implementing functionality.

Used By:
- backend-engineer
- frontend-engineer
- test-engineer

When To Use:
Before implementing a new feature or bug fix.

Inputs:
- task specification
- architecture documentation
- relevant source code

Steps:

1. Identify behaviors that must be tested.

2. Create tests for:

Happy path
- expected successful behavior

Edge cases
- empty inputs
- boundary values

Failure cases
- invalid input
- service failure
- authorization failure

3. Write tests before implementation.

4. Ensure tests fail initially.

Test Types:

Unit tests
- test business logic in isolation

Integration tests
- verify interaction between components

Contract tests
- verify API responses match schema

Test Quality Rules:
- deterministic
- isolated
- readable
- minimal mocking

Output:
Test files ready to run in the project test framework.
