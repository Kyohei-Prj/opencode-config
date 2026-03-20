---
description: Implement all planned slices in parallel waves. Each task goes through red-green-refactor TDD and per-task review before advancing. Accepts an optional scope (slice slug or task id) and --concurrency N.
agent: build-orchestrator
subtask: true
---

Run the build workflow for feature: $1

Read workflow/$1/feature.yaml. Parse any additional arguments from: $ARGUMENTS

If a --concurrency value is present, use it; otherwise default to 1. If a slice slug or task id is present as a second argument, scope the build to that target only.

Compute parallel waves from plan.dag, check open question blockers before each wave, fan out tdd-builder subagents up to the concurrency limit, gate every completed task through task-reviewer, and advance wave by wave until all tasks are done. Write all execution state to feature.yaml as it happens.

The feature slug is: $1
Additional arguments (scope, concurrency): $2 $3
