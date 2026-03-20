---
name: tdd-cycle
description: Implement a task using red-green-refactor-evidence. Write a failing test first, implement the minimum to pass, refactor without changing behaviour, then capture the run log. Each phase has a distinct exit condition. Stop and raise a blocker rather than working around any obstacle silently.
compatibility: opencode
metadata:
  used-by: tdd-builder
  load-at: agent definition time
---

## What I do

Define the red → green → refactor → evidence loop used to implement each task. Every task must produce a passing test suite and a completed run log before it is considered done.

## The loop

```
red → green → refactor → evidence
```

Each phase has a distinct goal and exit condition. None are optional.

## Test Code Format

When writing a test code, follow Arrange-Act-Assert (AAA) pattern where possible.
Example:
```python
def test_example() -> None:
    """Description of the test."""

    # Arrange
	input_value = 5
	expected = 10
	
	# Act
	actual = example(input_value)
	
	# Assert
	assert expected == actual
```

## Phase 1 — Red

**Goal:** Write a failing test that precisely describes the acceptance criterion being implemented.

### Procedure

1. Read the task's `acceptance_criteria` from the manifest.
2. For each criterion, write the minimum test that would pass if and only if that criterion is met.
3. Run the tests. Confirm they fail for the right reason — not a compile error, not a missing import, but a logical failure that the implementation will fix.
4. If a test fails for the wrong reason (import error, syntax error, missing fixture), fix the test infrastructure first. Do not proceed to green with a test that fails for the wrong reason.

### What makes a good red test

- Tests one thing. One assertion or one logical group of related assertions.
- Fails with a message that names what's missing ("expected token to be signed with RS256, got HS256").
- Does not test implementation details — tests the contract (inputs → outputs, side effects).
- Uses real types and interfaces where they exist. Stubs and mocks are acceptable for external dependencies (network, filesystem, clock) but not for in-process logic.

### Exit condition

At least one failing test per acceptance criterion. Record test names and failure messages in the run log under "Red — test written".

## Phase 2 — Green

**Goal:** Write the minimum implementation to make the failing tests pass. Nothing more.

### Procedure

1. Implement only what is needed to satisfy the failing tests.
2. Do not add error handling, logging, configuration, or features not covered by a test. These come in refactor or in a later task.
3. Run the full test suite — not just the new tests. No regressions allowed.
4. If a regression is introduced, fix it before moving to refactor.

### Discipline

Green phase is about correctness, not cleanliness. The code is allowed to be ugly. The only requirement is that the tests pass.

**Do not:**
- Add untested behaviour "while you're in here"
- Refactor existing code in the same commit as making tests pass
- Leave tests skipped or marked as pending

### Exit condition

All new tests pass. No existing tests regressed. Record the summary test output in the run log under "Green — implementation".

## Phase 3 — Refactor

**Goal:** Improve the structure of the code without changing its behaviour.

### Procedure

1. Re-read the green implementation with fresh eyes.
2. Identify: duplication, unclear naming, violation of project conventions, unnecessary complexity.
3. Refactor one concern at a time. Run tests after each change.
4. If refactoring reveals a missing test (behaviour that was implicitly assumed), write the test first — you've found a red phase that was missed.

### What counts as refactor

- Rename variables, functions, or types for clarity
- Extract a well-named helper function
- Consolidate duplicated logic
- Align with project conventions (naming, file structure, import style)
- Remove dead code introduced during green

### What does not count as refactor (do these in a separate task)

- Adding new behaviour
- Changing error handling strategy
- Changing the public interface of a component
- Performance optimisation (unless a test covers it)

### When to skip

If the green implementation is already clean — genuinely, not as an excuse — record "none" in the run log and move on. Forced refactoring for its own sake is waste.

### Exit condition

Tests still pass. Run log updated under "Refactor". Code meets project conventions.

## Phase 4 — Evidence

**Goal:** Capture the run log and update the manifest before moving to the next task.

### Procedure

1. Write the complete run log to `workflow/<feature>/runs/<run-id>.md` using the `evidence-log-writer` format skill.
2. Update the task's `phase` in `feature.yaml` from `implementing` to `reviewing`.
3. Signal the task-reviewer that this task is ready for review.

Do not mark a task `done` — that is the task-reviewer's responsibility after review passes.

## Handling blockers mid-task

If a blocker is discovered during implementation (missing dependency, design ambiguity, unexpected coupling):

1. **Stop.** Do not work around the blocker silently.
2. Record the blocker in `execution.blockers` in the manifest.
3. Set the task `phase` to `implementing` (unchanged — the task is not complete).
4. Note the blocker in the run log under "Notes".
5. Surface it to the build-orchestrator for resolution before continuing.

## Scope discipline

Work only within the slice's `context.files_touched`. Files outside this list should not be modified unless:
- A bug in an adjacent file is directly blocking a test from passing
- The change is a one-line fix with no design implications

If a larger change to an out-of-scope file is needed, raise it as a blocker rather than expanding scope silently.

## Lane adjustments

| Lane | Red phase | Refactor phase |
|---|---|---|
| small | 1–2 tests per task, lightweight | Optional — use judgment |
| standard | Full coverage of acceptance criteria | Required unless green is already clean |
| epic | Full coverage + edge cases + contract tests for interfaces_produced | Required, with explicit convention alignment |

## Task phase transitions

```
planned
  → implementing   (tdd-builder picks up the task)
  → reviewing      (red/green/refactor complete, evidence written)
  → done           (task-reviewer approves)
  → implementing   (task-reviewer rejects — builder retries)
```

The builder only transitions `planned → implementing` and `implementing → reviewing`. The reviewer transitions `reviewing → done` or `reviewing → implementing`.
