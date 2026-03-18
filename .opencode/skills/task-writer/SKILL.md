---
name: task-writer
description: "Canonical template and rules for atomic task list documents at plans/<feature>/phaseN/tasks.md. Load before writing any task file. Tasks must be sized 30min–4h, dependency-ordered, and each linked to a specific file and FR/NFR."
license: MIT
compatibility: opencode
metadata:
  category: workflow
  phase: implementation-planning
  prev-artifact: plans/<feature>/phaseN.md
  next-phase: implementation
---

# Task Writer Skill

This skill defines the exact template and rules for all
`plans/<feature>/phase<N>/tasks.md` files.

A task file is the direct input to the implementation workflow. Every task must
be specific enough that a developer can start coding immediately with no
remaining design decisions, sized to fit in a single focused work session, and
ordered so that working top-to-bottom never produces a dependency conflict.

---

## Document template

```markdown
# Tasks: Phase <N> — <Phase Name>

> **Feature**: <feature-slug>
> **Phase file**: [../phase<N>.md](../phase<N>.md)
> **Total tasks**: <count>
> **Total estimated effort**: <sum of all task estimates>
> **Created**: YYYY-MM-DD
> **Status**: Pending | In progress | Complete

---

## How to use this file

Work through tasks in order from top to bottom. Each task's dependencies are
listed — do not start a task until all its dependencies are marked `[x]`.

Mark a task complete by checking its box:
- `[ ]` → not started
- `[~]` → blocked
- `[x]` → complete

There is no separate chckbox state for "in progress". The active task is tracked by the implementation orchestrator and impl-log.
If a task is marked `[~]`, resolve that blockage before any later task proceeds.

---

## Task list

<!-- ------------------------------------------------------------------ -->
### T-<N>-01 · <Short imperative title> · <S|M|L>

> **Effort**: S (<1h) | M (1-2h) | L (2-4h)
> **Depends on**: none | T-<N>-NN, T-<N>-NN
> **Satisfies**: FR-N, NFR-N
> **Commit message**: `<type>(<scope>): <description>`

**What**: One sentence describing the outcome of this task.

**Files**:
| Action | Path | Description |
|--------|------|-------------|
| Create | `src/…` | What this file contains |
| Modify | `src/…` | What specifically changes |

**Acceptance**:
- [ ] <Binary, verifiable criterion — no subjective language>
- [ ] <Binary, verifiable criterion>

**Notes**: Any constraint, gotcha, or ADR reference the developer must be
aware of. Omit if none.

---
<!-- ------------------------------------------------------------------ -->
### T-<N>-02 · <Short imperative title> · <S|M|L>

> **Effort**: …
> **Depends on**: T-<N>-01
> **Satisfies**: FR-N
> **Commit message**: `…`

**What**: …

**Files**:
| Action | Path | Description |
|--------|------|-------------|

**Acceptance**:
- [ ] …

---
<!-- (repeat for every task) -->

---

## Phase completion checklist

All items below must be checked before closing the phase.

### Functional
- [ ] All T-<N>-NN tasks marked complete
- [ ] All task acceptance criteria verified

### Quality gates
- [ ] `<test command>` passes — 0 failures, 0 errors
- [ ] `<lint/typecheck command>` passes — 0 warnings treated as errors
- [ ] Test coverage ≥ <N>% on new/modified files (or project baseline, whichever is higher)

### Integration
- [ ] Feature works end-to-end in local development environment
- [ ] No regressions in existing test suite

### Phase exit
- [ ] All exit criteria from [phase<N>.md §7](../phase<N>.md) verified ✓
- [ ] Any new open questions added to the architecture doc's §11

---

## Appendix: task index

Quick-reference table of all tasks in this phase.

| Task | Title | Effort | Depends on | Status |
|------|-------|--------|-----------|--------|
| T-<N>-01 | … | S | — | [ ] |
| T-<N>-02 | … | M | T-<N>-01 | [ ] |
```

---

## Task numbering convention

Tasks are numbered `T-<phase>-<sequence>` with zero-padded two-digit sequence:

| Phase | First task | Last task (example) |
|-------|-----------|---------------------|
| 1 | `T-1-01` | `T-1-14` |
| 2 | `T-2-01` | `T-2-09` |
| 3 | `T-3-01` | `T-3-07` |

Never restart the sequence within a phase. Never use letters or other characters.

---

## Effort sizing guide

| Size | Time range | When to use |
|------|-----------|-------------|
| S | 15 min – 1 h | Config changes, single-function additions, simple type definitions, small migrations |
| M | 1 h – 2 h | Implementing a service method + unit test, a single API endpoint + test, a UI component |
| L | 2 h – 4 h | A full repository with multiple methods, a complex service with multiple dependencies, a multi-step UI flow |
| **XL** | **> 4 h** | **Not allowed. Split into multiple tasks.** |

If you cannot split an XL task, flag it with `⚠️ NEEDS SPLIT` and explain why.

---

## Ordering rules (strict)

Apply these rules in order — the first applicable rule determines placement:

1. **Resolve tasks first**: any "Resolve: <question>" task is always T-<N>-01.
2. **Config and environment**: environment variables, package installs, `.env.example` updates.
3. **Schema / migrations**: database migrations before any code that reads or writes the table.
4. **Types and interfaces**: TypeScript types, Zod schemas, interface definitions before implementations.
5. **Data access layer**: repository methods, DB query functions.
6. **Unit tests for data layer**: immediately after the data-layer task they test.
7. **Service / business logic layer**: after the data layer it depends on.
8. **Unit tests for service layer**: immediately after the service task they test.
9. **API / controller layer**: after the service it calls.
10. **Integration / API tests**: immediately after the API task they test.
11. **UI / client layer**: after the API it consumes.
12. **UI tests**: immediately after the UI task they test.
13. **Documentation**: README, JSDoc, inline comments.
14. **Cleanup**: remove temporary scaffolding, TODOs, debug logs.

---

## Commit message format

Every task must specify a conventional commit message:

```
<type>(<scope>): <imperative description under 72 chars>
```

Types: `feat` · `fix` · `refactor` · `test` · `chore` · `docs` · `perf` · `style`

Scope: the module or layer being changed (e.g. `auth`, `user-repo`, `magic-link-api`)

Examples:
- `feat(magic-link): add MagicTokenRepository with create and consume methods`
- `test(magic-link): add unit tests for MagicTokenRepository`
- `feat(auth-api): implement POST /auth/magic-link endpoint`
- `test(auth-api): add integration tests for magic-link endpoint`
- `chore(auth): install nodemailer and add SMTP env vars`

---

## Acceptance criterion rules

Each criterion must be:
- **Binary**: either clearly passes or clearly fails — no "mostly works"
- **Verifiable without the author**: another developer can check it cold
- **Specific**: references exact commands, values, or observable behaviours

Good:
- `Running npm test -- --testPathPattern=magic-token exits 0 with 3 passing`
- `POST /auth/magic-link with invalid email returns 400 { "error": "Invalid email" }`
- `magic_tokens table exists in DB after running migration forward`

Bad:
- `Tests pass` (which tests?)
- `API works correctly` (what does correct mean?)
- `Code is clean` (not verifiable)

---

## File path rules

- Paths must be relative to the project root (no leading `/`).
- Use the exact path style of the existing codebase (e.g. `src/` vs `app/`).
- If creating a new directory, include a task for `mkdir` as part of the first
  task that writes to that directory (note it in the Files table, not a
  separate task).

---

## Mandatory task categories

Every phase task file must contain at least one task from each of these
categories (unless the phase genuinely has no work in that category — explain why):

| Category | Typical task title pattern |
|----------|---------------------------|
| Setup / config | "Add <X> env var to `.env.example`" |
| Data layer | "Implement `<Repository>` with `<methods>`" |
| Business logic | "Implement `<Service>.<method>()` for `<use case>`" |
| API / interface | "Implement `<METHOD> <path>` endpoint" |
| Tests | "Add unit/integration tests for `<component>`" |
| Phase exit gate | "Verify phase exit criteria and completion handoff" |

The last task in every task file must always be:

```markdown
### T-<N>-NN · Verify phase exit criteria · S

> **Effort**: S
> **Depends on**: T-<N>-NN (all prior tasks)
> **Satisfies**: Phase <N> exit criteria
> **Commit message**: `chore(<feature>): verify phase <N> complete`

**What**: Run the phase verification commands, confirm all exit criteria in phase<N> §7 are satisfied, and hand off to the implementation orchestrator for final phase completion. 

**Files**:
| Action | Path | Description |
|--------|------|-------------|
| Verify | `plans/<feature>/phase<N>.md` | Confirm all exit criteria are satisfied; do not update Status directly |

**Acceptance**:
- [ ] All exit criteria in `plans/<feature>/phase<N>.md` §7 are checked `[x]`
- [ ] `<test command>` exits 0
- [ ] Phase is ready for `impl-orchestrator` + `test-runner` completion handling
```

---

## Quality checklist

Before writing the file, confirm:

- [ ] Every task has a unique `T-<N>-NN` ID with no gaps
- [ ] No task is sized XL (> 4h)
- [ ] Ordering follows the strict ordering rules above
- [ ] Every functional task has an adjacent test task
- [ ] Every task cites at least one FR-N or NFR-N (or "Phase exit criteria")
- [ ] Every task has a valid conventional commit message
- [ ] The final task is "Verify phase exit criteria"
- [ ] The appendix task index matches all tasks in the file
- [ ] File saved to `plans/<feature-slug>/phase<N>/tasks.md`
