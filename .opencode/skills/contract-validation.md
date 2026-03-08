---
name: contract-validation
description: Ensure implementations comply with defined API contracts.
---

Purpose:
Ensure implementations comply with defined API contracts.

Used By:
- backend-engineer
- test-engineer
- code-reviewer

Inputs:
- contracts/openapi.yaml
- contracts/events.yaml
- API implementation code

Steps:

1. Parse API schema.

2. Verify endpoints:

- route paths
- HTTP methods
- request parameters
- response schemas

3. Validate:

- required fields
- data types
- error responses

4. Ensure documentation and implementation match.

Common Issues To Detect:

- missing fields
- incorrect status codes
- schema mismatch
- undocumented endpoints

Output:

Validation report:

PASS
or

FAIL with list of violations.
