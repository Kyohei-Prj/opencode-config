---
name: review-report-writer
description: "Canonical template and formatting rules for review report documents at plans/<feature>/phaseN/review.md. Load before writing any review report. Consumed by review-consolidator after all per-task code-reviewer findings are collected."
license: MIT
compatibility: opencode
metadata:
  category: workflow
  phase: review
  prev-artifact: plans/<feature>/phaseN/impl-log.md
  next-phase: implementation (next phase) or validate
---

# Review Report Writer Skill

This skill defines the exact template and rules for all
`plans/<feature>/phase<N>/review.md` files.

The review report is the deliverable of the `/review` workflow. It is the
authoritative record of what was found, how severe each finding is, and
what must change before the phase is considered shippable. It is written
by `review-consolidator` from the aggregated findings objects produced by
per-task `code-reviewer` invocations.

---

## Document template

```markdown
# Code Review: Phase <N> — <Phase Name>

> **Feature**: <feature-slug>
> **Phase file**: [phase<N>.md](./phase<N>.md)  
> **Verdict**: ✅ Approved | ✅ Approved with notes | 🔴 Changes required
> **Reviewed**: YYYY-MM-DD
> **Tasks reviewed**: <N>
> **Files reviewed**: <N>
> **Commits reviewed**: <N>

---

## Summary

| Severity | Count | Must fix before shipping? |
|----------|-------|--------------------------|
| 🔴 Blocking | N | Yes |
| 🟡 Non-blocking | N | No — address in follow-up |
| 🔵 Suggestion | N | No — optional |
| **Total findings** | **N** | |

| Lens | Result |
|------|--------|
| Spec conformance | ✅ Passed / ⚠️ N findings |
| TDD quality | ✅ Passed / ⚠️ N findings |
| Architecture conformance | ✅ Passed / ⚠️ N findings |

| Task | Verdict |
|------|---------|
| T-<N>-01 · <title> | ✅ Passed |
| T-<N>-02 · <title> | 🟡 1 non-blocking |
| T-<N>-03 · <title> | 🔴 2 blocking, 1 non-blocking |

---

## Verdict

<!-- Choose one block and delete the others -->

### ✅ Approved

No blocking or non-blocking findings. Phase <N> is shippable.
Suggestions are recorded below for optional follow-up.

---

### ✅ Approved with notes

No blocking findings. Phase <N> is shippable.
<N> non-blocking finding(s) should be addressed in a follow-up task before
the next phase begins. Suggestions are optional.

---

### 🔴 Changes required

<N> blocking finding(s) must be resolved before Phase <N> is shippable.

To fix and re-review:
1. Address every 🔴 blocking finding below
2. Commit the fixes using the same conventional commit style
3. Re-run: `/review <feature> <N>`

---

## Findings

<!-- If no findings at all, write: "No findings. All tasks passed all three lenses." -->

### 🔴 Blocking findings

<!-- If none, write: "None." -->

#### <F-N-NN-NN> · <Finding title>

> **Task**: T-<N>-NN · <task title>  
> **Lens**: Spec conformance | TDD quality | Architecture conformance  
> **File**: `<path/to/file.ts>`  
> **Lines**: <start>–<end>  
> **References**: <ADR-N>, <FR-N>, <§section>

**Problem**

<Clear description of what is wrong and why it matters. Specific enough that
a developer who did not write the code can understand it immediately. Reference
the exact criterion, ADR, or architecture section violated.>

**Required resolution**

<What must change to resolve this finding. Describe the outcome, not the
implementation. "Add a test case that covers [criterion]" not "Here is the
code to add".>

---

<!-- repeat for each blocking finding -->

### 🟡 Non-blocking findings

<!-- If none, write: "None." -->

#### <F-N-NN-NN> · <Finding title>

> **Task**: T-<N>-NN · <task title>  
> **Lens**: Spec conformance | TDD quality | Architecture conformance  
> **File**: `<path/to/file.ts>`  
> **Lines**: <start>–<end>  
> **References**: <ADR-N>, <FR-N>, <§section>

**Problem**

<Description of the issue.>

**Suggested resolution**

<What would resolve this finding. Non-binding — use judgement.>

---

<!-- repeat for each non-blocking finding -->

### 🔵 Suggestions

<!-- If none, write: "None." -->

#### <F-N-NN-NN> · <Finding title>

> **Task**: T-<N>-NN · <task title>  
> **Lens**: Spec conformance | TDD quality | Architecture conformance  
> **File**: `<path/to/file.ts>`  
> **Lines**: <start>–<end>

**Observation**

<Description of the opportunity.>

---

<!-- repeat for each suggestion -->

## Per-task review results

Summary of results by task with impl-log notes.

| Task | Files | Overall | Blocking | Non-blocking | Suggestions | Impl-log notes |
|------|-------|---------|----------|-------------|-------------|----------------|
| T-<N>-01 · <title> | N | ✅ passed | 0 | 0 | 0 | — |
| T-<N>-02 · <title> | N | 🟡 needs work | 0 | 1 | 1 | <note from impl-log> |
| T-<N>-03 · <title> | N | 🔴 needs work | 2 | 1 | 0 | — |

---

## Findings index

Quick reference for all findings.

| ID | Severity | Task | File | Title |
|----|----------|------|------|-------|
| F-<N>-NN-01 | 🔴 Blocking | T-<N>-NN | `path/to/file.ts` | <title> |
| F-<N>-NN-02 | 🟡 Non-blocking | T-<N>-NN | `path/to/file.ts` | <title> |
| F-<N>-NN-03 | 🔵 Suggestion | T-<N>-NN | `path/to/file.ts` | <title> |

<!-- If no findings: "No findings." -->

---

## Requirements traceability

Which FR/NFR IDs does this phase cover, and what is their review status?

| Requirement | Covered by tasks | Review status |
|-------------|-----------------|---------------|
| FR-1 | T-<N>-02, T-<N>-03 | ✅ Covered, no findings |
| FR-2 | T-<N>-04 | ⚠️ Covered, 1 blocking finding (F-<N>-04-01) |
| NFR-1 | T-<N>-05 | ✅ Covered, no findings |

---

## Next steps

<!-- Choose the appropriate block -->

**If Approved or Approved with notes:**
```
Next: /implement <feature> <next-phase-number>
```
If there are non-blocking findings, create a follow-up task in
`plans/<feature>/phase<next>/tasks.md` before running /implement.

**If Changes required:**
```
1. Fix all 🔴 blocking findings
2. Commit fixes using conventional commit style
3. Re-run: /review <feature> <N>
```

---

## References

- [Phase <N> file](./phase<N>.md)
- [Task list](./phase<N>/tasks.md)
- [Implementation log](./phase<N>/impl-log.md)
- [Architecture document](../../docs/<feature>/architecture.md)
- [Requirements document](../../docs/<feature>/requirements.md)
```

---

## Formatting rules

1. **File name**: always `review.md`, inside `plans/<feature>/phase<N>/`.
2. **Verdict** in frontmatter must match the body's Verdict section exactly.
3. **Finding IDs** must appear in the findings index and the per-task table.
   They must match the IDs in the findings objects from `code-reviewer`.
4. **Findings order**: Blocking → Non-blocking → Suggestions.
   Within each group: ascending by finding ID (F-N-NN-01 before F-N-NN-02).
5. **Verdict value rules**:
   - `✅ Approved` — zero blocking and zero non-blocking findings
   - `✅ Approved with notes` — zero blocking, one or more non-blocking
   - `🔴 Changes required` — one or more blocking findings
6. **Per-task table** must include every task reviewed, in task ID order.
7. **Requirements traceability table** must include every FR/NFR listed in
   the phase file's §3.1 scope table.
8. **"None."** must appear (not an empty section) when a severity group has
   no findings.
9. File must end with `## References` and a trailing newline.

---

## Verdict decision matrix

| Blocking count | Non-blocking count | Suggestion count | Verdict |
|---------------|-------------------|-----------------|---------|
| 0 | 0 | 0 | ✅ Approved |
| 0 | 0 | ≥1 | ✅ Approved |
| 0 | ≥1 | any | ✅ Approved with notes |
| ≥1 | any | any | 🔴 Changes required |

---

## Quality checklist

Before writing the file, confirm:

- [ ] Verdict is consistent with the finding counts in the summary table
- [ ] Every finding ID from the findings objects appears in the report
- [ ] No finding IDs are invented that did not come from code-reviewer
- [ ] Findings are ordered: Blocking → Non-blocking → Suggestions
- [ ] Every FR/NFR from the phase's §3.1 appears in the traceability table
- [ ] Per-task table has a row for every task in the manifest
- [ ] "None." written (not empty section) for groups with zero findings
- [ ] Next steps section matches the verdict
- [ ] File saved to `plans/<feature-slug>/phase<N>/review.md`
