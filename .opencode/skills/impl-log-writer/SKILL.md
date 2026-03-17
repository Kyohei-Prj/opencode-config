---
name: impl-log-writer
description: "Defines the format for plans/<feature>/phaseN/impl-log.md — the persistent run log written by impl-orchestrator after each task. Used to resume interrupted runs and provide an audit trail of what was implemented, when, and with what result."
license: MIT
compatibility: opencode
metadata:
  category: workflow
  phase: implementation
  agent: impl-orchestrator
---

# Implementation Log Writer Skill

This skill defines the format for `plans/<feature>/phase<N>/impl-log.md`.

The log file serves two purposes:
1. **Resume support**: when a `/implement` run is interrupted, `impl-orchestrator`
   reads this file to determine which tasks already completed and resumes
   from the first incomplete task.
2. **Audit trail**: a human-readable record of every task's outcome,
   test results, and commit hash.

---

## File location

```
plans/<feature>/phase<N>/impl-log.md
```

Created by `impl-orchestrator` when the first task completes.
Appended to (never overwritten) after each subsequent task.

---

## File template

The file is created once with this header, then entries are appended:

```markdown
# Implementation Log: Phase <N> — <Phase Name>

> **Feature**: <feature-slug>
> **Phase**: <N>
> **Run started**: YYYY-MM-DD HH:MM
> **Last updated**: YYYY-MM-DD HH:MM

---
```

---

## Entry format

Append one entry block after each task completes (pass, fail, or blocked).
Entries are separated by `---` and appear in chronological order.

### PASSED entry

```markdown
## T-<N>-NN · <Task title> · ✅ PASSED

> **Completed**: YYYY-MM-DD HH:MM
> **Effort actual**: <S|M|L> (estimated: <S|M|L>)
> **Commit**: `<full commit hash>` — `<commit message>`

**Files changed**:
- `<path>` — <created|modified>
- `<path>` — <created|modified>

**Tests**:
- Command: `<test command run>`
- Result: `<N passed, 0 failed>`

**Notes**: <Any implementation notes, ambiguities resolved, or deviations from
the task spec. Omit this line if none.>

---
```

### FAILED (blocked after retry) entry

```markdown
## T-<N>-NN · <Task title> · ❌ BLOCKED

> **Blocked at**: YYYY-MM-DD HH:MM
> **Attempts**: 2 (1 initial + 1 retry)

**Failure reason**:
<Detailed description of what failed. Include the exact test output or error
message that caused the block. Be specific enough that a developer can
diagnose the problem without running the code.>

**Tests**:
- Command: `<test command run>`
- Result: `<N passed, N failed>`
- Failing test: `<test name>` → `<assertion error>`

**Files left in working tree** (not committed):
- `<path>` — <describe state of file>

**Suggested resolution**:
<One paragraph describing what a developer should investigate or change to
unblock this task. This is the agent's best guess — not guaranteed correct.>

---
```

### SKIPPED entry (for tasks already complete when resuming)

```markdown
## T-<N>-NN · <Task title> · ⏭ SKIPPED (already complete)

> **Skipped at**: YYYY-MM-DD HH:MM
> **Reason**: Task was marked `[x]` in tasks.md before this run began.

---
```

---

## Phase completion entry

Appended by `impl-orchestrator` after `@test-runner` confirms all exit criteria pass:

```markdown
## Phase <N> Complete · ✅ ALL EXIT CRITERIA PASSED

> **Completed**: YYYY-MM-DD HH:MM

**Exit criteria verification**:
| Criterion | Status | Evidence |
|-----------|--------|----------|
| `<criterion text>` | ✅ | `<test output or command result>` |
| `<criterion text>` | ✅ | `<test output or command result>` |

**Summary**:
- Tasks completed: N of N
- Total commits: N
- First commit: `<sha>`
- Final commit: `<sha>`

---
```

---

## Formatting rules

1. **Never overwrite** the log file — always append.
2. **Timestamps** use local time in `YYYY-MM-DD HH:MM` format.
3. **Commit hashes** are the full 40-character SHA, not abbreviated.
4. **File paths** are relative to project root (no leading `/`).
5. **Test result format** is always `N passed, N failed` — no other wording.
6. Entries are separated by `---` on its own line.
7. The file ends with `---` and a trailing newline after the last entry.

---

## Resume logic (how impl-orchestrator uses this file)

When `impl-orchestrator` detects a phase is `In Progress` on entry:

1. Read `impl-log.md` and extract all task IDs with `✅ PASSED` entries.
2. Cross-reference with `tasks.md` — any task with a PASSED log entry AND
   `[x]` in tasks.md is considered done.
3. The first task in tasks.md with `[ ]` (not `[x]`) is the resume point.
4. Log a SKIPPED entry for each already-complete task (for auditability).
5. Proceed with the resume-point task.

If `impl-log.md` does not exist but phase Status is `In Progress`, treat all
tasks as incomplete and start from the beginning.
