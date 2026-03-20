---
name: verify-checklist
description: Verify a completed feature for shippability using a four-stage manifest-first checklist. Check execution completeness and interface contracts from feature.yaml before touching code. Run the test suite third. Check design intent last (epic lane only). Record each failure as a typed finding. Never approve with unresolved blocking findings.
compatibility: opencode
metadata:
  used-by: feature-verifier
  load-at: agent definition time
---

## What I do

Define how the feature-verifier evaluates a completed feature for shippability. Verification is manifest-first: the manifest is checked for completeness and consistency before inspecting any code. Code inspection is a fallback for findings the manifest cannot resolve.

## Core principle

Most verification failures are visible in the manifest before a single line of code is read. A task with `phase: implementing` is not done. An open question with `blocks: true` was never resolved. An interface declared in `interfaces_produced` but absent from `interfaces_consumed` in the dependent slice is a contract gap. Read the manifest first; read the code only when the manifest is ambiguous or incomplete.

## Verification inputs

1. **`feature.yaml`** — the canonical source of truth
2. **`workflow/<feature>/runs/*.md`** — run logs for evidence, read only when a manifest check is inconclusive
3. **The codebase** — inspected only when a specific finding requires it

Never read `brief.md` or `review.md` as inputs. They are generated views.

## Verification procedure

Run the checks in order. Stop at each failing check and record a finding before continuing. Do not skip checks for a feature that appears "obviously done".

---

### Stage 1 — Execution completeness (manifest only)

**Check 1.1 — All tasks done**
- Every task in every slice has `phase: done`
- No task is `planned`, `implementing`, or `reviewing`
- Failure type: **blocking**

**Check 1.2 — No open blockers**
- `execution.blockers` has no entries with `resolved_at: null`
- Failure type: **blocking**

**Check 1.3 — All waves complete**
- Every entry in `execution.waves` has `status: complete`
- No wave is `pending`, `running`, or `failed`
- Failure type: **blocking**

**Check 1.4 — Open questions resolved**
- Every entry in `problem.open_questions` with `blocks: true` has `status: resolved` or `status: deferred`
- An `open` blocking question at verify time is a planning failure
- Failure type: **blocking**

---

### Stage 2 — Interface contract consistency (manifest + light code inspection)

**Check 2.1 — Produced interfaces are consumed correctly**
- For each slice with `interfaces_produced`, verify that every dependent slice's `interfaces_consumed` references the correct name
- Name mismatches suggest a contract drift — one side was renamed during implementation
- Failure type: **blocking** if the mismatch would cause a runtime error; **non-blocking** if it is a naming inconsistency only

**Check 2.2 — No orphaned interface references**
- For each slice with `interfaces_consumed`, verify the referenced interface appears in at least one other slice's `interfaces_produced`
- An interface consumed but never produced is a missing slice or an undeclared external dependency
- Failure type: **blocking**

**Check 2.3 — Files touched are consistent with context**
- Spot-check: for each slice, verify at least one file in `context.files_touched` was actually modified
- A slice with an empty or inaccurate `files_touched` suggests the plan was not followed
- Failure type: **non-blocking** (evidence quality issue, not a correctness issue)

---

### Stage 3 — Test suite (code inspection)

**Check 3.1 — Test suite passes**
- Run the full test suite
- Zero failures, zero errors
- Failure type: **blocking**

**Check 3.2 — No skipped tests without justification**
- Skipped or pending tests must have an explanation in the relevant run log
- Unexplained skips are assumed to cover untested behaviour
- Failure type: **blocking** if the skipped test covers an acceptance criterion; **non-blocking** otherwise

**Check 3.3 — Coverage of acceptance criteria**
- For each acceptance criterion across all tasks, confirm a test exists that directly covers it
- Sampling check for standard and small lanes — not a line-coverage requirement
- For epic lane: full coverage of all acceptance criteria is required
- Failure type: **blocking** if an acceptance criterion has zero test coverage

---

### Stage 4 — Design intent (code inspection, epic lane only)

Skip this stage for `small` and `standard` lanes unless a specific earlier check flagged a potential design deviation.

**Check 4.1 — Components match design**
- Each component in `design.components` is present in the codebase with its declared responsibility intact
- Failure type: **non-blocking** (flag for human review)

**Check 4.2 — Rollout strategy implemented**
- If `design.rollout.strategy` is `flag` or `phased`, verify the flag/gate mechanism exists in code
- Failure type: **blocking** if strategy is `flag` or `phased` and no mechanism is present

**Check 4.3 — Risk mitigations in place**
- For each `design.risks` entry with a non-null `mitigation`, verify the mitigation is implemented
- Failure type: **non-blocking** (flag for human review)

---

## Recording findings

For each failed check, record a finding in `review.findings`:

```yaml
- id: fnd-NNN
  type: blocking | non-blocking | suggestion
  status: raised
  description: <specific — name the check, what was found, what is needed>
  slice: <slice-slug | null>
  task: <task-NNN | null>
  raised_at: <ISO 8601>
  resolved_at: null
  resolved_by: null
```

Finding descriptions must be actionable. Bad: "tests failing". Good: "Check 3.1 — 2 tests in auth-token slice are failing: `token_expires_after_ttl` and `invalid_signature_rejected`. Run `/fix <feature> fnd-001` to route through a fix cycle."

## Verdict

After all checks complete:

- **`approved`** — no findings with `type: blocking` and `status: raised`
- **`blocked`** — one or more blocking findings remain

Write the verdict to `review.verdict`. Write `final_review.recommended_next_action`:
- `approved` → "Ready to merge."
- `blocked` → List each blocking finding id and the `/fix` command to resolve it.

## Lane adjustments

| Check | small | standard | epic |
|---|---|---|---|
| Stage 1 — execution completeness | Full | Full | Full |
| Stage 2 — interface contracts | Checks 2.1–2.2 only | Full | Full |
| Stage 3 — test suite | 3.1 + 3.3 (sampling) | Full | Full |
| Stage 4 — design intent | Skip | Skip | Full |

## What the feature-verifier does not do

- Does not re-implement or fix anything
- Does not update task phases (those are frozen at verify time — execution is complete)
- Does not approve a feature with unresolved blocking findings under any circumstances
- Does not treat a clean `review.md` from a previous run as evidence of anything — always re-run from the manifest
