---
description: Resume an interrupted build from the last incomplete wave. Skips all completed work and restarts only what was in progress. Use instead of re-running /build after an interruption.
agent: build-orchestrator
subtask: true
---

Resume the interrupted build for feature: $1

Read workflow/$1/feature.yaml and confirm feature.status is building. Scan execution.waves to find the resume point — the first wave that is not complete. For any running or failed wave, inspect each slice's task phases: skip slices where all tasks are done, restart tasks that are in implementing or reviewing state, and begin normally for slices where all tasks are still planned.

Re-check open question blockers before proceeding. Then continue execution from the resume point using the concurrency already recorded in execution.concurrency.

The feature slug is: $1
