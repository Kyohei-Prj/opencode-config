---
name: phase-writer
description: "Canonical template and formatting rules for per-phase plan documents at plans/<feature>/phaseN.md. Load before writing any phase file. Each phase file is the primary input to task-decomposer."
license: MIT
compatibility: opencode
metadata:
  category: workflow
  phase: implementation-planning
  prev-phase: architecture
  next-artifact: plans/<feature>/phaseN/tasks.md
---

# Phase Writer Skill

This skill defines the exact template and rules for all
`plans/<feature>/phase<N>.md` files.

A phase file bridges the architecture document and the task list. It must
contain everything a developer needs to understand the scope, constraints,
and success criteria of a phase — without re-reading the architecture doc.
It must also contain enough structured detail that `task-decomposer` can
produce an unambiguous, complete task list from it alone (plus the arch doc).

---

## Document template

Use this section order exactly. Do not omit any section; write
"N/A — [reason]" only if a section genuinely cannot apply.

```markdown
# Phase <N>: <Phase Name>

> **Feature**: <feature-slug>
> **Status**: Pending | In Progress | Complete
> **Architecture doc**: [docs/<feature>/architecture.md](../../docs/<feature>/architecture.md)
> **Phase sequence**: Phase <N> of <Total>
> **Estimated effort**: <S = <1 day | M = 1-3 days | L = 3-5 days | XL = 1-2 weeks>
> **Created**: YYYY-MM-DD

---

## 1. Goal

One sentence. What user-visible or system-level outcome is achieved when this
phase is complete? Frame it as a capability, not a task.

Example: "A user can request and consume a magic-link email to authenticate
without a password."

---

## 2. Entry Criteria

What must be true before work on this phase begins? For Phase 1, these are
pre-conditions from the architecture's "Architecture Context". For Phase N>1,
these are exactly the Exit Criteria of Phase N-1.

- [ ] Entry criterion 1
- [ ] Entry criterion 2

---

## 3. Scope

### 3.1 In scope

List every deliverable for this phase. Each item must:
- Map to one or more FR-N / NFR-N IDs from the requirements document
- Correspond to a named component or file from the architecture's component table
- Be implementable without changes to prior phases

| Deliverable | FR / NFR refs | Component / file | Notes |
|-------------|--------------|------------------|-------|
| Implement `<thing>` | FR-1, FR-2 | `src/…` | |
| Add migration for `<table>` | FR-3 | `migrations/…` | |

### 3.2 Out of scope

Capabilities explicitly deferred to a later phase. This prevents scope creep.

- <Capability X> → Phase <M>
- <Capability Y> → Phase <M>

---

## 4. Technical Specification

The "how" inherited from the architecture document, scoped to this phase.
This is not new design — it is a focused extraction from the architecture.

### 4.1 Components to create

| Component | Path | Responsibility | Interfaces / exports |
|-----------|------|----------------|---------------------|
| `FeatureService` | `src/features/<f>/service.ts` | … | `create()`, `find()` |

### 4.2 Components to modify

| Component | Path | What changes | Backward compatible? |
|-----------|------|-------------|----------------------|
| `UserRepository` | `src/repositories/user.ts` | Add `findByToken()` | Yes |

### 4.3 Schema changes (this phase only)

List only migrations needed for this phase.

| Migration file | Table | Operation | Reversible? |
|----------------|-------|-----------|-------------|
| `YYYYMMDD_add_magic_tokens.ts` | `magic_tokens` | CREATE TABLE | Yes |

If none: "No schema changes in this phase."

### 4.4 API surface (this phase only)

List only endpoints introduced or modified in this phase.

```
POST /auth/magic-link
Request:  { "email": "string" }
Response: 202 Accepted — { "message": "string" }
Errors:   400 invalid email | 429 rate limited
```

If none: "No API surface changes in this phase."

### 4.5 Key ADR references

Which ADRs from the architecture doc directly constrain implementation in this
phase? List ADR-N and the constraint it imposes.

- ADR-1: <constraint on this phase's implementation>

---

## 5. Dependencies

### 5.1 Depends on (blocking)

What must exist before this phase can start? Include prior phases, external
services, configuration, environment variables, or third-party packages.

| Dependency | Type | Where defined | Status |
|------------|------|---------------|--------|
| Phase 1 exit criteria met | Prior phase | Phase 1 exit criteria | — |
| `SMTP_HOST` env var | Config | `.env.example` | Must be added |
| `nodemailer` package | Package | `package.json` | Must be installed |

### 5.2 Blocking (what this phase unblocks)

What becomes available after this phase is complete?

- Phase <N+1> can begin
- <Other team / service> can integrate with <endpoint>

---

## 6. Testing Requirements

Minimum test coverage that must exist before this phase is marked Complete.
Align with the testing strategy in the architecture document.

### 6.1 Unit tests

| What to test | File | Scenario |
|-------------|------|----------|
| `FeatureService.create()` | `src/features/<f>/service.test.ts` | happy path, invalid input, duplicate |

### 6.2 Integration tests

| What to test | File | Scenario |
|-------------|------|----------|
| `POST /auth/magic-link` | `tests/api/magic-link.test.ts` | 202 success, 400 bad email, 429 rate limit |

### 6.3 Manual verification checklist

Steps a developer runs locally to confirm the phase works end-to-end before
marking it complete.

- [ ] Step 1: run `<command>`, expect `<output>`
- [ ] Step 2: navigate to `<url>`, expect `<behaviour>`

---

## 7. Exit Criteria

Binary, verifiable statements. All must be true for this phase to be considered
complete. These become the Entry Criteria of the next phase verbatim.

- [ ] `<test command>` passes with 0 failures
- [ ] Given [setup], when [action], then [outcome]
- [ ] No TypeScript / lint errors on `<check command>`
- [ ] Migration runs forward and backward without error

---

## 8. Risks and Mitigations

Known risks specific to this phase.

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Third-party email API rate limit | Medium | High | Implement exponential back-off in task T-12 |

If none: "No phase-specific risks identified."

---

## 9. Open Questions

Questions that must be resolved before or during this phase.
Carry forward any unresolved Q-N items from the architecture doc that
affect this phase.

| # | Question | Must resolve before | Owner |
|---|----------|-------------------|-------|
| Q-1 | | Start of phase | TBD |

If none: "No open questions for this phase."

---

## 10. References

- [Architecture document](../../docs/<feature>/architecture.md) — §9 Phase <N>
- [Requirements document](../../docs/<feature>/requirements.md)
- [Tasks for this phase](./phase<N>/tasks.md) ← written by task-decomposer
```

---

## Formatting rules

1. **File name**: `phase1.md`, `phase2.md` … (no zero-padding, no other naming).
2. **Feature slug** in the frontmatter must match `docs/<slug>/` and `plans/<slug>/`.
3. **Status** starts as `Pending`. Changes to `In Progress` when work begins,
   `Complete` when all exit criteria are checked off — never by the planning agent.
4. **Effort sizing**:
   - S = less than 1 day
   - M = 1–3 days
   - L = 3–5 days
   - XL = 1–2 weeks (flag for architecture review if a phase is XL)
5. **FR/NFR IDs** in the scope table must match the requirements document exactly.
6. **Exit criteria** are the canonical source of truth for phase completion.
   They must be Given/When/Then or command-based — never subjective.
7. **Section 3.2 (Out of scope)** must always have at least one entry unless this
   is the final phase, in which case write: "This is the final phase; all
   remaining scope has been addressed."
8. File must end with `## 10. References` and a trailing newline.

---

## Quality checklist

Before writing the file, confirm:

- [ ] Every in-scope deliverable in §3.1 maps to a FR-N or NFR-N
- [ ] §4 contains only content drawn from the architecture doc (no new decisions)
- [ ] Every ADR that constrains this phase is listed in §4.5
- [ ] Exit criteria in §7 are identical to what will appear as Entry Criteria in the next phase file
- [ ] Schema changes in §4.3 match the architecture's §4 (Data Architecture) exactly
- [ ] All environment variables and packages needed are listed in §5.1
- [ ] File saved to `plans/<feature-slug>/phase<N>.md`
