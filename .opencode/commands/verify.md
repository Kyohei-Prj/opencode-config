---
description: Run manifest-first verification and produce a shippability verdict. Checks execution completeness, interface contracts, test suite, and (for epic) design intent. Accepts --finding fnd-id for scoped re-verify after /fix.
agent: feature-verifier
subtask: true
---

Run the verify workflow for feature: $1

Read workflow/$1/feature.yaml. If a --finding argument is present in $2, run a scoped re-verify for that finding only; otherwise run the full four-stage verification.

Apply the verify-checklist skill in order: execution completeness (manifest only), interface contracts (manifest + light code), test suite (code), design intent (epic lane only). Record each failed check as a finding immediately. For features with more than 10 tasks, invoke review-consolidator to surface run history patterns.

Determine the verdict, write the review section to feature.yaml, and generate workflow/$1/review.md using the review-report-writer skill.

The feature slug is: $1
Optional scoped finding: $2
