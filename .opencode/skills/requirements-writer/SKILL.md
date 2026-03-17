---
name: requirements-writer
description: "Provides the canonical template and formatting rules for writing a requirements.md document. Load this skill before writing any requirements document to ensure consistent structure across the project."
license: MIT
compatibility: opencode
metadata:
  workflow: requirements
  stage: specification
  next-stage: architecture
---

# Requirements Writer Skill

This skill defines the exact template and rules for producing a
`docs/<feature>/requirements.md` file.

---

## Template

Copy this template verbatim, then fill in every section. Do not remove any
section heading; use "N/A" if genuinely not applicable.

```markdown
# Requirements: <Feature Name>

> **Status**: Draft | Review | Approved  
> **Created**: YYYY-MM-DD  
> **Last updated**: YYYY-MM-DD  
> **Author**: AI-generated via `/spec`  
> **Next step**: Architecture design → `docs/<feature>/architecture.md`

---

## 1. Overview

One paragraph. What is this feature and why does it matter to users or the business?

---

## 2. Problem Statement

What specific problem does this solve? Who experiences it? What is the cost of
not solving it?

---

## 3. Goals

A checklist of outcomes that must be true when this feature ships.

- [ ] Goal 1
- [ ] Goal 2

---

## 4. Non-Goals

Explicit scope boundaries. What will NOT be built as part of this feature?

- Not in scope: …
- Future consideration: …

---

## 5. Project Context

Summary of relevant codebase findings that informed these requirements:

- **Stack**: …
- **Related modules**: …
- **Existing patterns to follow**: …
- **Constraints inherited from codebase**: …

---

## 6. User Stories

| # | As a… | I want… | So that… |
|---|-------|---------|----------|
| US-1 | | | |
| US-2 | | | |

---

## 7. Functional Requirements

Each requirement must be independently testable. Use the prefix `FR-`.

| ID | Requirement | Priority | Notes |
|----|-------------|----------|-------|
| FR-1 | | Must-have | |
| FR-2 | | Must-have | |
| FR-3 | | Should-have | |

Priority values: **Must-have** · **Should-have** · **Nice-to-have**

---

## 8. Non-Functional Requirements

| ID | Category | Requirement | Metric |
|----|----------|-------------|--------|
| NFR-1 | Performance | | |
| NFR-2 | Security | | |
| NFR-3 | Accessibility | | |
| NFR-4 | Observability | | |

---

## 9. Constraints

Technical, regulatory, or business constraints that bound the solution space.

- …

---

## 10. Assumptions

Assumptions made while writing these requirements. Each assumption should be
validated before architecture begins.

- …

---

## 11. Open Questions

Questions that require a human decision before architecture design can proceed.
Do not leave this section empty if any ambiguity exists.

| # | Question | Owner | Due |
|---|----------|-------|-----|
| Q-1 | | | |

---

## 12. Acceptance Criteria

High-level acceptance criteria for the feature as a whole (not per requirement).
These will be used to verify the feature before release.

- [ ] AC-1: …
- [ ] AC-2: …

---

## 13. References

Links to related docs, tickets, designs, or prior art.

- …
```

---

## Formatting Rules

1. **Feature name** in the H1 must match the directory name under `docs/`.
2. **IDs** (FR-, NFR-, US-, Q-, AC-) must be sequential with no gaps.
3. **Priority** column in FR table: use exactly `Must-have`, `Should-have`, or
   `Nice-to-have` — no other values.
4. **Status** in the frontmatter callout must be one of: `Draft`, `Review`, `Approved`.
   All AI-generated documents start as `Draft`.
5. **Tables** must have a header row and at least one data row.
6. **Open Questions section** must never be omitted. If there are truly no open
   questions, write: *"No open questions at this time. Ready for architecture."*
7. The document must end with `## 13. References`. Add a trailing newline after.

---

## Quality Checklist

Before finalizing the document, verify:

- [ ] At least 5 entries in the Functional Requirements table
- [ ] At least 2 User Stories
- [ ] Non-Goals section has at least 1 entry
- [ ] Project Context reflects actual codebase findings (not generic placeholders)
- [ ] Every Must-have FR has a corresponding Acceptance Criterion
- [ ] Open Questions are assigned an owner (use "TBD" if unknown)
