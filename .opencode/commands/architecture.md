---
description: Design system architecture based on docs/requirements.md.
agent: build
---

Goal: Design a scalable system architecture.

Inputs:
- @docs/requirements.md

Steps:

1. Analyze system requirements.

2. Identify major subsystems:
   - API
   - data storage
   - authentication
   - background processing
   - frontend
   - infrastructure

3. Propose 2–3 architecture options.

For each option include:
- system diagram (text)
- tech stack
- scalability strategy
- operational complexity
- pros and cons

4. Recommend one architecture.

5. Produce final documentation.

Output:

docs/architecture.md

Structure:

# Architecture Overview

# System Context

# Component Architecture

# Data Flow

# Technology Stack

# Deployment Model

# Security Boundaries

# Observability Strategy

6. Extract system contracts.

Create directory:

contracts/

Possible files:
- openapi.yaml
- events.yaml
- db-schema.sql

Rules:
- Prefer simple architectures.
- Design for incremental delivery.
