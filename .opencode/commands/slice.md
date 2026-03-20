---
description: Break a shaped epic feature into a dependency-ordered DAG of slices and tasks. Run after reviewing /shape output.
agent: slice-planner
subtask: true
---

Run the slice workflow for feature: $1

Read workflow/$1/feature.yaml and confirm status is shape_complete. Apply the slice-writer skill to decompose design.components into plan.dag. Validate the DAG for cycles and requirement coverage. Write the plan section to feature.yaml and generate workflow/$1/brief.md.

The feature slug is: $1
