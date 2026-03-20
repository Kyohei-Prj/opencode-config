---
name: slice-writer
description: Decompose a shaped feature into a dependency-ordered DAG of slices and tasks. Each slice is a vertical cut — independently buildable and testable. Produces plan.dag entries with depends_on, context blocks, and task acceptance criteria. Do not produce a flat ordered list.
compatibility: opencode
metadata:
  used-by: slice-planner
  load-at: agent definition time
---

## What I do

Break a shaped feature into well-scoped, dependency-ordered slices. Each slice is independently buildable and reviewable. The output is a DAG written into `plan.dag` in `feature.yaml` — not a flat ordered list.

## Core principle

A good slice is the smallest unit of work that:
- Can be built and tested in isolation
- Produces a meaningful, reviewable diff
- Has a clear interface boundary with adjacent slices
- Does not require another slice to be partially complete before it can start

Slices are not layers — don't split "backend slice" from "frontend slice" unless they truly have no coupling. Slices are vertical cuts through the stack that deliver a testable capability.

## Slice sizing by lane

| Lane | Typical slice count | Task count per slice |
|---|---|---|
| small | 1–2 | 1–3 |
| standard | 2–5 | 2–5 |
| epic | 4–10 | 2–6 |

These are guidance ranges, not hard limits. A genuinely complex standard feature may need 6 slices. Use judgment over formula.

## Dependency graph rules

1. **Declare `depends_on` explicitly.** Every slice must declare which other slices it depends on. Root slices (no dependencies) have `depends_on: []`.
2. **No cycles.** A slice may not directly or transitively depend on itself. Check before writing.
3. **Minimize dependencies.** Only add a dependency when the slice genuinely cannot start without the depended-on slice being complete. Artificial sequencing defeats parallelism.
4. **Prefer width over depth.** A wide, shallow DAG (many parallel root slices) is faster to build than a deep chain. Aim for the minimum depth needed to satisfy real ordering constraints.
5. **The orchestrator computes waves.** Do not store wave assignments or slice_order in the manifest. The build-orchestrator derives the execution schedule from the DAG at runtime.

## Slice decomposition procedure

### Step 1 — Identify natural seams

Read `design.components` and `design.integration_points` in the manifest. Each component boundary or integration point is a candidate seam. Ask:
- Can this component be built and tested without the others being complete?
- Does building this component produce an interface that other components will consume?

### Step 2 — Identify the data/contract layer

If the feature introduces new data models, API contracts, or shared interfaces, these almost always form root slices. Nothing else can be tested against a contract that doesn't exist yet.

### Step 3 — Map dependencies

Draw the dependency relationships. Mark which slices produce interfaces and which slices consume them. A consumer slice depends on the producer slice.

### Step 4 — Assign tasks within each slice

Each slice gets 2–6 tasks. Tasks within a slice are sequential (the slice is the unit of parallelism, not individual tasks). Tasks should map to acceptance criteria, not implementation steps.

**Good task framing:**
- "Token generation produces a signed JWT with correct claims"
- "Email sender delivers the magic link to the specified address"
- "Login handler validates token and creates a session"

**Avoid:**
- "Write the token model" (implementation step, not an outcome)
- "Make it work" (not testable)
- "Frontend and backend integration" (too broad, crosses slice boundaries)

### Step 5 — Scope the context block

For each slice, populate `context`:
- `files_touched`: list the files this slice is expected to create or modify. Best-effort at plan time — the builder may discover more.
- `interfaces_consumed`: names of interfaces/contracts this slice reads (e.g. `TokenService`, `EmailQueue`)
- `interfaces_produced`: names of interfaces/contracts this slice exposes for other slices

The context block serves two purposes: it initializes tdd-builder with a scoped working set, and it lets the verifier check interface contracts across slices without re-reading the full codebase.

### Step 6 — Flag open questions

If any `problem.open_questions` with `blocks: true` affect a specific slice, add the question id to `plan.dag.<slice>.open_questions`. The build-orchestrator will halt that slice until the question is resolved.

## Anti-patterns to avoid

**The monolith slice** — one slice that does everything. Defeats parallelism and makes review useless.

**The artificial layer split** — "database slice", "API slice", "UI slice" as separate top-level slices when they're tightly coupled and can't be tested independently. Prefer vertical cuts.

**Premature dependency** — slice B depends on slice A "just in case". If B can start without A being fully complete (e.g. B can be built against a stub), don't add the dependency.

**Over-tasking** — 10+ tasks in a single slice. Break the slice further or consolidate tasks into meaningful outcomes.

**Under-tasking** — 1 task per slice for a standard feature. Each task should represent a distinct testable outcome, not a single function.

## Output contract

Write to `plan.dag` in `feature.yaml` following the schema in `manifest-writer`. After writing, update:
- `feature.status` → `slice_complete`
- `feature.commands.current` → `/slice` or `/shape-slice`
- `feature.commands.next` → `/build`
