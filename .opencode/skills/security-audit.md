---
name: security-audit
description: Detect common security vulnerabilities.
---

Purpose:
Detect common security vulnerabilities.

Used By:
- security-reviewer
- code-reviewer

Inputs:
- source code
- dependency manifest
- authentication modules

Security Checks:

Input validation:
- SQL injection
- command injection
- path traversal

Authentication:
- password storage
- token handling
- session management

Data security:
- sensitive logging
- plaintext secrets

Dependency vulnerabilities:
- outdated libraries
- known CVEs

Secrets management:
- hardcoded credentials
- exposed tokens

Output:

Security report including:

- vulnerability description
- severity
- remediation suggestion
