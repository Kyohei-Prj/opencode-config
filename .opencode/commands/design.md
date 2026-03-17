---
description: "Produce an architecture design document at docs/<feature>/architecture.md from an existing requirements.md"
agent: architecture-designer
subtask: true
model: anthropic/claude-sonnet-4-20250514
---

You are starting the architecture design phase for an existing feature specification.

Feature slug provided by the user:
$ARGUMENTS

---

Follow these steps **in order**. Do not skip any step.

## Step 1 — Validate the requirements document

Check that `docs/$ARGUMENTS/requirements.md` exists and its Status is not `Draft`.
- If the file does not exist, stop and report: "No requirements document found at `docs/$ARGUMENTS/requirements.md`. Run `/spec $ARGUMENTS` first."
- If Status is `Draft`, proceed but add a prominent warning at the top of the architecture doc: ⚠️ Based on a Draft requirements document — confirm requirements are approved before implementation.
- Read the full requirements document carefully before proceeding.

## Step 2 — Deep codebase exploration

Use the `@explore` subagent to investigate:
- Directory structure and module boundaries
- Existing patterns for the same concerns this feature touches (auth, storage, API routes, state management, etc.)
- Build tooling, test infrastructure, and deployment configuration
- Any existing code that this feature must integrate with or extend
- Database schema, ORM models, or data access patterns in use

Document findings — they become the "Architecture Context" section.

## Step 3 — Load the architecture-writer skill

Call the `architecture-writer` skill. Use its template and rules as the strict blueprint for the document you are about to write.

## Step 4 — Design the architecture

Working strictly from the requirements and codebase findings, design an architecture that:
- Is the **simplest solution** that satisfies all P0 and P1 requirements
- Follows the **existing patterns** found in Step 2 — never introduce a new pattern when an established one fits
- Makes **phase boundaries explicit**: the design must decompose into 2–4 sequential implementation phases where each phase produces working, shippable software
- Identifies every **cross-cutting concern**: error handling, logging, auth, testing, migrations

## Step 5 — Write the document

Write the completed architecture document to `docs/$ARGUMENTS/architecture.md`. Create the directory if it does not exist (it usually already exists from the requirements step).

## Step 6 — Confirm

Print a summary:
- Path written
- Number of phases defined
- Key technical decisions made
- Any open questions added that need human resolution before Phase 1 begins
