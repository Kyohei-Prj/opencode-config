---
description: "Transform a vague idea into a structured requirements doc at docs/<feature>/requirements.md"
agent: requirements-analyst
subtask: true
---

You are starting the requirements engineering workflow for a new feature.

Feature or idea provided by the user:
$ARGUMENTS

---

Follow these steps **in order**:

## Step 1 — Understand the codebase context

Use the `@explore` subagent (or read key files directly) to:
- Identify the tech stack, major modules, and existing patterns
- Note any existing similar features that could inform scope
- Understand the project's coding conventions and architecture style

Summarize your findings in a `## Project Context` section.

## Step 2 — Clarify and expand the requirements

Given the vague input above, apply structured thinking to produce:
- A clear **feature name** (kebab-case, suitable as a directory name)
- **Problem statement**: what pain point or need does this address?
- **Goals**: what must be true when this feature is complete?
- **Non-goals**: what is explicitly out of scope?
- **User stories**: in the format `As a <role>, I want <capability>, so that <benefit>.`
- **Functional requirements**: numbered list, each testable
- **Non-functional requirements**: performance, security, accessibility, etc.
- **Constraints**: technical, regulatory, or business constraints
- **Open questions**: ambiguities that need a human decision before architecture

## Step 3 — Write the requirements document

Call the `requirements-writer` skill to get the exact output template and formatting rules, then write the document to:

```
docs/<feature-name>/requirements.md
```

Create the directory if it does not exist.

## Step 4 — Confirm

After writing the file, print a brief summary:
- Path of the file written
- Feature name
- Count of functional requirements captured
- Any open questions that need human input before proceeding to architecture
