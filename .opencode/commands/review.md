---
description: "Review implemented code for a feature phase against its task specs, TDD quality, and architecture conformance. Usage: /review <feature> <phase-number>"
agent: review-orchestrator
subtask: true
---

You are starting the code review stage for a completed feature phase.

Arguments: $ARGUMENTS
(Expected format: `<feature-slug> <phase-number>` — e.g. `passwordless-login 1`)

Parse $ARGUMENTS:
- `FEATURE` = first token  (e.g. `passwordless-login`)
- `PHASE`   = second token (e.g. `1`)

---

Follow these steps **in order**. Do not skip any step.

## Step 1 — Validate inputs

Check the following files exist. Stop with a clear error message if any are
missing:

| File | Error if missing |
|------|-----------------|
| `plans/${FEATURE}/phase${PHASE}.md` | "Phase file not found. Run `/plan ${FEATURE}` first." |
| `plans/${FEATURE}/phase${PHASE}/tasks.md` | "Task file not found. Run `/plan ${FEATURE}` first." |
| `plans/${FEATURE}/phase${PHASE}/impl-log.md` | "Implementation log not found. Run `/implement ${FEATURE} ${PHASE}` first." |
| `docs/${FEATURE}/architecture.md` | "Architecture doc not found. Run `/design ${FEATURE}` first." |
| `docs/${FEATURE}/requirements.md` | "Requirements doc not found. Run `/spec ${FEATURE}` first." |

Check the phase Status in `plans/${FEATURE}/phase${PHASE}.md`:
- If Status is not `Complete` → stop: "Phase ${PHASE} is not yet Complete
  (current status: <status>). Run `/implement ${FEATURE} ${PHASE}` first,
  or manually mark it Complete if it was implemented outside this workflow."

## Step 2 — Build the review manifest

Read `plans/${FEATURE}/phase${PHASE}/tasks.md` in full.

Build a **review manifest**: the ordered list of tasks with their associated
files. For each task `T-${PHASE}-NN`:
- Extract the task ID, title, files table (action + path), and acceptance
  criteria
- Cross-reference the `impl-log.md` to confirm each task has a PASSED entry
  and a commit hash

Log the manifest to the user:
```
📋 Review manifest for ${FEATURE} phase ${PHASE}:
  T-${PHASE}-01 · <title> — <N files> (<commit sha short>)
  T-${PHASE}-02 · <title> — <N files> (<commit sha short>)
  …
  Total: N tasks, N files, N commits
```

## Step 3 — Run per-task code reviews

For each task in the manifest, **sequentially**, invoke `@code-reviewer`:

Pass it a focused context package:
- The single task block (ID, title, files table, acceptance criteria, notes,
  satisfies FR/NFR)
- The current content of every file listed in that task's files table
- The relevant architecture extracts for those files:
  - Component table rows for those paths
  - API contract if the task touches an endpoint
  - ADR entries cited in the task's Notes field
  - Schema rows if the task touches the DB
- The phase testing requirements §6 (unit + integration test table)
- The impl-log entry for this task (actual vs estimated effort, notes,
  any deviations noted by tdd-implementer)

Do NOT pass: the full architecture doc, other tasks' files, the full task
list, or prior review findings.

Wait for `@code-reviewer` to return a findings object (structure defined in
the `review-standards` skill). Collect all findings objects in order.

## Step 4 — Consolidate and write report

After all per-task reviews are complete, invoke `@review-consolidator`:

Pass it:
- The complete ordered list of findings objects from Step 3
- The feature slug and phase number
- The total task count, file count, and commit count
- The phase name (from the phase file header)
- The list of FR/NFR IDs this phase satisfies (from §3.1 of the phase file)

Do NOT pass: any source file contents. The consolidator works only with
findings data.

`@review-consolidator` writes `plans/${FEATURE}/phase${PHASE}/review.md`.

## Step 5 — Report to user

After the consolidator finishes, print:

```
📝 Review complete: ${FEATURE} phase ${PHASE}

Findings summary:
  🔴 Blocking:     N   (must fix before phase is shippable)
  🟡 Non-blocking: N   (should fix in a follow-up task)
  🔵 Suggestions:  N   (optional improvements)
  ✅ Passed:       N tasks with no findings

Report written to: plans/${FEATURE}/phase${PHASE}/review.md

Next steps:
  - Fix all 🔴 blocking findings, then re-run: /review ${FEATURE} ${PHASE}
  - OR if no blocking findings: /implement ${FEATURE} $((PHASE + 1))
```

If there are zero blocking findings, also print:
```
✅ No blocking findings. Phase ${PHASE} is shippable.
```
