---
name: task-review-standards
description: Review a completed task against a six-item checklist covering acceptance criteria coverage, test quality, implementation scope, interface contracts, code quality, and run log completeness. Produce a pass or fail verdict with a specific, actionable rejection reason. Never re-implement. Never approve with conditions.
compatibility: opencode
metadata:
  used-by: task-reviewer
  load-at: agent definition time
---

## What I do

Define how the task-reviewer evaluates a completed task before marking it `done`. Review is a gate, not a ceremony — it exists to catch problems at the smallest possible scope before they compound across the build. A task that fails review goes back to the builder; it does not proceed to the next task.

## Core principle

The task-reviewer does not re-run implementation. It reads the run log, inspects the diff, and makes a verdict. The failure surface must be clean: if the reviewer rejects a task, the reason is specific, actionable, and scoped to that task.

## Review inputs

Before reviewing, read:

1. **The task definition** — `plan.dag.<slice>.tasks[task-id]` including `description`, `acceptance_criteria`, and `phase`
2. **The run log** — `workflow/<feature>/runs/<run-id>.md` for this task
3. **The diff** — the actual code changes produced during the TDD cycle
4. **The slice context** — `plan.dag.<slice>.context` to understand intended scope

## Review checklist

Apply all checks. A single blocking failure is sufficient to reject the task.

### 1. Acceptance criteria coverage

- [ ] Every acceptance criterion has at least one test covering it
- [ ] Tests assert the criterion's outcome, not an implementation detail
- [ ] No criterion is covered by a test that would pass trivially (e.g. `assert True`)

### 2. Test quality

- [ ] Tests fail for the right reason in the red phase (confirmed in run log)
- [ ] Tests pass cleanly in the green phase — no skips, no pending, no marked-as-expected-to-fail unless intentional and noted
- [ ] No regressions in the existing test suite
- [ ] Test names are descriptive enough to understand what failed without reading the body

### 3. Implementation scope

- [ ] Changes are scoped to the files listed in `context.files_touched`, or deviations are explained in the run log
- [ ] No new behaviour was introduced beyond what the tests cover
- [ ] No untested code paths were added ("I'll test this later" is a reject)

### 4. Interface contracts

- [ ] If the slice produces an interface (`interfaces_produced`), the implementation matches the declared contract
- [ ] If the slice consumes an interface (`interfaces_consumed`), the implementation matches what the producer declared — no silent assumptions

### 5. Code quality (lane-adjusted — see below)

- [ ] No obviously broken patterns: infinite loops, unclosed resources, silent error swallowing
- [ ] Naming is clear enough that the next developer can orient without the run log
- [ ] No commented-out code left in (unless it's an intentional TODO with a tracking reference)

### 6. Run log completeness

- [ ] Red, green, and refactor phases are all recorded (or refactor is explicitly "none")
- [ ] Final test output is present and shows passing counts
- [ ] Notes section is filled in (even if "none")

## Verdict

### Pass

All checklist items are met. Transition the task `phase` from `reviewing` to `done` in the manifest. Write a one-line review note in `execution.run_history[run-id]`.

### Fail — fix required

One or more checklist items are not met. Transition the task `phase` from `reviewing` back to `implementing`. The rejection must name:
- Which checklist item failed
- What specifically was wrong
- What the builder needs to do to fix it

**Example rejections:**
- "Acceptance criterion 2 (token expiry) has no test. Add a test asserting tokens expire after the configured TTL."
- "Implementation modifies `auth/session.ts` which is outside this slice's context. Either constrain the change or raise a blocker."
- "Run log is missing the red phase. Record the initial failing test output before marking complete."

### Fail — blocker raised

The task cannot be completed as specified because of a design gap, missing dependency, or conflicting requirement. Do not send back to implementing. Instead:
- Record the blocker in `execution.blockers` in the manifest
- Set the task `phase` to `implementing` (held, not regressed)
- Surface the blocker to the build-orchestrator

## Lane adjustments

### small

Apply the full checklist but with lighter weight on code quality items. One meaningful test per acceptance criterion is sufficient. Refactor phase is optional.

Checklist items to relax:
- Test names: acceptable if they describe the scenario, even briefly
- Code quality: apply only items 1–3 (broken patterns, naming, dead code). Style alignment not required.

### standard

Full checklist. No relaxations. This is the default and the baseline for what "done" means.

### epic

Full checklist plus:
- [ ] Interface contracts are tested, not just implemented — consumer tests exist for every `interfaces_produced` entry
- [ ] Edge cases and error paths are covered (not just the happy path)
- [ ] Changes align with the project's conventions (naming, structure, import patterns) — note any deviations
- [ ] No TODO comments without a linked issue or tracking reference

## What the task-reviewer does not do

- Does not re-read the full codebase
- Does not re-run the implementation
- Does not redesign the task
- Does not add new acceptance criteria (if new criteria are needed, that is a plan change — raise it as a blocker)
- Does not approve a task "with notes" — a task either passes or fails; suggestions go in the run log as non-blocking notes, not as conditions on the verdict
