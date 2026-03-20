# OpenCode Dev Workflow

An AI-driven development workflow for [OpenCode](https://opencode.ai/docs). A single feature manifest file drives every stage — planning, implementation, review, and recovery — with full parallel build support and a clean re-entry path at every failure point.

---

## Table of contents

- [How it works](#how-it-works)
- [Installation](#installation)
- [Quick start](#quick-start)
- [Commands](#commands)
- [Lanes](#lanes)
- [The manifest](#the-manifest)
- [Parallel builds](#parallel-builds)
- [Git integration](#git-integration)
- [Recovering from failures](#recovering-from-failures)
- [Reference: workflow files](#reference-workflow-files)
- [Reference: repository layout](#reference-repository-layout)
- [Concepts glossary](#concepts-glossary)

---

## How it works

The workflow is a five-stage pipeline:

```
/intake <idea>          →  creates workflow/<feature>/feature.yaml
/shape-slice <feature>  →  explores codebase, writes design + task plan
/build <feature>        →  implements tasks in parallel waves, TDD + per-task review
/verify <feature>       →  manifest-first verification, shippability verdict
/fix <feature> <fnd-id> →  targeted fix cycle for any blocking finding
```

One file — `feature.yaml` — is the canonical source of truth throughout. Generated markdown files (`brief.md`, `review.md`, run logs) are read-only views derived from the manifest. If they ever disagree, the manifest wins.

### Core design principles

**Manifest-first.** Every agent reads and writes `feature.yaml`. No agent reads generated markdown as an input. This means any stage can be safely re-run, interrupted, or resumed without losing state.

**Growing manifest.** The manifest starts slim at intake (three sections) and grows as stages complete. Sections are only added when they have real content — no null-filled placeholders from day one.

**Lanes calibrate rigor.** Features are classified as `small`, `standard`, or `epic` at intake. Lane choice affects exploration depth, the shape/slice path, and verification thoroughness. The lane confirmation gate requires your explicit sign-off before anything is written.

**Parallel by default.** The build stage computes a dependency graph (DAG) from your slice plan and executes independent slices in parallel waves. `--concurrency N` controls how many slices run simultaneously.

**One commit per slice.** When all tasks in a slice are reviewed and approved, the build-orchestrator commits those changes to a `feature/<slug>` branch. The commit SHA is recorded in the manifest, tying every slice back to an auditable point in git history.

**Clean recovery.** Every failure point has an explicit re-entry path. Interrupted builds resume from the last incomplete wave. Blocked verifications route individual findings through a scoped fix cycle.

---

## Installation

Copy the `.opencode/` directory into your project root:

```bash
cp -r .opencode/ /path/to/your/project/
cd /path/to/your/project
opencode
```

That's it. The workflow is self-contained — no external dependencies beyond OpenCode itself.

### What gets installed

```
.opencode/
├── opencode.json               ← registers all commands, agents, and skills
├── commands/                   ← 8 slash commands (prompt templates)
├── agents/                     ← 8 AI subagents
└── skills/                     ← 9 skill folders, each containing a SKILL.md
    ├── lane-classifier/
    ├── slice-writer/
    ├── tdd-cycle/
    ├── task-review-standards/
    ├── verify-checklist/
    ├── manifest-writer/
    ├── brief-writer/
    ├── evidence-log-writer/
    └── review-report-writer/
```

Skills follow the [OpenCode skills format](https://opencode.ai/docs/skills/) — each skill is a folder containing a `SKILL.md` with YAML frontmatter and a prompt body. Agents are [OpenCode subagents](https://opencode.ai/docs/agents/) defined as markdown files with frontmatter (`mode: subagent`, `hidden: true`, `permission` blocks). Commands are [OpenCode custom commands](https://opencode.ai/docs/commands/) — markdown files with frontmatter and a prompt template body.

---

## Quick start

### Standard feature (the common path)

```bash
/intake add passwordless login via magic link
# → confirms lane, creates workflow/passwordless-login/feature.yaml

/shape-slice passwordless-login
# → explores codebase, writes design + task plan, generates brief.md

/build passwordless-login --concurrency 2
# → implements slices in parallel waves, commits each slice to feature/passwordless-login

/verify passwordless-login
# → checks manifest completeness, runs test suite, produces verdict
```

### Epic feature (large or architecturally significant)

```bash
/intake replace the authentication system
# → classifies as epic, confirms lane

/shape replace-auth-system
# → deep codebase exploration, design decisions — stops for your review

# Review workflow/replace-auth-system/feature.yaml, then:
/slice replace-auth-system
# → breaks the reviewed design into a slice DAG, generates brief.md

/build replace-auth-system --concurrency 3
/verify replace-auth-system
```

### Small feature (single-component change)

```bash
/intake add a loading spinner to the submit button
# → classifies as small, confirms lane

/shape-slice loading-spinner
# → lightweight pass: minimal design, 1–2 slices, 1–3 tasks each

/build loading-spinner
/verify loading-spinner
```

---

## Commands

### `/intake <idea>`

**The entry point for every feature.** Creates `workflow/<slug>/feature.yaml` from a plain-language idea.

```
/intake add passwordless login via magic link
/intake "build a CSV export for the monthly activity report"
```

Before writing anything, the command pauses and shows:

```
Feature:   Passwordless Login
Slug:      passwordless-login
Lane:      standard
Rationale: Classified as standard because it introduces a new auth flow touching API, email, and session layers.

Confirm? [y / n / small / standard / epic]
```

Respond with `y` to accept, `n` to cancel, or type a lane name to override.

---

### `/shape-slice <slug>`

**For small and standard lanes.** Explores the codebase and produces both the design and the task plan in a single pass.

```
/shape-slice passwordless-login
```

What it writes to the manifest:
- `design` — codebase findings, decisions, components, rollout strategy, risks
- `plan` — slice DAG with tasks, acceptance criteria, and context blocks

What it generates:
- `workflow/<slug>/brief.md` — human-readable summary of the plan

---

### `/shape <slug>` and `/slice <slug>`

**For epic lanes only.** Splits the shape and slice stages so you can review the design before committing to a task plan.

```
/shape replace-auth-system
# → writes design section, prints decisions for review, stops

/slice replace-auth-system
# → reads the reviewed design, writes plan section, generates brief.md
```

Use this when the design genuinely needs a separate sign-off pass before work is broken into tasks. For standard features, use `/shape-slice` — the extra round-trip adds ceremony without benefit.

---

### `/build <slug> [scope] [--concurrency N]`

**Implements all planned tasks.** Reads the slice DAG, schedules slices into parallel waves, runs each task through a red→green→refactor TDD cycle with per-task review, and commits each completed slice to the `feature/<slug>` branch.

```
/build passwordless-login                    # sequential, one slice at a time
/build passwordless-login --concurrency 3   # up to 3 slices in parallel
/build passwordless-login auth-token        # build one slice only
/build passwordless-login task-003          # build one task only
```

What happens per task:
1. `tdd-builder` writes a failing test, implements the minimum to pass, refactors
2. `task-reviewer` checks acceptance criteria coverage, test quality, and scope
3. On pass: task advances to `done`; when all tasks in the slice are done, the slice is committed to `feature/<slug>`
4. On fail: rejection reason sent back to `tdd-builder` for a targeted retry

If a task is rejected 3 times without passing, the build pauses and surfaces the issue for manual inspection.

---

### `/verify <slug>`

**Produces the shippability verdict.** Checks the manifest for completeness before touching any code, then runs the test suite, and generates `review.md`.

```
/verify passwordless-login
/verify passwordless-login --finding fnd-002   # re-verify after /fix
```

Verification stages (in order):
1. **Execution completeness** — all tasks `done`, no open blockers, no unresolved blocking questions (manifest only)
2. **Interface contracts** — produced/consumed interfaces consistent across slices (manifest + light code)
3. **Test suite** — suite passes, acceptance criteria covered (code)
4. **Design intent** — components and rollout strategy implemented (epic lane only)

Verdict is either `approved` (ready to merge) or `blocked` (one or more findings must be fixed).

---

### `/fix <slug> <fnd-id>`

**Resolves a specific blocking finding** from a failed verify without re-running the full build.

```
/fix passwordless-login fnd-001
/fix passwordless-login fnd-002
```

What happens:
1. Finding is marked `acknowledged` (prevents re-raise mid-fix)
2. Affected task(s) are reset and re-built through the full TDD + review cycle
3. A fix commit is added to the feature branch (`fix(<slice>): resolve <fnd-id>`)
4. Verification runs scoped to the fixed finding
5. If resolved and no blocking findings remain: verdict flips to `approved`

Some findings don't require a code change — they require a manifest update (e.g. resolving an open question, marking a blocker resolved). For these, update `feature.yaml` directly and then run `/fix` — it detects the manifest-only case and skips the build cycle.

---

### `/resume <slug>`

**Continues an interrupted build** from the last incomplete wave. Use this instead of re-running `/build` after a crash, timeout, or blocked open question.

```
/resume passwordless-login
```

The orchestrator reads `execution.waves`, skips all completed work, and picks up exactly where execution stopped. Tasks that were mid-implementation get a fresh run log; tasks that were in review re-invoke the reviewer against the existing code. Already-committed slices are not re-committed.

---

## Lanes

Lane choice is made once at `/intake` and affects the entire downstream workflow. The `lane-classifier` skill proposes a lane automatically — you confirm, cancel, or override.

| Lane | When to use | Shape/slice path | Build rigor | Verification |
|---|---|---|---|---|
| `small` | Single-component change, hours of work | `/shape-slice` (lightweight) | 1–2 slices, 1–3 tasks each | Stages 1–3 |
| `standard` | Multi-component feature, days of work | `/shape-slice` (full) | 2–5 slices, 2–5 tasks each | Stages 1–3 |
| `epic` | Architectural change, weeks of work | `/shape` then `/slice` | 4–10 slices, 2–6 tasks each | Stages 1–4 |

**When in doubt, round up.** An epic treated as standard misses the design sign-off gate. A standard treated as epic costs some extra ceremony. A standard treated as small gets under-designed.

You can override the proposed lane at the confirmation gate by typing the lane name instead of `y`:

```
Confirm? [y / n / small / standard / epic]
> standard    ← override
```

---

## The manifest

`workflow/<slug>/feature.yaml` is the single source of truth. It grows as stages complete — never pre-populated with empty sections.

### What's in the manifest at each stage

```
After /intake:
  meta         schema version, lane confirmation record
  feature      slug, title, lane, status, summary, timestamps
  problem      statement, goals, users, open questions (seeded)

After /shape-slice or /shape + /slice:
  + design     findings, decisions, components, rollout, risks
  + plan       slice DAG with tasks, context blocks, open question flags

After /build:
  + execution  wave schedule, run history (with commit SHAs), slice_commits, blockers

After /verify:
  + review     findings, verdict, final review summary
```

### The manifest always wins

Generated files are views, not inputs:

| File | What it is |
|---|---|
| `workflow/<slug>/brief.md` | Human-readable plan summary (generated after `/slice`) |
| `workflow/<slug>/review.md` | Shippability report (generated after `/verify`) |
| `workflow/<slug>/runs/<run-id>.md` | Task execution evidence (generated during `/build`) |

If any generated file disagrees with `feature.yaml`, ignore the generated file. Re-run the relevant command to regenerate it from the manifest.

### Feature status lifecycle

```
intake_complete → shaping → shape_complete → slicing → slice_complete
  → building → build_complete → verifying → verified
                                                     ↘ blocked
```

The `feature.commands.next` field in the manifest always tells you what to run next.

### Open questions

Open questions seeded at intake or added during shape can block specific slices. A question with `blocks: true` halts the build-orchestrator when it reaches the affected slice.

To unblock: update the question status in `feature.yaml` and run `/resume <slug>`:

```yaml
problem:
  open_questions:
    - id: oq-001
      text: "Should magic links be single-use or time-bounded only?"
      status: resolved       # was: open
      resolved_by: "user"
      blocks: true
```

---

## Parallel builds

The build stage computes a dependency graph from `plan.dag` and schedules independent slices into waves.

### How waves work

Given this DAG:

```yaml
plan:
  dag:
    auth-token:
      depends_on: []
    email-sender:
      depends_on: []
    magic-link-handler:
      depends_on: [auth-token, email-sender]
    login-ui:
      depends_on: [magic-link-handler]
```

The orchestrator computes:

```
Wave 1:  auth-token, email-sender      ← no dependencies, run in parallel
Wave 2:  magic-link-handler            ← depends on both wave 1 slices
Wave 3:  login-ui                      ← depends on wave 2
```

With `--concurrency 2`, wave 1 runs both slices simultaneously. Wave 2 starts only after both wave 1 slices are fully done (all tasks reviewed, approved, and committed).

### Concurrency model

`--concurrency N` controls slice-level parallelism, not task-level. Tasks within a slice are always sequential — task-reviewer must approve task N before task N+1 begins.

```
/build passwordless-login --concurrency 1    # default: one slice at a time
/build passwordless-login --concurrency 3    # up to 3 slices simultaneously
```

### Execution state in the manifest

The wave schedule and slice commits are written to `execution` as the build runs:

```yaml
execution:
  concurrency: 2
  waves:
    - wave: 1
      slices: [auth-token, email-sender]
      status: complete
      started_at: "2026-03-18T14:00:00Z"
      completed_at: "2026-03-18T14:45:00Z"
    - wave: 2
      slices: [magic-link-handler]
      status: running
      started_at: "2026-03-18T14:45:00Z"
      completed_at: null
  slice_commits:
    auth-token: "a1b2c3d4e5f6..."
    email-sender: "b2c3d4e5f6a1..."
```

---

## Git integration

The build stage automatically maintains a `feature/<slug>` branch. No manual git operations are needed during the build.

### Branch lifecycle

On the first slice commit of a fresh build, `build-orchestrator` creates the branch:

```
git checkout -b feature/passwordless-login
```

Each subsequent slice commits to that branch. When all slices are complete, the branch contains one commit per slice, ready to open as a pull request.

### Commit format

Each slice produces a structured commit message:

```
feat(auth-token): Token generation and validation

Tasks: task-001, task-002, task-003
Run logs: auth-token-task-001-20260318-143022, ...
Feature: passwordless-login
```

### Commit traceability in the manifest

Every slice commit SHA is recorded in `execution.slice_commits`, and each run history entry carries the SHA of the commit it landed in:

```yaml
execution:
  slice_commits:
    auth-token: "a1b2c3d..."
  run_history:
    - run_id: auth-token-task-001-20260318-143022
      slice: auth-token
      task: task-001
      status: pass
      commit_sha: "a1b2c3d..."
```

This makes it possible to trace any finding from `/verify` back to the exact commit that introduced it.

### Fix commits

When `/fix` resolves a blocking finding, a new commit is added to the feature branch:

```
fix(auth-token): resolve fnd-001

Finding: fnd-001 — Check 3.1 — token_expires_after_ttl test failing
Run log: auth-token-task-002-20260318-160044
```

`execution.slice_commits` is updated to the new SHA.

---

## Recovering from failures

### Build interrupted mid-wave

```bash
/resume passwordless-login
```

The orchestrator reads `execution.waves`, skips complete waves, and restarts from the first incomplete wave. Tasks already `done` are not re-run. Slices that were already committed are not re-committed.

### Verify returns blocked

```
Verdict: BLOCKED

Blocking findings:
  fnd-001  Check 3.1 — 2 tests failing in auth-token slice
  fnd-002  Check 1.4 — open question oq-001 not resolved before build
```

Fix each blocking finding:

```bash
/fix passwordless-login fnd-001
/fix passwordless-login fnd-002
```

Each fix runs the minimum affected build + review cycle, commits the fix to the feature branch, then runs scoped re-verification. When all blocking findings are resolved, the verdict automatically flips to `approved`.

### Slice blocked by an open question

```
⚠ Slice magic-link-handler is blocked by open question oq-001:
  "Should magic links be single-use or time-bounded only?"
```

1. Resolve the question in `feature.yaml`
2. Run `/resume <slug>`

### Task rejected repeatedly

If a task is rejected 3 times by the task-reviewer, the build pauses:

```
⚠ Task task-003 in auth-token has failed review 3 times.
  Last rejection: Acceptance criterion 2 (token expiry) has no test.
```

Inspect the run logs in `workflow/<slug>/runs/`, address the issue manually, then:
- Set the task `phase` back to `reviewing` in `feature.yaml` to retry review only
- Or set it back to `planned` to re-run the full TDD cycle

---

## Reference: workflow files

### Commands

| Command | Lane | What it does |
|---|---|---|
| `/intake <idea>` | all | Creates the initial manifest with lane confirmation gate |
| `/shape-slice <slug>` | small, standard | Explores codebase, writes design + plan in one pass |
| `/shape <slug>` | epic | Explores codebase, writes design, stops for sign-off |
| `/slice <slug>` | epic | Breaks reviewed design into slice DAG |
| `/build <slug>` | all | Parallel wave execution with TDD + per-task review + git commits per slice |
| `/verify <slug>` | all | Manifest-first verification, produces shippability verdict |
| `/resume <slug>` | all | Resumes interrupted build from last incomplete wave |
| `/fix <slug> <fnd-id>` | all | Scoped fix cycle for a specific blocking finding |

### Agents

All agents are OpenCode subagents (`mode: subagent`, `hidden: true`) — invoked by commands or other agents, never directly by the user.

| Agent | Invoked by | What it does |
|---|---|---|
| `intake-analyst` | `/intake` | Classifies lane, seeds manifest, runs confirmation gate |
| `solution-shaper` | `/shape`, `/shape-slice` | Explores codebase, completes problem + design sections |
| `slice-planner` | `/slice`, `/shape-slice` | Builds slice DAG, assigns tasks, generates `brief.md` |
| `build-orchestrator` | `/build`, `/resume` | Computes waves, fans out builders, manages git commits per slice |
| `tdd-builder` | `build-orchestrator` | Implements one task via red→green→refactor |
| `task-reviewer` | `build-orchestrator` | Reviews each completed task before it can advance |
| `feature-verifier` | `/verify` | Runs all verification checks, writes verdict |
| `review-consolidator` | `feature-verifier` | Aggregates patterns across run history (>10 tasks) |

### Skills

Skills follow the [OpenCode skills format](https://opencode.ai/docs/skills/): each skill is a folder under `.opencode/skills/` containing a `SKILL.md` with YAML frontmatter and a prompt body.

**Behavioral** — shape how agents reason (loaded via the `skill` tool at agent start):

| Skill | Used by |
|---|---|
| `lane-classifier` | `intake-analyst` |
| `slice-writer` | `slice-planner` |
| `tdd-cycle` | `tdd-builder` |
| `task-review-standards` | `task-reviewer` |
| `verify-checklist` | `feature-verifier` |

**Format** — enforce output structure (loaded at write time):

| Skill | Used by |
|---|---|
| `manifest-writer` | `intake-analyst`, `solution-shaper`, `slice-planner`, `build-orchestrator`, `feature-verifier` |
| `brief-writer` | `slice-planner` |
| `evidence-log-writer` | `tdd-builder` |
| `review-report-writer` | `feature-verifier`, `review-consolidator` |

---

## Reference: repository layout

```
.opencode/
├── opencode.json
├── commands/
│   ├── intake.md
│   ├── shape-slice.md
│   ├── shape.md
│   ├── slice.md
│   ├── build.md
│   ├── verify.md
│   ├── resume.md
│   └── fix.md
├── agents/
│   ├── intake-analyst.md
│   ├── solution-shaper.md
│   ├── slice-planner.md
│   ├── build-orchestrator.md
│   ├── tdd-builder.md
│   ├── task-reviewer.md
│   ├── feature-verifier.md
│   └── review-consolidator.md
└── skills/
    ├── lane-classifier/
    │   └── SKILL.md
    ├── slice-writer/
    │   └── SKILL.md
    ├── tdd-cycle/
    │   └── SKILL.md
    ├── task-review-standards/
    │   └── SKILL.md
    ├── verify-checklist/
    │   └── SKILL.md
    ├── manifest-writer/
    │   └── SKILL.md
    ├── brief-writer/
    │   └── SKILL.md
    ├── evidence-log-writer/
    │   └── SKILL.md
    └── review-report-writer/
        └── SKILL.md

workflow/                          ← created when you run /intake
└── <feature-slug>/
    ├── feature.yaml               ← canonical source of truth
    ├── brief.md                   ← generated after /slice
    ├── review.md                  ← generated after /verify
    └── runs/
        └── <run-id>.md            ← generated per task during /build
```

---

## Concepts glossary

**Manifest** — `workflow/<slug>/feature.yaml`. The canonical source of truth. All agents read from and write to this file. Generated files are derived from it and never override it.

**Lane** — the rigor level assigned at intake: `small`, `standard`, or `epic`. Controls exploration depth, shape/slice path, task counts, and verification thoroughness.

**Slice** — a vertically cut, independently buildable and testable unit of work within a feature. Slices are the unit of parallelism in the build stage and the unit of git commits.

**DAG** — directed acyclic graph. The slice plan is stored as a DAG where each slice declares its `depends_on` list. The build-orchestrator computes execution waves from this graph.

**Wave** — a maximal set of slices all of whose dependencies are complete. Slices in the same wave can run in parallel up to the concurrency limit.

**Task** — a concrete, testable unit of work within a slice. Tasks within a slice are sequential. Each task has acceptance criteria and goes through a full TDD cycle followed by per-task review.

**Finding** — a specific issue recorded during `/verify`. Type is `blocking`, `non-blocking`, or `suggestion`. Only blocking findings prevent approval. Findings move through a lifecycle: `raised → acknowledged → resolved` (or `waived`).

**Open question** — an explicit unknown recorded in the manifest. Questions with `blocks: true` halt the build-orchestrator when it reaches the affected slice.

**Verdict** — the output of `/verify`: either `approved` (ready to merge) or `blocked` (one or more blocking findings unresolved).

**TDD cycle** — red (failing test) → green (minimum implementation) → refactor (clean up without changing behaviour). Every task goes through this loop. Evidence is captured in a run log.

**Run log** — `workflow/<slug>/runs/<run-id>.md`. Records the red/green/refactor phases, test output, and notes for one task execution. Read-only once written; retried tasks get a new run log.

**Feature branch** — `feature/<slug>`. Created automatically on the first slice commit of a build. Each completed slice adds one commit. Fix cycles add fix commits. The branch is ready to open as a pull request once `/verify` returns `approved`.

**Slice commit** — a git commit made by `build-orchestrator` after all tasks in a slice pass review. Uses conventional commit format (`feat(<slice>): <title>`). The SHA is recorded in `execution.slice_commits` and in each affected run history entry.
