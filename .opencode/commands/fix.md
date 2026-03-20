---
description: Route a specific blocking finding through a targeted fix cycle. Runs a scoped build for the affected task or slice, then re-verifies only that finding. Flips verdict to approved if no blocking findings remain.
agent: build-orchestrator
subtask: true
---

Run the fix cycle for feature $1, finding $2.

Read workflow/$1/feature.yaml. Look up review.findings[$2] and confirm it is type blocking with status raised or acknowledged.

Determine the fix scope from the finding's slice and task fields:
- If task is not null: scope the build to that task only, passing --fix $2
- If slice is not null but task is null: scope the build to that slice, passing --fix $2  
- If both are null: this is a manifest-only fix — skip the build cycle and go directly to scoped re-verify

Before starting the build, update review.findings[$2].status from raised to acknowledged.

For build-scoped fixes: reset the target task phase from done to planned, record the reset in execution.run_history, then run the tdd-builder and task-reviewer cycle. If the build fails after 3 retries, stop and report — do not proceed to re-verify.

After a successful build (or for manifest-only fixes), invoke the feature-verifier in scoped mode for finding $2 only. If the finding is resolved and no other blocking findings remain, set verdict to approved and regenerate review.md.

The feature slug is: $1
The finding id is: $2
