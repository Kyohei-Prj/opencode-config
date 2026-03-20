---
name: review-report-writer
description: Generate workflow/<feature>/review.md from the review section of feature.yaml after /verify completes. Defines the verdict template, finding grouping order (blocking first), verdict rendering symbols, and rendering rules. review.md is a read-only view — never an orchestration input or source of finding IDs.
compatibility: opencode
metadata:
  used-by: feature-verifier, review-consolidator
  load-at: output-write time
---

## Core rule

review.md is generated from the manifest. If review.md disagrees with feature.yaml, the manifest wins. Do not read review.md as an input to any subsequent command or as a source of finding IDs.

## When to generate

Generate after `feature-verifier` has written the complete `review` section to `feature.yaml`, including `review.verdict` and `review.final_review`.

Regenerate if `/fix` resolves findings and `/verify` is re-run scoped to those findings.

## Template

```markdown
# Review: <feature.title>

**Verdict:** <review.verdict> — APPROVED | BLOCKED | PENDING
**Checked:** <review.final_review.checked_at>
**Checked by:** <review.final_review.checked_by>

---

## Summary

<review.final_review.summary>

---

## Findings

<if no findings>
No findings.
<else>

<group findings by type: blocking first, then non-blocking, then suggestions>

### Blocking (<count of blocking findings>)

<for each blocking finding>
#### <fnd.id> — <fnd.description>

**Status:** <fnd.status>
**Slice:** <fnd.slice | "—">
**Task:** <fnd.task | "—">
**Raised:** <fnd.raised_at>
<if resolved> **Resolved:** <fnd.resolved_at> by <fnd.resolved_by> </if>

---
</for each>

### Non-blocking (<count>)

<for each non-blocking finding>
- **<fnd.id>** `[<fnd.status>]` <fnd.description> _(slice: <fnd.slice | "—">)_
</for each>

### Suggestions (<count>)

<for each suggestion finding>
- **<fnd.id>** `[<fnd.status>]` <fnd.description>
</for each>

</if>

---

## Checks run

<for each check in review.final_review.checks_run>
- <check>
</for each>

---

## Recommended next action

<review.final_review.recommended_next_action | "None">

---

*Generated from feature.yaml. Do not edit directly.*
```

## Verdict rendering

| Verdict | Header style |
|---|---|
| `approved` | `✓ APPROVED` |
| `blocked` | `✗ BLOCKED` |
| `pending` | `… PENDING` |

## Rendering rules

1. **Blocking findings always appear first**, regardless of when they were raised.
2. **Omit empty groups** — if there are no non-blocking findings, omit that section header entirely.
3. **Resolved blocking findings** are still listed under blocking — show their resolved status inline. Resolved findings explain the history; they are not hidden.
4. **Finding counts are derived** from the findings list in `feature.yaml` — do not copy stored counts.
5. **Do not include** run history, wave state, or task-level detail in the review report. That lives in run logs and the manifest.
6. **Recommended next action** maps to verdict as a default:
   - `approved` → "Ready to merge."
   - `blocked` → "Run `/fix <feature> <fnd-id>` for each blocking finding, then re-run `/verify`."
   - `pending` → "Run `/verify <feature>` to complete verification."
   Override the default if `final_review.recommended_next_action` is set in the manifest.
