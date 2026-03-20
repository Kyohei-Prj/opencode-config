---
name: evidence-log-writer
description: Write workflow/<feature>/runs/<run-id>.md for one task execution. Defines the run ID format, the red/green/refactor/notes template, and six writing rules including mandatory red section, checkbox state at completion, and one log per execution (never overwrite on retry).
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

## Template

```markdown
# Run: <run-id>

**Feature:** <feature.slug>
**Slice:** <slice-slug>
**Task:** <task-id> — <task.title>
**Status:** pass | fail | skip
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

## TDD cycle

### Red — test written

```
<test file path>
<test function name(s)>
<brief description of what the test asserts>
```

**Result:** <failing output summary — error type and message, no full stack trace>

---

### Green — implementation

```
<file(s) modified>
<summary of changes in 1–3 sentences>
```

**Result:** <passing output summary — number of tests passed>

---

### Refactor

```
<file(s) touched>
<summary of refactor in 1–2 sentences, or "none">
```

**Result:** <passing output summary after refactor, or "unchanged">

---

## Final test output

```
<last test run output — pass/fail counts, duration>
```

---

## Notes

<any blockers encountered, decisions made mid-task, deviations from the plan, or "none">

---

*Evidence log — read only. Execution state of record is in feature.yaml.*
```

## Writing rules

1. **Create the file at task start** with `status: in progress` and `Completed: in progress`. Update status and completed timestamp when the task finishes.
2. **Red section is required.** A task is not considered started until at least one failing test is recorded. If the task has no testable output (e.g. a pure configuration change), note that explicitly and skip the TDD cycle section.
3. **Acceptance criteria checkboxes** reflect the state at task completion — `[x]` for met, `[ ]` for unmet. A task with unmet acceptance criteria must have `status: fail`.
4. **Keep outputs brief.** Truncate test output to the summary line (e.g. `5 passed, 0 failed in 0.42s`). Do not paste full stack traces.
5. **Notes section is mandatory** — write "none" if there is truly nothing to record. Silence is ambiguous.
6. **One run log per task execution.** If a task is retried, create a new run log with a new run ID. Do not overwrite the previous log.
