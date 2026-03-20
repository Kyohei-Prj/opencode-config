---
name: brief-writer
description: Generate workflow/<feature>/brief.md from feature.yaml after the plan section is written. Defines the template structure, dependency-ordered slice rendering, and rules for omitting empty sections. brief.md is a read-only view — never an orchestration input.
compatibility: opencode
metadata:
  used-by: slice-planner
  load-at: output-write time
---

## Core rule

brief.md is generated from the manifest. If brief.md disagrees with feature.yaml, the manifest wins. Do not read brief.md as an input to any subsequent command.

## When to generate

Generate or regenerate brief.md after the `plan` section has been written to `feature.yaml`. If `/shape-slice` is used, generate once at the end of that command. If `/shape` and `/slice` are separate (epic lane), generate after `/slice`.

## Template

```markdown
# <feature.title>

**Lane:** <feature.lane>
**Status:** <feature.status>
**Last updated:** <feature.updated_at>

---

## Summary

<feature.summary>

---

## Problem

<problem.statement>

### Goals

<problem.goals as bullet list>

### Non-goals

<problem.non_goals as bullet list>

### Users

<problem.users as bullet list>

---

## Design decisions

<for each design.decisions entry>
**<dec.title>** — <dec.rationale>
</for each>

---

## Rollout

**Strategy:** <design.rollout.strategy>
<design.rollout.notes if not null>

---

## Slices

<for each slice in plan.dag, in dependency order (roots first)>
### <slice-slug>: <slice.title>

**Depends on:** <slice.depends_on as comma list, or "none">
**Files touched:** <slice.context.files_touched as comma list, or "TBD">

Tasks:
<for each task in slice.tasks>
- [ ] <task.id> — <task.title>
</for each>
</for each>

---

## Open questions

<if problem.open_questions is empty>
None.
<else>
<for each open_question>
- **<oq.id>** `[<oq.status>]` <oq.text> <if oq.blocks> ⚠️ blocks build</if>
</for each>
</if>

---

*Generated from feature.yaml. Do not edit directly — re-run `/slice` or `/shape-slice` to regenerate.*
```

## Rendering rules

- **Dependency order:** list slices so that each slice appears after all slices it depends on. For slices in the same wave (no mutual dependency), list alphabetically by slug.
- **Task checkboxes:** use `- [ ]` for all tasks regardless of phase — brief.md reflects the plan, not execution state. Execution state lives in the manifest.
- **Omit empty sections:** if `design.decisions` is empty, omit that section entirely rather than printing a header with no content. Same for rollout notes, open questions, non-goals.
- **Omit `design` and `rollout` sections** if the `design` section has not yet been added to the manifest (i.e. intake-only manifests).
- **Do not include** execution state, run history, review findings, or verdict in the brief. Those belong in `review.md`.
- **One sentence per decision** — rationale in the brief is a summary. Full detail lives in `feature.yaml`.
