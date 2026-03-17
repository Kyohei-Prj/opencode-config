---
description: "Break an architecture.md into per-phase plan files (plans/<feature>/phaseN.md) and per-phase task lists (plans/<feature>/phaseN/tasks.md)"
agent: phase-planner
subtask: true
---

You are starting the implementation planning stage for an existing architecture document.

Feature slug provided by the user:
$ARGUMENTS

---

Follow these steps **in order**. Do not skip or reorder any step.

## Step 1 — Validate inputs

1. Confirm `docs/$ARGUMENTS/architecture.md` exists.
   - If it does not exist, stop immediately and report:
     "No architecture document found at `docs/$ARGUMENTS/architecture.md`. Run `/design $ARGUMENTS` first."
2. Read `docs/$ARGUMENTS/architecture.md` in full.
3. Read `docs/$ARGUMENTS/requirements.md` in full (for FR/NFR IDs and priorities).
4. If the architecture Status is `Draft`, continue but prepend this warning to
   every generated file:
   > ⚠️ **Warning**: Based on a Draft architecture document. Confirm architecture
   > is approved before starting implementation.

## Step 2 — Extract and enumerate phases

From `## 9. Implementation Phases` in the architecture document:
- Identify every phase (Phase 1, Phase 2, … Phase N).
- For each phase, extract: name, goal, entry criteria, in-scope deliverables,
  out-of-scope items, key files table, and exit criteria.
- Confirm the phase ordering is correct (each phase's entry criteria match the
  prior phase's exit criteria).
- Record the total phase count — you will need it in Step 3 and 4.

## Step 3 — Generate all phase files

For each phase N (1 … total):
1. Load the `phase-writer` skill to get the exact template.
2. Write a complete phase document to `plans/$ARGUMENTS/phase<N>.md`.
3. Create `plans/$ARGUMENTS/` if it does not exist.
4. Do not proceed to the next phase until the current file is written and confirmed.

Write phases sequentially: phase1.md → phase2.md → … Do not batch or skip.

## Step 4 — Generate all task files

For each phase N (1 … total), invoke the `@task-decomposer` subagent:
- Pass it: the feature slug, the phase number, the path to the phase file just written,
  and the paths to the architecture and requirements docs.
- The subagent will write `plans/$ARGUMENTS/phase<N>/tasks.md`.
- Wait for each subagent call to complete before invoking the next.

Invoke `@task-decomposer` sequentially per phase: phase1 → phase2 → …

## Step 5 — Confirm

Print a structured summary:

```
✅ Planning complete for: $ARGUMENTS

Phase files written:
  plans/$ARGUMENTS/phase1.md  — <phase name>
  plans/$ARGUMENTS/phase2.md  — <phase name>
  …

Task files written:
  plans/$ARGUMENTS/phase1/tasks.md  — N tasks
  plans/$ARGUMENTS/phase2/tasks.md  — N tasks
  …

⚠️ Open questions requiring human input before Phase 1 begins:
  - <list any Q-1, Q-2 … items carried over from architecture>

Next step: run /implement $ARGUMENTS phase1 task1 to begin implementation.
```
