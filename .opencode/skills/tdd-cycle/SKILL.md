---
name: tdd-cycle
description: Classify each task into one of three implementation strategies — full TDD, verify-after, or no-test — then execute the appropriate procedure. Prevents wasteful test-writing for scaffolding, dependency installation, and boilerplate while preserving rigorous TDD for all business logic and behaviour.
compatibility: opencode
metadata:
  used-by: tdd-builder
  load-at: agent definition time
---

## What I do

Define how to implement each task by first classifying it, then executing the right procedure for that class. Not every task warrants a failing test written before the code. The classification step is mandatory — skip it and you will either write useless tests for scaffolding or miss tests for real logic.

## Phase 0 — Classify the task

Read the task `description` and `acceptance_criteria` before writing a single line of code. Apply this decision tree:

**Does the task have verifiable behaviour?**
Behaviour means: outputs that could be wrong, state transitions that could fail, contracts that could be violated, error conditions that could be missed.

Examples of behaviour: "token is signed with RS256", "returns 401 when unauthenticated", "calculates total including tax", "rejects duplicate email on registration".

→ If yes: **Strategy 1 — Full TDD**

**Or is the task primarily wiring, configuration, or integration plumbing?**
Wiring means: connecting existing pieces, mounting routes, registering middleware, configuring a library, bootstrapping a service. The output is structural or connective, not behavioural. Writing a test first is impractical because the thing being tested can't exist until the wiring is in place.

Examples: "mount the auth router at /api/v1/auth", "initialise the logger with the config from env", "register the email service with the DI container", "connect the database pool on startup".

→ If yes: **Strategy 2 — Verify-after**

**Or is the task pure scaffolding with no logic?**
Scaffolding means: creating directory structures, installing packages, generating boilerplate files, writing configuration files that have no runtime logic, creating a README or changelog entry.

The distinguishing question: *would a test for this catch a real bug, or would it just assert that a script ran?* If the latter, no test is needed.

Examples: "create the src/auth/ directory structure", "install jest and ts-jest", "add express app boilerplate to app.ts", "create .env.example with documented variables", "add eslint config".

→ If yes: **Strategy 3 — No test**

**When in doubt:**
- Between Strategy 1 and 2 → use Strategy 1
- Between Strategy 2 and 3 → use Strategy 2
- Strategy 3 requires that acceptance criteria describe *existence or presence*, not *behaviour*

Record the chosen strategy and rationale in the run log under "Strategy". The task-reviewer validates this choice.

---

## Strategy 1 — Full TDD

For tasks with verifiable behaviour. This is the default for all business logic, domain rules, API handlers, validation, data transformations, and state transitions.

### Red

1. Read `acceptance_criteria` from the manifest.
2. For each criterion, write the minimum test that passes if and only if that criterion is met.
3. Run the tests. Confirm they fail for the right reason — a logical failure, not a compile error or missing import. Fix test infrastructure issues before proceeding.

**What makes a good red test:**
- Tests one thing — one assertion or one logical group
- Fails with a message naming what's missing ("expected RS256, got HS256")
- Tests the contract (inputs → outputs, side effects), not implementation details
- Uses real types and interfaces where they exist; stubs only for external dependencies (network, filesystem, clock)

Exit: at least one failing test per acceptance criterion. Record test names and failure messages in the run log.

### Green

1. Implement only what is needed to make the failing tests pass. Nothing more.
2. Do not add error handling, logging, or features not covered by a test.
3. Run the full test suite — no regressions allowed.

Exit: all new tests pass, no regressions. Record summary test output in the run log.

### Refactor

1. Re-read the implementation. Identify: duplication, unclear naming, convention violations.
2. Refactor one concern at a time, running tests after each change.
3. If refactoring reveals a missing test, write it first.

Skip only if the green implementation is genuinely already clean — record "none" explicitly.

Exit: tests still pass, code meets project conventions.

---

## Strategy 2 — Verify-after

For wiring, configuration, and integration plumbing where writing a test first is impractical.

### Implement

Write the wiring code directly. Follow existing patterns in the codebase for how similar connections are made.

### Verify

Write a lightweight smoke or integration test that confirms the wiring is observable:
- A server that starts without error and responds to a health check
- A module that imports and exposes the expected exports
- A database pool that connects and executes a trivial query
- A middleware that passes a request through the correct handler chain

The test must be meaningful — it should fail if the wiring is broken. A test that always passes regardless of the implementation is not a verify-after test; it is a useless test. If you cannot write a test that would catch a real misconfiguration, use Strategy 3 instead.

### Refactor

Same as Strategy 1's refactor phase.

Exit: smoke test passes, wiring is confirmed, code is clean.

---

## Strategy 3 — No test

For pure scaffolding with no verifiable logic.

### Implement

Create the directories, install the packages, generate the boilerplate, write the config files. Follow project conventions.

### Document

In the run log Notes section, write:
- What was created or installed
- Why no test was written (reference the classification: acceptance criteria describe existence/presence, not behaviour)
- Any decisions made (e.g. version pinned, directory layout chosen)

This documentation is mandatory. An empty Notes section for a Strategy 3 task is a run log failure.

Exit: task is done, Notes are complete. No test output — the run log records "Strategy 3 — no test" in place of the TDD cycle section.

---

## Phase 4 — Evidence (all strategies)

1. Write the complete run log using the `evidence-log-writer` skill. The TDD cycle section format depends on strategy — see that skill for the conditional template.
2. Update the task `phase` from `implementing` to `reviewing`.
3. Report to build-orchestrator.

---

## Handling blockers (all strategies)

If a blocker is discovered during implementation:

1. Stop — do not work around it silently.
2. Record in `execution.blockers`.
3. Note in the run log under Notes.
4. Update run history status to `blocked`.
5. Surface to build-orchestrator. Do not advance the task phase.

---

## Scope discipline (all strategies)

Work only within `context.files_touched`. If a file outside this list must be modified, record it in the run log and flag it for the task-reviewer. Never silently expand scope.

---

## Lane adjustments

| Lane | Strategy 1 red phase | Strategy 1 refactor | Strategy 2 verify test |
|---|---|---|---|
| small | 1–2 tests per criterion, lightweight | Optional | Smoke test only |
| standard | Full criterion coverage | Required unless already clean | Meaningful integration test |
| epic | Full coverage + edge cases + contract tests for interfaces_produced | Required, convention-aligned | Full integration test |

---

## Task phase transitions

```
planned
  → implementing   (tdd-builder picks up the task)
  → reviewing      (implementation complete, evidence written)
  → done           (task-reviewer approves)
  → implementing   (task-reviewer rejects — builder retries)
```
