---
name: lane-classifier
description: Classify a feature idea as small, standard, or epic using signal-based rules. Produces a proposed_lane and a one-sentence lane_rationale. Output is a proposal only — do not write to the manifest until the user confirms at the lane gate.
compatibility: opencode
metadata:
  used-by: intake-analyst
  load-at: agent definition time
---

## What I do

Classify a feature idea into one of three lanes — `small`, `standard`, or `epic` — and produce a one-sentence rationale. The output is a proposal, not a final decision. The lane confirmation gate in `/intake` presents the proposal to the user before it is written to the manifest.

## Lane definitions

### small

A self-contained change with a narrow blast radius. Can be understood, implemented, and reviewed in a single focused session. No cross-cutting concerns, no schema migrations, no new external dependencies, no rollout strategy needed.

**Signals:**
- Single file or single component change
- No new API surface
- No database schema changes
- No impact on other features or services
- Reversible without a migration
- Estimated effort: hours, not days

**Examples:**
- Add a field to an existing form
- Change a copy string
- Add a helper utility function
- Increase a timeout value
- Add a missing index to an existing table (if trivial)

### standard

The default lane. A well-scoped feature with clear boundaries but enough moving parts to benefit from explicit design, task breakdown, and TDD. May touch multiple components, introduce a new API endpoint, or require a minor schema change.

**Signals:**
- 2–5 components or files meaningfully changed
- New API endpoint or new data model
- Requires coordinated changes across layers (e.g. DB + API + UI)
- Straightforward rollout — no flag needed, or a simple flag
- Estimated effort: days

**Examples:**
- Add passwordless login via magic link
- Implement a user notification preference screen
- Add CSV export to an existing report
- Introduce a new webhook event type

### epic

A large or architecturally significant change. Requires design sign-off before planning. May span multiple teams, introduce breaking changes, require a phased rollout, or have meaningful compatibility and observability concerns.

**Signals:**
- Touches core infrastructure or cross-cutting concerns
- Introduces a new service, subsystem, or external dependency
- Requires a rollout strategy (feature flag, phased, migration)
- Breaking change to a public API or data contract
- Meaningful risk of regressions in unrelated areas
- Estimated effort: weeks
- Design decisions genuinely benefit from a separate review pass before slicing

**Examples:**
- Replace the authentication system
- Migrate from a monolith to a service boundary
- Add multi-tenancy support
- Introduce a new background job infrastructure
- Major database schema migration affecting multiple tables

## Classification procedure

1. **Read the raw idea.** Extract the core action and the scope it implies.
2. **Check for epic signals first.** If any epic signal is present, classify as `epic` unless the idea is clearly too small for it.
3. **Check for small signals.** If all small signals are met and no standard or epic signals are present, classify as `small`.
4. **Default to `standard`** when signals are mixed or unclear. Prefer over-scoping to under-scoping — a standard feature treated as small gets under-designed; the cost is higher than over-engineering a genuinely small change.
5. **Write the rationale.** One sentence. Name the primary signal that drove the decision. Do not hedge or list multiple reasons — pick the most important one.

## Rationale format

```
Classified as <lane> because <primary signal in one clause>.
```

Examples:
- `Classified as small because this only changes a single UI label with no API or data impact.`
- `Classified as standard because it introduces a new API endpoint and touches three coordinated layers.`
- `Classified as epic because it replaces a core authentication subsystem with a phased rollout requirement.`

## Output contract

Return exactly two fields for the confirmation gate to display:

```yaml
proposed_lane: small | standard | epic
lane_rationale: <one sentence>
```

Do not write these to the manifest. The intake-analyst writes them after the user confirms.

## Misclassification cost

| Direction | Cost |
|---|---|
| Epic treated as small | Under-designed. Risks discovered late in build or verify. High rework cost. |
| Small treated as epic | Over-engineered. Unnecessary ceremony. Low cost but wasted time. |
| Standard treated as epic | Mild over-engineering. Acceptable. |
| Epic treated as standard | Missing design sign-off gate. Risks discovered at slice or build. Medium cost. |

When in doubt, round up.
