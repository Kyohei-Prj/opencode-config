---
description: Explore the codebase, define requirements and design, then break the feature into a parallel-ready task plan. For small and standard lanes only — use /shape then /slice for epic.
agent: solution-shaper
subtask: true
---

Run the shape-slice workflow for feature: $1

First, act as solution-shaper: read workflow/$1/feature.yaml, confirm the lane is small or standard (if epic, stop and tell the user to use /shape then /slice instead), explore the codebase at the appropriate depth, complete the problem section, and add the design section.

Then, act as slice-planner: read the freshly written design, apply the slice-writer skill to decompose design.components into a DAG of slices and tasks, validate the DAG for cycles and full requirement coverage, write the plan section to feature.yaml, and generate workflow/$1/brief.md.

The feature slug is: $1
