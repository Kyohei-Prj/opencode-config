---
name: review-standards
description: "Defines the three review lenses (spec conformance, TDD quality, architecture conformance), severity levels, finding ID format, and the findings object structure returned by code-reviewer. Load before conducting any code review."
license: MIT
compatibility: opencode
metadata:
  category: workflow
  phase: review
  agent: code-reviewer
---

# Review Standards Skill

This skill is the authoritative definition of code review standards for this
project's review workflow. Every `code-reviewer` invocation must apply all
three lenses and use the severity levels defined here without deviation.

---

## The three review lenses

Reviews are structured into three independent lenses applied in order.
Each lens has a distinct question, scope, and set of checks.

```
┌──────────────────────────────────────────────────────────────────────┐
│                                                                      │
│  LENS 1              LENS 2               LENS 3                     │
│  Spec Conformance    TDD Quality          Architecture Conformance   │
│                                                                      │
│  Does the code       Are the tests        Does the code fit          │
│  do what the         honest specs         the agreed design?         │
│  task required?      of behaviour?                                   │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

---

## Lens 1: Spec Conformance

**Core question**: Does the implementation satisfy what the task required?

### What to check

**Acceptance criteria coverage**
Each acceptance criterion in the task block must have:
- At least one test that directly targets it
- An implementation that actually satisfies it (not just one that makes the
  test pass)

Flag if: a criterion has no test, or the test verifies a proxy rather than
the criterion itself.

**File fidelity**
The files created or modified must match the task's Files table:
- Correct paths (exact string match — `src/auth/token.ts` ≠ `src/Auth/token.ts`)
- Correct action (a Create entry should not already exist; a Modify entry
  should not be a brand-new file)

Flag if: a file is at the wrong path, or a required file is absent.

**FR / NFR satisfaction**
For each FR-N / NFR-N the task claims to satisfy, the implementation must
address it. Partial satisfaction counts as a finding.

Flag if: an FR is claimed but the implementation only covers part of it.

**Commit message conformance**
The actual commit message (from impl-log) must match the pattern in the task:
- Type, scope, and description must align with the task's specified message
- Must follow conventional commits format

Flag if: commit message deviates significantly from the task spec.

---

## Lens 2: TDD Quality

**Core question**: Are the tests an honest, independent specification of
behaviour — not just a safety net bolted on after?

### What to check

**Test structure and naming**
Tests must be organised so they read as documentation:
```
describe('<Unit>') > describe('<method>()') > it('<behaviour> when <condition>')
```
Test names must describe observable behaviour, not implementation details.

✅ `it('returns 404 when the user does not exist')`
❌ `it('hits the DB and returns null')`

Flag if: test names describe internals, not behaviour.

**Coverage honesty**
Tests are only valuable if they can catch real bugs. Check:
- Is there at least one error/edge case for every happy-path scenario?
- Would a test still pass if the implementation returned a hardcoded value?
  (Tautological tests)
- Are error cases tested with specific error types/messages?

Flag if: only happy paths are tested; error cases not covered by acceptance
criteria but obvious from the domain are absent; assertions are too loose
to catch regressions.

**Test isolation**
Each test must be independently runnable:
- External dependencies (DB, APIs, time, randomness, filesystem) must be
  mocked or stubbed
- No shared mutable state between tests
- `beforeEach`/`afterEach` used for setup/teardown, not ad-hoc state in the
  test body

Flag if: tests make real network calls, share database state, or depend on
execution order.

**RED-first evidence**
The impl-log entry should confirm tests were written before implementation.
If the impl-log notes a deviation (e.g. "implemented first, then wrote tests"),
flag it. The RED phase is not cosmetic.

Flag if: impl-log explicitly notes tests were written after implementation.

### Tautology detection

A test is tautological if it would pass with a stub implementation. Common
patterns:

```typescript
// Tautological — passes with `return undefined`
expect(result).toBeDefined()

// Tautological — passes with `return {}`
expect(Object.keys(result).length).toBeGreaterThan(0)

// Not tautological — would fail with a stub
expect(result.userId).toBe('user-123')
expect(result.expiresAt).toBeInstanceOf(Date)
```

---

## Lens 3: Architecture Conformance

**Core question**: Does the implementation match the design decisions recorded
in the architecture document?

### What to check

**Component location**
Files must live at the exact paths specified in the architecture's component
table. A file at the wrong path breaks the import graph and signals the
component table is stale.

Flag if: a file is at a path not listed in the component table for this task.

**Exported interface**
The public API of a component (exported functions, class methods, TypeScript
types) must match what the component table specifies under
"Interfaces / exports".

Flag if: an exported function has a different signature than specified;
an expected export is missing; an internal function is unexpectedly exported.

**Layer discipline**
The architecture enforces a strict call direction:

```
UI / Client
    ↓
API Handler / Controller
    ↓
Service / Business Logic
    ↓
Repository / Data Access
    ↓
Database / External Service
```

Each layer may only call the layer directly below it.
Violations (e.g. an API handler calling a repository directly) break the
isolation that makes the service layer independently testable.

Flag if: any layer calls a layer other than the one immediately below it.

**ADR compliance**
Every ADR cited in the task's Notes field constrains implementation choices.
If the implementation deviates from an ADR decision, it is a blocking finding
unless a newer ADR supersedes the cited one.

Flag if: the cited ADR specifies pattern X and the implementation uses
pattern Y without a superseding ADR.

**API contract**
If the task implements or modifies an endpoint, the implementation must match
the architecture's §5 API Design exactly:
- HTTP method and path
- Request shape (field names and types)
- Success response shape and status code
- Error response shapes and status codes

Flag if: any field name differs, any status code differs, any required field
is absent.

**Schema compliance**
If the task touches the database, the migration and model must match §4.1
exactly:
- Table name
- Column names and types
- Nullability constraints
- Indexes specified

Flag if: any column name, type, or constraint differs from the schema table.

---

## Severity levels

Use these definitions without deviation. When in doubt between two severities,
use the higher one and explain in the finding's description.

### 🔴 BLOCKING

The phase cannot be considered shippable until this is resolved. Use for:

| Situation | Example |
|-----------|---------|
| ADR violation | Code uses pattern Y when ADR-2 requires pattern X |
| Acceptance criterion with zero test coverage | Criterion "returns 403 for unauthenticated users" has no test |
| Required file entirely missing | `src/auth/token.repository.ts` absent despite being in files table |
| Layer discipline violation | API handler calls `db.query()` directly |
| API contract mismatch | Endpoint returns 200 where architecture specifies 201 |
| Schema column mismatch | Migration creates `user_token` column; architecture specifies `magic_token` |
| Tautological test on a blocking acceptance criterion | `expect(response).toBeDefined()` is the only assertion |

### 🟡 NON-BLOCKING

Should be fixed soon but does not prevent shipping. Use for:

| Situation | Example |
|-----------|---------|
| Missing error/edge case not in acceptance criteria | Happy path tested; "user already has an active token" case not tested |
| Test name describes internals | `it('calls tokenService.create()')` |
| Missing JSDoc on exported public interface | `createMagicToken()` exported but undocumented |
| Loose assertion where tighter is straightforward | `expect(token).toBeTruthy()` when `expect(token).toMatch(/^[a-f0-9]{64}$/)` is available |
| Minor layer concern | Service reaches into a second repository not listed in component table |

### 🔵 SUGGESTION

Optional improvement. No obligation to act. Use for:

| Situation | Example |
|-----------|---------|
| Cleaner implementation approach | Could use `Array.from()` instead of manual loop |
| More expressive naming | `tok` could be `magicToken` |
| Test factory opportunity | Three tests repeat the same setup — a factory would help |
| Extractable helper | Logic duplicated in two places within the same file |

---

## Finding ID format

```
F-<phase>-<task-seq>-<finding-seq>
```

| Part | Meaning | Example |
|------|---------|---------|
| `F` | Finding prefix | always `F` |
| `<phase>` | Phase number | `1`, `2` |
| `<task-seq>` | Two-digit task sequence from task ID | `03` from `T-1-03` |
| `<finding-seq>` | Two-digit finding sequence within task | `01`, `02` |

Examples:
- `F-1-03-01` = Phase 1, Task 03, first finding
- `F-2-07-02` = Phase 2, Task 07, second finding

---

## Findings object structure

```json
{
  "task_id": "T-N-NN",
  "task_title": "Short task title from tasks.md",
  "overall": "passed | passed_with_suggestions | needs_work",
  "files_reviewed": [
    "src/features/auth/token.repository.ts",
    "src/features/auth/token.repository.test.ts"
  ],
  "findings": [
    {
      "id": "F-1-03-01",
      "severity": "blocking | non_blocking | suggestion",
      "lens": "spec_conformance | tdd_quality | architecture_conformance",
      "file": "src/features/auth/token.repository.ts",
      "line_range": "42-58",
      "title": "Short, specific title under 80 characters",
      "description": "Clear explanation of what is wrong and why it matters, referencing the specific criterion, ADR, or architecture section violated.",
      "resolution": "Description of what the fix must accomplish — not the fix itself.",
      "references": ["ADR-2", "FR-3", "§5.1 API Design"]
    }
  ],
  "lens_summary": {
    "spec_conformance": "passed | findings",
    "tdd_quality": "passed | findings",
    "architecture_conformance": "passed | findings"
  },
  "impl_log_notes": "Notable deviations or observations from the impl-log entry."
}
```

### `overall` value rules

| Value | Condition |
|-------|-----------|
| `"passed"` | Zero findings of any severity |
| `"passed_with_suggestions"` | One or more `suggestion` findings only |
| `"needs_work"` | One or more `blocking` or `non_blocking` findings |

---

## Review completeness checklist

Before returning the findings object, confirm:

- [ ] All three lenses applied — no lens skipped
- [ ] Every acceptance criterion in the task checked under Lens 1
- [ ] Every test file read and evaluated under Lens 2
- [ ] Every file in the files table cross-referenced against architecture under Lens 3
- [ ] Every ADR cited in task Notes checked under Lens 3
- [ ] All finding IDs are unique and follow the `F-N-NN-NN` format
- [ ] No finding severity is higher than the blocking rules justify
- [ ] `overall` value consistent with findings severity distribution
- [ ] No findings added about files outside the task's files table

---

## What a good finding looks like

```json
{
  "id": "F-1-03-01",
  "severity": "blocking",
  "lens": "tdd_quality",
  "file": "src/features/auth/token.repository.test.ts",
  "line_range": "18-22",
  "title": "No test for token expiry — acceptance criterion AC-3 has no coverage",
  "description": "Acceptance criterion AC-3 requires that consuming an expired token throws ExpiredTokenError. The test file covers token creation and successful consumption but has no test for the expiry path. A bug in the expiry check would not be caught by the test suite.",
  "resolution": "Add a test case that creates a token with a past expiry, attempts to consume it, and asserts ExpiredTokenError is thrown with the expected message.",
  "references": ["FR-4", "Acceptance criterion AC-3"]
}
```

## What a poor finding looks like (do not do this)

```json
{
  "id": "F-1-03-02",
  "severity": "non_blocking",
  "lens": "spec_conformance",
  "file": "src/features/auth/token.repository.ts",
  "line_range": "1-120",
  "title": "Code could be improved",
  "description": "The implementation works but could be cleaner.",
  "resolution": "Refactor it.",
  "references": []
}
```

Poor because: vague title, no specific problem, no reference, no actionable
resolution, line range covers the entire file.
