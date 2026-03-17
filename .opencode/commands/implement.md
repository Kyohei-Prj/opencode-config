---
description: "Implement one phase of a feature using TDD, task by task. Each task runs in its own sub-agent context. Usage: /implement <feature> <phase-number>"
agent: impl-orchestrator
subtask: true
---

You are starting the TDD implementation stage for a single feature phase.

Arguments: $ARGUMENTS
(Expected format: `<feature-slug> <phase-number>` — e.g. `passwordless-login 1`)

Parse $ARGUMENTS:
- `FEATURE` = first token  (e.g. `passwordless-login`)
- `PHASE`   = second token (e.g. `1`)

---

Follow these steps **in order**. Do not skip any step.

## Step 1 — Validate all inputs

Check the following files exist. Stop with a clear error message if any are missing:

| File | Error if missing |
|------|-----------------|
| `plans/${FEATURE}/phase${PHASE}.md` | "Phase file not found. Run `/plan ${FEATURE}` first." |
| `plans/${FEATURE}/phase${PHASE}/tasks.md` | "Task file not found. Run `/plan ${FEATURE}` first." |
| `docs/${FEATURE}/architecture.md` | "Architecture doc not found. Run `/design ${FEATURE}` first." |

Read all three files in full before proceeding.

Also check `plans/${FEATURE}/phase${PHASE}.md` §2 Entry Criteria:
- If any entry criterion is unchecked (`[ ]`), list them and ask the user to
  confirm before continuing. Do not proceed automatically.

## Step 2 — Check phase status

Read the Status field in `plans/${FEATURE}/phase${PHASE}.md`:
- If `Complete` → stop: "Phase ${PHASE} is already marked Complete.
  To re-run, manually reset its Status to Pending."
- If `Pending` → update it to `In Progress` now, before any task work begins.
- If `In Progress` → a previous run was interrupted. Read
  `plans/${FEATURE}/phase${PHASE}/impl-log.md` (if it exists) to determine
  which tasks already have status `[x]` and resume from the first `[ ]` task.

## Step 3 — Build the task queue

From `plans/${FEATURE}/phase${PHASE}/tasks.md`, extract the ordered task list.
Skip any task already marked `[x]` (completed in a prior run).
The remaining tasks become the queue, in their existing order.

Log the queue to the user:
```
📋 Task queue for ${FEATURE} phase ${PHASE}:
  [ ] T-${PHASE}-01 · <title> · <effort>
  [ ] T-${PHASE}-02 · <title> · <effort>
  …
  Resuming from: T-${PHASE}-NN  (if resuming)
```

## Step 4 — Execute tasks via sub-agents

For each task in the queue, **sequentially**:

### 4a. Invoke @tdd-implementer

Pass it a focused context package containing only:
- Feature slug and phase number
- The single task block (ID, title, effort, dependencies, satisfies, commit
  message, what, files table, acceptance criteria, notes)
- Relevant extracts from the architecture doc (the component table entry,
  API contract, and ADR entries that apply to this task — not the full doc)
- The phase's testing requirements (§6 from the phase file)
- Paths to any files the task says it modifies (so the agent can read current state)

Do **not** pass: the full architecture doc, the full task list, other tasks'
implementation details, or prior tasks' full file contents. Keep each
`@tdd-implementer` invocation context-lean.

Wait for `@tdd-implementer` to return a result object:
```
{
  "task_id": "T-N-NN",
  "status": "passed" | "failed" | "blocked",
  "files_written": ["path/to/file", ...],
  "tests_run": "<command>",
  "test_output_summary": "<N passed, N failed>",
  "failure_reason": "<only if status != passed>",
  "commit_message": "<conventional commit string>"
}
```

### 4b. Evaluate the result

**If `passed`**:
1. Mark the task `[x]` in `plans/${FEATURE}/phase${PHASE}/tasks.md`
2. Append an entry to `plans/${FEATURE}/phase${PHASE}/impl-log.md`
   (format defined by the `impl-log-writer` skill)
3. `git add -A && git commit -m "<commit_message>"`
4. Proceed to the next task

**If `failed`**:
1. Invoke `@tdd-implementer` a second time with the same context plus the
   failure reason and test output. This is the one retry.
2. If the retry also fails → mark the task `[~]` (blocked) in the task file,
   append a BLOCKED entry to impl-log.md, and **stop the entire run**.
   Report to the user:
   ```
   ❌ Blocked on T-${PHASE}-NN · <title>
   Reason: <failure_reason>
   Test output: <test_output_summary>
   Action needed: resolve the issue manually, then re-run:
     /implement ${FEATURE} ${PHASE}
   The run will resume from this task.
   ```

**If `blocked`**:
- The agent detected a dependency or decision gap it cannot resolve.
  Stop immediately, report the blockage, and do not retry.

### 4c. Context hygiene between tasks

After each task completes, **do not carry forward** the implementation details
of the completed task into the next `@tdd-implementer` invocation. Each
invocation gets only what its own task block specifies. The context window of
`impl-orchestrator` itself must stay small — it holds task metadata, not code.

## Step 5 — Phase completion

After all tasks in the queue are `[x]`:

1. Invoke `@test-runner` with:
   - The phase file path (for exit criteria §7)
   - The test commands from the phase file's §6 and §7
   - The feature slug and phase number

2. If `@test-runner` reports all exit criteria pass:
   - Update `plans/${FEATURE}/phase${PHASE}.md` Status → `Complete`
   - Check all exit criteria boxes in §7
   - `git add -A && git commit -m "chore(${FEATURE}): phase ${PHASE} complete"`
   - Print the success summary (see below)

3. If `@test-runner` reports any failure:
   - Do NOT mark the phase Complete
   - Report which exit criterion failed
   - Leave the phase In Progress for the developer to investigate

## Step 6 — Success summary

```
✅ Phase ${PHASE} complete: ${FEATURE}

Tasks implemented: N
Tests passing:     N
Files changed:     N

Commits made:
  <sha> T-${PHASE}-01 · <title>
  <sha> T-${PHASE}-02 · <title>
  …
  <sha> chore(${FEATURE}): phase ${PHASE} complete

Next step: /implement ${FEATURE} $((PHASE + 1))
```
