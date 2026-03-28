---
name: task-review-standards
description: Review a completed task against a strategy-aware checklist. First validate the strategy choice (Full TDD, Verify-after, or No test), then apply the appropriate checklist for that strategy. Produce a pass or fail verdict with a specific, actionable rejection reason. Never re-implement. Never approve with conditions.
compatibility: opencode
metadata:
  used-by: task-reviewer
  load-at: agent definition time
---

## What I do

Define how the task-reviewer evaluates a completed task before marking it `done`. Review is a gate, not a ceremony — it exists to catch problems at the smallest possible scope before they compound across the build.

## Core principle

The task-reviewer does not re-run implementation. It reads the run log, inspects the diff, and makes a verdict. The first thing to validate is the strategy choice — an incorrect strategy classification is itself a rejection reason.

## Review inputs

Before reviewing, read:

1. **The task definition** — `plan.dag.<slice>.tasks[task-id]` including `description`, `acceptance_criteria`, and `phase`
2. **The run log** — `workflow/<feature>/runs/<run-id>.md`, including the declared strategy and rationale
3. **The diff** — the actual code changes produced
4. **The slice context** — `plan.dag.<slice>.context` to understand intended scope

---

## Step 0 — Validate the strategy

Read the `**Strategy:**` field and rationale from the run log. Before checking anything else, confirm the strategy was correctly chosen.

### Is Strategy 3 (No test) justified?

Reject if any of the following are true:
- The acceptance criteria describe behaviour, not just existence or presence
- The implementation contains logic (conditionals, transformations, calculations) that could be wrong
- A meaningful test could have been written that would catch a real bug

**Example valid Strategy 3:** "create the src/auth/ directory structure", "install jest and ts-jest as devDependencies", "add .env.example with documented variables"

**Example invalid Strategy 3 (reject):** "add input validation to the registration endpoint" — this has clear verifiable behaviour and must use Strategy 1.

### Is Strategy 2 (Verify-after) justified?

Reject if:
- The task has verifiable behaviour that a red test could have described before implementation (should be Strategy 1)
- The task is pure scaffolding with no observable output (should be Strategy 3)
- The verify test is tautological — passes regardless of whether the wiring is correct

**Example valid Strategy 2:** "mount the auth router at /api/v1/auth" — verified by a smoke test hitting the endpoint

**Example invalid Strategy 2:** "validate JWT tokens in the auth middleware" — this has clear logic that belongs in Strategy 1

If the strategy is wrong, reject with: `"Strategy mismatch: task has [behaviour/scaffolding] that requires Strategy [1/3] not Strategy [2/3]. Reason: <specific explanation>."`

---

## Checklist — Strategy 1 (Full TDD)

Apply all items. A single blocking failure is sufficient to reject.

### 1. Acceptance criteria coverage

- [ ] Every acceptance criterion has at least one test covering it
- [ ] Tests assert the criterion's outcome, not an implementation detail
- [ ] No criterion is covered by a test that would pass trivially (e.g. `assert True`)

### 2. Test quality

- [ ] Tests fail for the right reason in the red phase (confirmed in run log)
- [ ] Tests pass cleanly in the green phase — no skips, no pending
- [ ] No regressions in the existing test suite
- [ ] Test names are descriptive enough to understand what failed without reading the body

### 3. Implementation scope

- [ ] Changes are scoped to `context.files_touched`, or deviations are explained in the run log
- [ ] No new behaviour introduced beyond what the tests cover
- [ ] No untested code paths added

### 4. Interface contracts

- [ ] `interfaces_produced`: implementation matches the declared contract
- [ ] `interfaces_consumed`: implementation matches the producer's declaration — no silent assumptions

### 5. Code quality (lane-adjusted — see below)

- [ ] No broken patterns: infinite loops, unclosed resources, silent error swallowing
- [ ] Naming is clear enough to orient without the run log
- [ ] No commented-out code (unless intentional TODO with tracking reference)

### 6. Run log completeness

- [ ] Strategy declared with a one-sentence rationale
- [ ] Red, green, and refactor phases recorded (refactor may be "none")
- [ ] Final test output present and showing passing counts
- [ ] Notes filled in (even if "none")

---

## Checklist — Strategy 2 (Verify-after)

### 1. Verify test quality

- [ ] A smoke or integration test exists and is recorded in the run log
- [ ] The test would fail if the wiring were broken — it is not tautological
- [ ] The test passes in the run log's final test output

### 2. Implementation scope

- [ ] Changes scoped to `context.files_touched`, or deviations explained
- [ ] No untested logic introduced alongside the wiring

### 3. Interface contracts

- [ ] Same as Strategy 1 items 4a and 4b

### 4. Code quality

- [ ] Same as Strategy 1 item 5 (all three points)

### 5. Run log completeness

- [ ] Strategy declared with a one-sentence rationale
- [ ] Implementation section filled in
- [ ] Verification section filled in with test name and what it confirms
- [ ] Notes filled in

---

## Checklist — Strategy 3 (No test)

### 1. Classification validity

- [ ] Acceptance criteria describe existence or presence, not behaviour (confirmed above in Step 0)

### 2. Completeness

- [ ] Every acceptance criterion checkbox is checked — all items created/installed
- [ ] Notes section includes the no-test justification sentence and any decisions made

### 3. Scope

- [ ] Changes scoped to `context.files_touched`, or deviations explained

---

## Verdict

### Pass

All checklist items for the declared strategy are met. Transition task `phase` from `reviewing` to `done`. Write a one-line review note.

### Fail — fix required

One or more items not met. Transition task `phase` back to `implementing`. The rejection must name: which checklist item failed, what was wrong, what the builder must do.

**Example rejections:**
- `"Strategy mismatch: 'add input validation to registration' has verifiable behaviour — use Strategy 1 (Full TDD), not Strategy 3."`
- `"Strategy 2 verify test is tautological: it imports the router module and asserts it is defined, which passes even if the router is not mounted. Write a test that sends a request to /api/v1/auth and gets a non-404 response."`
- `"Strategy 1 criterion 2 (token expiry) has no test. Add a test asserting tokens expire after the configured TTL."`
- `"Run log is missing the strategy rationale. Add a one-sentence explanation of why [strategy] was chosen."`

### Fail — blocker raised

Task cannot complete as specified due to a design gap or missing dependency. Record in `execution.blockers`. Do not send back to `implementing` (the builder cannot fix a design gap unilaterally).

---

## Lane adjustments

### small

Relax Strategy 1 checklist:
- Test names: acceptable if they describe the scenario, even briefly
- Code quality: items 1–3 only (broken patterns, naming, dead code). Style alignment not required.
- Refactor: may be skipped

### standard

Full checklist for declared strategy. No relaxations.

### epic

Strategy 1 full checklist plus:
- [ ] Contract tests exist for every `interfaces_produced` entry
- [ ] Edge cases and error paths are covered
- [ ] Changes align with project conventions — deviations noted
- [ ] No TODO comments without a tracking reference

Strategy 2: full integration test required (not just a smoke test).

---

## What the task-reviewer does not do

- Does not re-run or re-implement the task
- Does not modify code
- Does not add new acceptance criteria (plan change — raise as blocker)
- Does not approve with conditions — pass or fail only
- Does not review tasks in other slices
- Does not read `brief.md` or `review.md` as inputs
