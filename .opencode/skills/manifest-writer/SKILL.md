---
name: manifest-writer
description: Write and extend feature.yaml, the canonical source of truth for the workflow. Defines the full growing schema (meta, feature, problem, design, plan, execution, review), field-level writing rules, DAG constraints, open question lifecycle, review finding lifecycle, and lifecycle ownership table. Load this skill whenever writing to feature.yaml.
compatibility: opencode
metadata:
  used-by: intake-analyst, solution-shaper, slice-planner, build-orchestrator, feature-verifier
  load-at: output-write time
---

## Manifest tools — always use these, never write raw YAML

Five custom tools handle all manifest operations. **Never write raw YAML strings or use the `edit`/`write` file tools on `feature.yaml`.** LLM-generated YAML produces duplicate keys, indentation errors, and structural drift. The tools below parse and serialise safely using PyYAML.

| Tool | When to use |
|---|---|
| `manifest_read` | Before every write — get current state as parsed JSON |
| `manifest_write_section` | Write a new top-level section for the first time (intake, shape, slice, build, verify) |
| `manifest_set` | Targeted single-field update — status transitions, timestamps, phase changes, commit SHAs |
| `manifest_append` | Add an item to any list — run_history, findings, blockers, open_questions, waves |
| `manifest_validate` | After every write — catch missing sections, bad paths, invalid values immediately |

### Rule: read → write → validate

Every manifest update follows this sequence:

```
1. manifest_read(slug)           — confirm current state before writing
2. manifest_set / manifest_append / manifest_write_section
3. manifest_validate(slug)       — fix any errors before continuing
```

Never skip the validate step. A failed validate must be resolved before the agent proceeds.

### Dot-path reference

`manifest_set` and `manifest_append` use dot-separated paths. Numeric indices address list items. Hyphenated keys work as-is.

```
feature.status                              → scalar field
feature.commands.next                       → nested scalar
execution.waves.0.status                    → list item by index
execution.waves.0.completed_at              → list item field
plan.dag.auth-token.tasks.0.phase           → nested in hyphenated key
execution.slice_commits.auth-token          → map entry with hyphenated key
review.findings                             → list (for manifest_append)
execution.run_history                       → list (for manifest_append)
execution.blockers                          → list (for manifest_append)
problem.open_questions                      → list (for manifest_append)
```

### Common operation patterns

```
# Status transition (always pair with commands update)
manifest_set(slug, "feature.status", '"building"')
manifest_set(slug, "feature.commands.current", '"/build"')
manifest_set(slug, "feature.commands.next", '"/verify"')

# Task phase advance
manifest_set(slug, "plan.dag.auth-token.tasks.0.phase", '"reviewing"')

# Wave completion
manifest_set(slug, "execution.waves.0.status", '"complete"')
manifest_set(slug, "execution.waves.0.completed_at", '"2026-03-18T15:00:00Z"')

# Slice commit recorded
manifest_set(slug, "execution.slice_commits.auth-token", '"a1b2c3d4e5f6"')

# Run history entry added
manifest_append(slug, "execution.run_history", {
  "run_id": "auth-token-task-001-20260318-143022",
  "slice": "auth-token",
  "task": "task-001",
  "status": "pass",
  "started_at": "2026-03-18T14:00:00Z",
  "completed_at": "2026-03-18T14:20:00Z",
  "commit_sha": null
})

# Blocker raised
manifest_append(slug, "execution.blockers", {
  "id": "blk-001",
  "description": "Missing TokenService interface",
  "slice": "auth-token",
  "task": "task-002",
  "raised_at": "2026-03-18T15:30:00Z",
  "resolved_at": null
})

# Review finding raised
manifest_append(slug, "review.findings", {
  "id": "fnd-001",
  "type": "blocking",
  "status": "raised",
  "description": "Check 3.1 — test suite failing",
  "slice": "auth-token",
  "task": null,
  "raised_at": "2026-03-18T16:00:00Z",
  "resolved_at": null,
  "resolved_by": null
})

# New section written for first time
manifest_write_section(slug, "execution", {
  "concurrency": 2,
  "waves": [],
  "run_history": [],
  "slice_commits": {},
  "blockers": []
})

# Always validate after any write
manifest_validate(slug)
```

### Value encoding for manifest_set

The `value` argument must be a JSON-encoded string:

| Type | Example |
|---|---|
| String | `'"building"'` |
| Number | `'1'` |
| Boolean | `'true'` |
| Null | `'null'` |
| Object | `'{"key": "value"}'` |
| ISO date | `'"2026-03-18"'` |
| ISO timestamp | `'"2026-03-18T15:00:00Z"'` |

---

## Core rule


The manifest is the source of truth. Generated markdown files (brief.md, review.md, runs/*.md) are read-only views. If they disagree with feature.yaml, the manifest wins. Never read generated files as orchestration inputs.

## Growth pattern

The manifest grows incrementally — each pipeline stage adds its own section. Do not pre-declare sections that haven't been written yet. Empty noise fields make manifests harder to read and increase hallucination risk.

| Stage completed | Sections present in manifest |
|---|---|
| `/intake` | `meta` + `feature` + `problem` (seeded) |
| `/shape` or `/shape-slice` | + `design` |
| `/slice` or `/shape-slice` | + `plan` |
| `/build` (first run) | + `execution` |
| `/verify` | + `review` |

Never add a section before its stage. Never leave a section out after its stage completes.

## Section schemas

### `meta` — added at intake

```yaml
meta:
  schema_version: "1.0"
  lane_confirmed_by: null        # set to "user" after confirmation gate
  lane_confirmed_at: null        # ISO 8601 timestamp
```

### `feature` — added at intake

```yaml
feature:
  slug: <kebab-case-string>      # derived from idea, used as directory name
  title: <string>                # human-readable title
  lane: small | standard | epic  # set after confirmation gate
  proposed_lane: small | standard | epic  # set by lane-classifier before confirmation
  lane_rationale: <string>       # one sentence explaining the classification
  status: <status-value>         # see status lifecycle below
  summary: <string>              # one sentence: what the feature does for the user
  source_idea: <string>          # the raw idea string passed to /intake
  created_at: <YYYY-MM-DD>
  updated_at: <YYYY-MM-DD>
  owner: ai | human
  commands:
    current: <string>            # command that produced the current state
    next: <string>               # recommended next command
```

**Status lifecycle:**

```
intake_complete
  → shaping
  → shape_complete
  → slicing
  → slice_complete
  → building
  → build_complete
  → verifying
  → verified
  → blocked                      # set when verify verdict is "blocked"
```

### `problem` — seeded at intake, completed at shape

At intake, seed only the fields the idea provides. Leave others as empty lists or null — do not invent values.

```yaml
problem:
  statement: <string>
  goals:
    - <string>
  non_goals:
    - <string>
  users:
    - <string>
  stories: []                          # filled at shape
  functional_requirements: []          # filled at shape
  non_functional_requirements: []      # filled at shape
  constraints: []                      # filled at shape
  assumptions: []                      # filled at shape
  open_questions:                      # may be seeded at intake if obvious unknowns exist
    - id: <oq-NNN>
      text: <string>
      status: open | resolved | deferred
      resolved_by: null                # agent name or "user"
      blocks: true | false             # if true, /build halts affected slices until resolved
```

### `design` — added at shape

```yaml
design:
  context:
    codebase_findings:
      - <string>
    constraints:
      - <string>
    assumptions:
      - <string>
  decisions:
    - id: <dec-NNN>
      title: <string>
      rationale: <string>
      alternatives_considered:
        - <string>
  components:
    - name: <string>
      responsibility: <string>
      interfaces_consumed: []
      interfaces_produced: []
  integration_points:
    - <string>
  rollout:
    strategy: none | flag | phased | migration
    notes: <string | null>
  risks:
    - id: <risk-NNN>
      description: <string>
      severity: low | medium | high
      mitigation: <string | null>
```

Only include `rollout` subfields relevant to the chosen strategy. Omit `flags` and `migration_notes` keys entirely if strategy is `none`.

### `plan` — added at slice

```yaml
plan:
  dag:
    <slice-slug>:
      title: <string>
      depends_on: []             # list of slice-slug strings; empty for root slices
      context:
        files_touched: []        # relative paths this slice is expected to modify
        interfaces_consumed: []  # interface names this slice reads
        interfaces_produced: []  # interface names this slice writes
      open_questions: []         # oq-NNN ids that block this slice
      tasks:
        - id: <task-NNN>
          title: <string>
          description: <string>
          phase: planned | implementing | reviewing | done
          acceptance_criteria:
            - <string>
```

**DAG rules:**
- Root slices have `depends_on: []`
- `depends_on` lists slice slugs, not task ids
- A slice may not depend on itself (no cycles)
- The orchestrator computes waves from the DAG at runtime — do not store `slice_order` or wave assignments here

### `execution` — added at first /build run

```yaml
execution:
  concurrency: <int>             # --concurrency value passed to /build
  waves:
    - wave: <int>                # 1-indexed
      slices: [<slice-slug>]
      status: pending | running | complete | failed
      started_at: <ISO 8601 | null>
      completed_at: <ISO 8601 | null>
  run_history:
    - run_id: <string>           # matches runs/<run-id>.md filename
      slice: <slice-slug>
      task: <task-NNN>
      status: pass | fail | skip
      started_at: <ISO 8601>
      completed_at: <ISO 8601 | null>
      commit_sha: <string | null>  # SHA of the slice commit; null until slice is committed
  slice_commits:                 # one entry per committed slice; written after all tasks in the slice are done
    <slice-slug>: <full commit SHA>
  blockers:
    - id: <blk-NNN>
      description: <string>
      slice: <slice-slug>
      task: <task-NNN | null>
      raised_at: <ISO 8601>
      resolved_at: <ISO 8601 | null>
```

### `review` — added at /verify

```yaml
review:
  status: pending | in_progress | complete
  verdict: pending | approved | blocked
  findings:
    - id: <fnd-NNN>
      type: blocking | non-blocking | suggestion
      status: raised | acknowledged | resolved | waived
      description: <string>
      slice: <slice-slug | null>
      task: <task-NNN | null>
      raised_at: <ISO 8601>
      resolved_at: <ISO 8601 | null>
      resolved_by: <string | null>
  final_review:
    summary: <string | null>
    checked_at: <ISO 8601 | null>
    checked_by: <string | null>
    checks_run: []
    recommended_next_action: <string | null>
```

**Verdict rules:**
- `approved` — no findings with `type: blocking` and `status: raised | acknowledged`
- `blocked` — one or more blocking findings remain unresolved
- Counts (blocking_count, etc.) are derived at read time from the findings list — never store them as fields

## Writing rules

1. **Always update `feature.updated_at`** when writing any section.
2. **Always update `feature.status`** to reflect the stage just completed.
3. **Always update `feature.commands.current` and `.next`** after each stage.
4. **Preserve existing content.** Agents add to the manifest; they do not rewrite sections owned by earlier stages.
5. **Use `null`, not empty string**, for optional fields with no value yet.
6. **Use ISO 8601 dates** (`YYYY-MM-DD` for dates, `YYYY-MM-DDTHH:MM:SSZ` for timestamps).
7. **IDs are stable.** Once assigned, a finding/question/task/blocker id never changes.
8. **Slug format:** lowercase, hyphens only, no underscores, no spaces.

## Open question lifecycle

```
open
  → resolved   (answer found — set resolved_by to agent name or "user")
  → deferred   (answer not needed before build — acknowledged but not blocking)
  → open       (remains open if blocks: false — does not halt build)
```

**Transition rules:**
- Only `solution-shaper` and the user may transition `open → resolved`
- `build-orchestrator` reads but never writes question status — it halts on `open + blocks: true`
- `deferred` is a user decision — it means "we accept the ambiguity and will proceed"
- A question with `blocks: false` never halts the build regardless of status
- Once `resolved` or `deferred`, a question is never set back to `open`

**Who writes what:**

| Agent / actor | Permitted transitions |
|---|---|
| `intake-analyst` | Creates questions with `status: open` |
| `solution-shaper` | `open → resolved` (if codebase answers it), adds new questions |
| User (via manifest edit) | `open → resolved`, `open → deferred` |
| `build-orchestrator` | Read only — halts slice if `open + blocks: true` |
| `/resume` | Read only — re-checks status before restarting a halted slice |

## Review finding lifecycle

```
raised
  → acknowledged   (/fix has picked up the finding and fix is in progress)
  → resolved       (fix cycle completed successfully)
  → waived         (user accepted the risk; finding bypassed)
```

**Transition rules:**
- `feature-verifier` creates findings with `status: raised`
- `/fix` transitions `raised → acknowledged` before the fix cycle begins
- `feature-verifier` (scoped re-verify) transitions `acknowledged → resolved` or back to `raised`
- Only the user may set `status: waived` — never an agent
- `resolved` and `waived` are terminal — never transition out of them
- Verdict re-evaluation happens after every finding status change:
  - If no `blocking` findings remain with `status: raised | acknowledged` → `verdict: approved`
  - Otherwise → `verdict: blocked`

**Who writes what:**

| Agent / actor | Permitted transitions |
|---|---|
| `feature-verifier` | Creates findings (`raised`), `acknowledged → resolved`, `acknowledged → raised` |
| `review-consolidator` | Creates non-blocking/suggestion findings (`raised`) only |
| `/fix` command | `raised → acknowledged` |
| User (via manifest edit) | `raised → waived`, `acknowledged → waived` |

**Finding severity does not change.** Once a finding is typed as `blocking`, `non-blocking`, or `suggestion`, the type is frozen. If the severity assessment was wrong, waive the finding and raise a new one with the correct type.

**Stuck `acknowledged` findings.** If a `/fix` cycle fails and cannot proceed, the finding remains `acknowledged`. The user may reset it to `raised` manually:

```yaml
review.findings[fnd-id].status: raised
review.findings[fnd-id].resolved_at: null
```

## Lifecycle ownership summary

This table is the authoritative reference for which agents may write which fields. Agents must not make transitions not listed here.

| Field | Created by | Modified by | Terminal states |
|---|---|---|---|
| `problem.open_questions[].status` | `intake-analyst`, `solution-shaper` | `solution-shaper` (→ resolved), user (→ resolved, deferred) | `resolved`, `deferred` |
| `problem.open_questions[].resolved_by` | — | `solution-shaper`, user | — |
| `plan.dag.<slice>.open_questions` | `slice-planner` | Never modified after creation | — |
| `review.findings[].status` | `feature-verifier`, `review-consolidator` | `/fix` (→ acknowledged), `feature-verifier` (→ resolved, → raised), user (→ waived) | `resolved`, `waived` |
| `review.findings[].type` | `feature-verifier`, `review-consolidator` | Never — frozen on creation | — |
| `review.verdict` | `feature-verifier` | `feature-verifier` after every finding status change | `approved` (may revert to `blocked` if new findings raised) |
| `execution.blockers[].resolved_at` | — | User (via manifest edit) | non-null value |
| `plan.dag.<slice>.tasks[].phase` | `slice-planner` | `tdd-builder` (→ implementing, → reviewing), `task-reviewer` (→ done, → implementing), `build-orchestrator`/fix (→ planned, reset only) | `done` (except fix reset) |
| `execution.slice_commits` | `build-orchestrator` | `build-orchestrator` (updated on fix) | — |
| `execution.run_history[].commit_sha` | `build-orchestrator` | `build-orchestrator` (updated on fix) | — |
