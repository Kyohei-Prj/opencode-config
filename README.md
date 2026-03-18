# OpenCode Dev Workflow

A complete AI-driven development pipeline from vague idea to reviewed,
committed, shippable code — structured as slash commands, sub-agents, and skills.

```
/spec <idea>               →  docs/<feature>/requirements.md
/design <feature>          →  docs/<feature>/architecture.md
/plan <feature>            →  plans/<feature>/phase<N>.md
                               plans/<feature>/phase<N>/tasks.md
/implement <feature> <N>   →  working, committed, tested code
                               plans/<feature>/phase<N>/impl-log.md
/review <feature> <N>      →  plans/<feature>/phase<N>/review.md
```

---

## Quick start

```bash
/spec add passwordless login via magic link
/design passwordless-login
/plan passwordless-login
/implement passwordless-login 1
/review passwordless-login 1
# fix any 🔴 blocking findings, then:
/implement passwordless-login 2
/review passwordless-login 2
```

---

## Full file layout

```
.opencode/
├── opencode.json
│
├── commands/
│   ├── spec.md                              # Stage 1
│   ├── design.md                            # Stage 2
│   ├── plan.md                              # Stage 3
│   ├── implement.md                         # Stage 4
│   └── review.md                            # Stage 5
│
├── agents/
│   ├── requirements-analyst.md              # Stage 1
│   ├── architecture-designer.md             # Stage 2
│   ├── phase-planner.md                     # Stage 3 orchestrator
│   ├── task-decomposer.md                   # Stage 3 leaf
│   ├── impl-orchestrator.md                 # Stage 4 orchestrator
│   ├── tdd-implementer.md                   # Stage 4 leaf (one per task)
│   ├── test-runner.md                       # Stage 4 leaf (phase exit check)
│   ├── review-orchestrator.md               # Stage 5 orchestrator
│   ├── code-reviewer.md                     # Stage 5 leaf (one per task)
│   └── review-consolidator.md              # Stage 5 leaf (report writer)
│
└── skills/
    ├── requirements-writer/SKILL.md         # Stage 1 template
    ├── architecture-writer/SKILL.md         # Stage 2 template
    ├── phase-writer/SKILL.md                # Stage 3 template
    ├── task-writer/SKILL.md                 # Stage 3 template
    ├── tdd-cycle/SKILL.md                   # Stage 4 TDD rules
    ├── impl-log-writer/SKILL.md             # Stage 4 log format
    ├── review-standards/SKILL.md            # Stage 5 review lenses + findings format
    └── review-report-writer/SKILL.md        # Stage 5 report template

docs/<feature>/
├── requirements.md                          # /spec output
└── architecture.md                          # /design output

plans/<feature>/
├── phase1.md                                # /plan output
├── phase1/
│   ├── tasks.md                             # /plan output
│   ├── impl-log.md                          # /implement output
│   └── review.md                            # /review output
├── phase2.md
└── phase2/
    ├── tasks.md
    ├── impl-log.md
    └── review.md
```

---

## Stage 1 — `/spec <idea>`

| | |
|---|---|
| Agent | `requirements-analyst` |
| Skill | `requirements-writer` |
| Output | `docs/<feature>/requirements.md` |

Explores the codebase, expands a vague idea into a full spec (goals, non-goals,
user stories, FR/NFR with priorities, acceptance criteria, open questions).

---

## Stage 2 — `/design <feature>`

| | |
|---|---|
| Agent | `architecture-designer` |
| Skill | `architecture-writer` |
| Input | `docs/<feature>/requirements.md` |
| Output | `docs/<feature>/architecture.md` |

Produces a 12-section architecture document: component diagrams (Mermaid),
data schema, API contracts, security, ADRs, and phased implementation plan.

---

## Stage 3 — `/plan <feature>`

| | |
|---|---|
| Orchestrator | `phase-planner` |
| Leaf agent | `task-decomposer` (one per phase) |
| Skills | `phase-writer`, `task-writer` |
| Output | `plans/<feature>/phase<N>.md` + `plans/<feature>/phase<N>/tasks.md` |

Breaks the architecture into phase files and atomic, dependency-ordered task
lists. Tasks are sized S/M/L (max 4h), each with a conventional commit message
and binary acceptance criteria.

---

## Stage 4 — `/implement <feature> <phase>`

| | |
|---|---|
| Orchestrator | `impl-orchestrator` |
| Leaf agents | `tdd-implementer` (one per task), `test-runner` (once per phase) |
| Skills | `tdd-cycle`, `impl-log-writer` |
| Output | Committed code + `plans/<feature>/phase<N>/impl-log.md` |

Implements one phase task-by-task using strict TDD (RED→GREEN→REFACTOR→VERIFY).
Each task runs in its own isolated sub-agent context to preserve context window.
Supports resume after interruption via `impl-log.md`.

---

## Stage 5 — `/review <feature> <phase>`

| | |
|---|---|
| Orchestrator | `review-orchestrator` |
| Leaf agents | `code-reviewer` (one per task), `review-consolidator` (once) |
| Skills | `review-standards`, `review-report-writer` |
| Input | Phase file + tasks.md + impl-log.md + architecture.md |
| Output | `plans/<feature>/phase<N>/review.md` |

Reviews a completed phase across three structured lenses. Produces a report
with findings categorised by severity and a shippability verdict.

### Three-agent pipeline

```
/review passwordless-login 1
         │
         ▼
[review-orchestrator]           — reads manifest, dispatches per task
  (read-only: no write/edit)
         │
         ├─▶ @code-reviewer  (T-1-01)  — 3 lenses, focused context
         │       └─ returns findings object
         │
         ├─▶ @code-reviewer  (T-1-02)  — fresh context, task-scoped
         │       └─ returns findings object
         │
         │   … (sequential, one per task)
         │
         └─▶ @review-consolidator      — findings objects only, no source code
                 └─ writes plans/<feature>/phase1/review.md
```

### The three review lenses

Every task is reviewed on three independent axes:

| Lens | Question | Key checks |
|------|----------|-----------|
| **Spec conformance** | Does the code do what the task required? | Acceptance criteria coverage, file paths, FR/NFR satisfaction, commit message |
| **TDD quality** | Are the tests an honest spec of behaviour? | Structure/naming, tautology detection, isolation, RED-first evidence |
| **Architecture conformance** | Does the code match the agreed design? | Component location, layer discipline, ADR compliance, API contract, schema |

### Finding severities

| Severity | Meaning | Examples |
|----------|---------|---------|
| 🔴 **Blocking** | Must fix before shipping | ADR violation, missing test for acceptance criterion, wrong API status code, layer discipline breach |
| 🟡 **Non-blocking** | Fix soon, doesn't block shipping | Missing error case test, non-descriptive test name, loose assertion |
| 🔵 **Suggestion** | Optional improvement | Naming, extractable helper, test factory opportunity |

### Verdict rules

| Verdict | Condition |
|---------|-----------|
| ✅ Approved | Zero blocking and non-blocking findings |
| ✅ Approved with notes | Zero blocking, one or more non-blocking |
| 🔴 Changes required | One or more blocking findings |

### Context isolation in review

The same discipline as Stage 4: `@code-reviewer` gets only the current task's
files and the architecture sections those files reference. It never sees other
tasks' code. `@review-consolidator` never sees source code at all — only the
findings objects. This keeps each invocation well within context limits
regardless of how many tasks or files the phase contains.

---

## Agent permission model

| Agent | Write files | Bash | Spawns |
|-------|------------|------|--------|
| `requirements-analyst` | `docs/` | mkdir, find, ls | — |
| `architecture-designer` | `docs/` | mkdir, find, ls, cat | @explore |
| `phase-planner` | `plans/` | mkdir, find, ls, cat | @task-decomposer |
| `task-decomposer` | `plans/` | mkdir, find, ls, cat | none |
| `impl-orchestrator` | `plans/` | git add/commit/status, find, cat | @tdd-implementer, @test-runner |
| `tdd-implementer` | `src/` (project) | test runners, lint, typecheck, cat, find | none |
| `test-runner` | none (edit: deny) | test runners, lint, typecheck, cat | none |
| `review-orchestrator` | none (edit: deny) | git log/diff, find, cat | @code-reviewer, @review-consolidator |
| `code-reviewer` | none (edit: deny) | cat, find, ls, git show | none |
| `review-consolidator` | `plans/` | mkdir only | none |

---

## Installation

```bash
cp -r .opencode/ /path/to/your/project/
cd /path/to/your/project
opencode
/init
```

Commit `.opencode/`, `docs/`, and `plans/` to version control.
Review reports (`review.md`) are worth committing — they are the quality record.
