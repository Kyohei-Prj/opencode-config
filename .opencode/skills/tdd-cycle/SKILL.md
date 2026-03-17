---
name: tdd-cycle
description: "Defines the strict TDD cycle (Red → Green → Refactor → Verify) that tdd-implementer must follow for every task. Covers test-first rules, implementation constraints, refactor discipline, and verification gates. Load before implementing any task."
license: MIT
compatibility: opencode
metadata:
  category: workflow
  phase: implementation
  agent: tdd-implementer
---

# TDD Cycle Skill

This skill is the authoritative definition of the Test-Driven Development
cycle used in this project's implementation workflow. Every `tdd-implementer`
invocation must follow this cycle exactly, for every task, without exception.

---

## The four-phase cycle

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│   RED ──────▶ GREEN ──────▶ REFACTOR ──────▶ VERIFY        │
│    │            │               │               │           │
│  Write        Write           Clean          Run full       │
│  failing      minimum         without        suite +        │
│  tests        impl to         breaking       types +        │
│  first        pass tests      tests          lint           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

A task is complete only after all four phases pass. You may not skip or
reorder phases.

---

## Phase 1 — RED: Write failing tests

### Purpose
Specify the behaviour before implementing it. Tests are the executable
specification derived from the task's acceptance criteria.

### Rules

**1.1 — Tests before code.**
No implementation file may be created or modified until at least one test
exists that will fail because the implementation does not yet exist.
The test code should follow Arrange-Act-Assert (AAA) pattern when applicable.

**1.2 — One test file per implementation unit.**
Follow the project's existing test file naming and location convention:

| Convention | Example |
|------------|---------|
| `*.test.ts` co-located | `src/auth/token.test.ts` |
| `*.spec.ts` co-located | `src/auth/token.spec.ts` |
| `__tests__/` directory | `src/auth/__tests__/token.ts` |
| `tests/` mirror | `tests/auth/token.test.ts` |
| `_test.go` suffix | `auth/token_test.go` |
| `test_*.py` prefix | `tests/test_token.py` |

If unsure, check two existing test files in the project and match their pattern.

**1.3 — Map acceptance criteria to test cases 1:1.**
Each acceptance criterion in the task block must produce at least one test case.
Write the test name to match the criterion:

```typescript
// Acceptance: POST /auth/magic-link with valid email returns 202
it('returns 202 when email is valid', async () => { … })

// Acceptance: POST /auth/magic-link with invalid email returns 400
it('returns 400 with error message when email is invalid', async () => { … })
```

**1.4 — Include edge cases for every happy-path test.**
For each happy-path acceptance criterion, also write:
- One test for the primary error case
- One test for the boundary/edge case if one exists

**1.5 — Run tests immediately. Confirm they fail.**
After writing tests, run them with the narrowest test command possible:
```bash
npm test -- --testPathPattern=<file-pattern>
```
Expected outcomes that confirm RED:
- Test runner reports `N failed` — ✅ correct RED state
- Test runner reports `cannot find module` — ✅ acceptable, file not created yet
- Test runner reports `N passed` — ❌ tests are tautological, rewrite them

**1.6 — Do not write implementation code in test files.**
Test helpers, fixtures, and factories are allowed. Business logic is not.

---

## Phase 2 — GREEN: Minimum implementation

### Purpose
Make the failing tests pass with the least possible code. Resist all urge to
build more than the tests demand.

### Rules

**2.1 — Implement only what the failing tests require.**
If a test for feature A is failing, do not implement feature B while you are
at it, even if B is trivially easy. B has its own task.

**2.2 — Run tests after every meaningful change.**
"Meaningful change" = any modification to an implementation file. The feedback
loop must be tight. Do not write 50 lines then run tests; write 5–10 lines,
run tests, iterate.

**2.3 — Three-strike rule.**
If tests are still failing after 3 distinct implementation attempts for the
same failing test:
- Stop implementing
- Return `status: "failed"` to the orchestrator with a detailed `failure_reason`
- Do not attempt a fourth approach

**2.4 — Minimal stubs for external dependencies.**
If the task requires a method that calls an external service (email, DB, API),
write a minimal stub/mock for test purposes — do not make real external calls
from tests. The mock should be the simplest thing that makes the test pass.

**2.5 — No global state mutations in tests.**
Each test must be independently runnable. Use `beforeEach`/`afterEach` to
set up and tear down state. Never rely on test execution order.

**2.6 — Implementation files must match the paths in the task's Files table.**
Do not create files at different paths than specified. If the architecture
specifies `src/features/auth/token.repository.ts`, that is the exact path.

---

## Phase 3 — REFACTOR: Clean without breaking

### Purpose
Remove duplication, improve names, add necessary comments. The behaviour
must not change.

### Rules

**3.1 — Run tests before and after every refactor change.**
If tests were green before a refactor, they must be green after. If they break,
undo the refactor immediately.

**3.2 — Allowed refactoring operations:**
- Rename variables, functions, types to be clearer
- Extract duplicated logic into a private helper (within the same file)
- Add JSDoc / docstring comments for exported functions
- Reorder code within a function for readability
- Remove dead code introduced during GREEN (temporary scaffolding, debug logs)
- Fix code style to match the project's lint rules

**3.3 — Forbidden during REFACTOR:**
- Changing any function signature
- Adding new behaviour (even "obviously needed" behaviour)
- Extracting into new files — that is a separate task
- Modifying test files (except to fix test descriptions/comments)

**3.4 — The refactor phase is not optional.**
Even if the implementation is clean, run tests one more time and verify there
are no `console.log` / `print` / debug statements left in committed code.

---

## Phase 4 — VERIFY: Full suite + quality gates

### Purpose
Confirm the task is complete and has not broken anything else.

### Rules

**4.1 — Run the full test suite for the affected module.**
Not just the new tests — the entire module or feature directory:
```bash
npm test -- --testPathPattern=src/features/auth
```
This catches regressions in adjacent code.

**4.2 — Run typecheck if the project uses static types.**
```bash
npx tsc --noEmit          # TypeScript
mypy src/                 # Python
```
Zero type errors required. Warnings are acceptable only if they existed before
this task (check with `git stash && typecheck && git stash pop` if unsure).

**4.3 — Run lint.**
```bash
npm run lint              # or eslint / ruff / golangci-lint / etc.
```
Zero new lint errors. Pre-existing lint debt is not this task's responsibility
to fix — but do not introduce new violations.

**4.4 — All acceptance criteria must be independently verifiable.**
Go through the task's acceptance criteria list and verify each one manually or
via the test output. Check each one off mentally:
- ✅ "5 tests passing" — confirmed by test output
- ✅ "migration runs without error" — confirmed by running migration
- ✅ "returns 400 for invalid input" — confirmed by integration test

**4.5 — Only return `status: "passed"` when all of the following are true:**
- [ ] All new tests pass
- [ ] No pre-existing tests broke
- [ ] Typecheck passes (or was already failing before this task)
- [ ] Lint passes (zero new violations)
- [ ] Every acceptance criterion in the task block is satisfied

---

## Test naming conventions

Use consistent, descriptive test names that read as documentation:

```
describe('<ComponentName>')
  describe('<methodName>()')
    it('<does what> when <condition>')
    it('throws <error> when <condition>')
    it('returns <value> given <input>')
```

Examples:
```typescript
describe('MagicTokenRepository')
  describe('create()')
    it('inserts a token record with a 1-hour expiry')
    it('throws DuplicateTokenError when token already exists')

  describe('consume()')
    it('marks token as used and returns associated user id')
    it('throws ExpiredTokenError when token is past expiry')
    it('throws NotFoundError when token does not exist')
```

---

## Test isolation requirements

| Concern | Requirement |
|---------|-------------|
| Database | Use a test database or in-memory equivalent; never the dev/prod DB |
| External APIs | Always mock/stub; never make real network calls from unit tests |
| Filesystem | Use temp directories; clean up in afterEach |
| Environment | Set required env vars in test setup, not in `.env` |
| Time | Use a clock mock for any code that uses `Date.now()` or equivalent |
| Randomness | Seed or mock random generators for deterministic tests |

---

## Coverage expectations

| Layer | Minimum new-code coverage |
|-------|--------------------------|
| Data access (repositories) | 90% line coverage |
| Service / business logic | 85% line coverage |
| API handlers / controllers | 80% line coverage |
| UI components | Key interaction paths tested |
| Config / migrations | Run forward + backward; no line coverage required |

These are minimums for new code written in this task. Do not reduce coverage
on existing code.

---

## Language-specific notes

### TypeScript / JavaScript
- Prefer `describe`/`it` (Jest / Vitest style) over `test()` top-level
- Use `expect(value).toBe()` for primitives, `.toEqual()` for objects
- Mock modules with `vi.mock()` (Vitest) or `jest.mock()` (Jest)
- Type assertions: prefer `satisfies` over `as` in test setup

### Python
- Use `pytest` fixtures for setup/teardown
- Use `pytest.raises()` for error cases
- Name test functions `test_<behaviour>_when_<condition>`

### Go
- Use `t.Run()` for sub-tests
- Use `testify/assert` for assertions
- Table-driven tests for multiple input cases

### Other languages
- Follow the project's existing test style — check 2–3 existing test files
  before writing any tests.
