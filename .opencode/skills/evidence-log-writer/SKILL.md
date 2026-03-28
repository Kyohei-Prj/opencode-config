---
name: evidence-log-writer
description: Write workflow/<feature>/runs/<run-id>.md for one task execution. Defines the run ID format and a strategy-conditional template — the TDD cycle section differs for full TDD, verify-after, and no-test tasks. One log per execution; retries get a new log.
compatibility: opencode
metadata:
  used-by: tdd-builder
  load-at: output-write time
---

## Core rule

Run logs are generated evidence. They are read-only views. The canonical execution state lives in `feature.yaml` under `execution.run_history`. If a run log disagrees with the manifest, the manifest wins.

## Run ID format

```
<slice-slug>-<task-id>-<YYYYMMDD>-<HHMMSS>
```

Example: `auth-token-task-001-20260318-143022`

The run ID is used as both the filename (`<run-id>.md`) and the `run_id` field in `execution.run_history`.

---

## Template — Strategy 1 (Full TDD)

```markdown
# Run: <run-id>

**Feature:** <feature.slug>
**Slice:** <slice-slug>
**Task:** <task-id> — <task.title>
**Strategy:** Full TDD
**Status:** pass | fail
**Started:** <ISO 8601 timestamp>
**Completed:** <ISO 8601 timestamp | in progress>

---

## Task description

<task.description>

## Acceptance criteria

<for each criterion>
- [x or space] <criterion>
</for each>

---

## Strategy rationale

<one sentence explaining why Full TDD was chosen — what verifiable behaviour this task has>

---

## TDD cycle

### Red — test written

<test file path>
<test function name(s)>
<brief description of what the test asserts>

**Result:** <failing output summary — error type and message, no full stack trace>

### Green — implementation

<file(s) modified>
<summary of changes in 1–3 sentences>

**Result:** <passing output summary — number of tests passed>

### Refactor

<file(s) touched and summary, or "none">

**Result:** <passing output summary after refactor, or "unchanged">

---

## Final test output

<last test run output — pass/fail counts, duration>

---

## Notes

<blockers, scope deviations, mid-task decisions, or "none">

---

*Evidence log — read only. Execution state of record is in feature.yaml.*
```

---

## Template — Strategy 2 (Verify-after)

```markdown
# Run: <run-id>

**Feature:** <feature.slug>
**Slice:** <slice-slug>
**Task:** <task-id> — <task.title>
**Strategy:** Verify-after
**Status:** pass | fail
**Started:** <ISO 8601 timestamp>
**Completed:** <ISO 8601 timestamp | in progress>

---

## Task description

<task.description>

## Acceptance criteria

<for each criterion>
- [x or space] <criterion>
</for each>

---

## Strategy rationale

<one sentence explaining why Verify-after was chosen — what makes this wiring/plumbing rather than testable behaviour>

---

## Implementation

<file(s) created or modified>
<summary of wiring in 1–3 sentences>

## Verification

<test file path>
<test function name(s)>
<what the smoke/integration test confirms>

**Result:** <passing output summary>

## Refactor

<file(s) touched and summary, or "none">

---

## Final test output

<last test run output — pass/fail counts, duration>

---

## Notes

<blockers, scope deviations, mid-task decisions, or "none">

---

*Evidence log — read only. Execution state of record is in feature.yaml.*
```

---

## Template — Strategy 3 (No test)

```markdown
# Run: <run-id>

**Feature:** <feature.slug>
**Slice:** <slice-slug>
**Task:** <task-id> — <task.title>
**Strategy:** No test
**Status:** pass
**Started:** <ISO 8601 timestamp>
**Completed:** <ISO 8601 timestamp>

---

## Task description

<task.description>

## Acceptance criteria

<for each criterion>
- [x] <criterion>
</for each>

---

## Strategy rationale

<one sentence explaining why No test was chosen — confirm acceptance criteria describe existence/presence, not behaviour>

---

## Implementation

<what was created or installed, file by file or action by action>

---

## Notes

<decisions made: versions pinned, layout choices, config values selected, or "none">
<No test was written: acceptance criteria describe [existence/presence], not verifiable behaviour>

---

*Evidence log — read only. Execution state of record is in feature.yaml.*
```

---

## Writing rules

1. **Create the file at task start** with `status: in progress` and `Completed: in progress`. Update both when the task finishes.
2. **Strategy header is required** — every run log must declare its strategy (`Full TDD`, `Verify-after`, or `No test`) in the frontmatter and include a one-sentence rationale. Missing strategy is a run log failure.
3. **Strategy 3 tasks always have `status: pass`** — there is no fail state for a scaffolding task unless the implementation was not completed.
4. **Acceptance criteria checkboxes** reflect the state at task completion — `[x]` for met, `[ ]` for unmet. A Strategy 1 or 2 task with unmet criteria must have `status: fail`.
5. **Keep outputs brief.** Truncate test output to the summary line (`5 passed, 0 failed in 0.42s`). No full stack traces.
6. **Notes section is mandatory** — write "none" if there is truly nothing to record. For Strategy 3, Notes must include the no-test justification sentence.
7. **One run log per task execution.** If a task is retried, create a new run log with a new run ID. Never overwrite.
