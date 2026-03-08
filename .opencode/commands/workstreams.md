---
description: Break the architecture into parallel workstreams.
agent: build
---

Goal:
Break the architecture into parallel workstreams.

Inputs:
- @docs/architecture.md

Steps:

1. Identify major subsystems.

2. Convert them into workstreams.

Example:

WS1 – API
WS2 – Authentication
WS3 – Database
WS4 – Frontend
WS5 – Infrastructure

3. Define dependencies between workstreams.

4. Create milestone roadmap.

Example:

Milestone 1:
Vertical slice working

Milestone 2:
Core API complete

Milestone 3:
Feature complete

5. Save documentation.

Output:

docs/workstreams.md

Structure:

# Workstreams

## WS1
Objective
Dependencies
Interfaces used

## WS2
...

# Milestones

Rules:
- Prefer loosely coupled workstreams.
- Minimize dependencies.
