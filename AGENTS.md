# AGENTS.md

This file provides global instructions for AI coding agents working in this repository.

## Development Workflow

The project follows an AI-driven development workflow:

1. Requirements → docs/requirements.md
2. Architecture → docs/architecture.md
3. Task planning → plan/tasks.yaml
4. Implementation using TDD
5. Code review
6. Integration tests
7. Documentation update

Agents must follow this workflow.

---

## Repository Structure

src/                application source code
tests/              unit and integration tests
docs/               specifications and architecture
plan/               machine-readable task plans
memory/             persistent AI memory
reports/            generated reports

.opencode/          AI workflow configuration

---

## Coding Rules

General rules:

- Prefer small, composable functions
- Write tests before implementation
- Follow consistent naming
- Avoid unnecessary dependencies
- Keep functions under ~50 lines where possible

---

## Testing

Every new feature must include:

- unit tests
- edge case coverage

Tests must pass before code review.

---

## Architecture Guardrails

Agents must not:

- change architecture without updating docs/architecture.md
- change public APIs without updating specification
- introduce breaking changes silently

---

## Commit Conventions

Commits should follow:

type(scope): summary

Examples:

feat(auth): add login endpoint
fix(cache): correct eviction logic 
test(api): add integration tests
