---
name: generate-migration
description: Create safe database schema migrations.
---

Purpose:
Create safe database schema migrations.

Used By:
- backend-engineer

Inputs:
- db-schema.sql
- current database schema
- new schema changes

Steps:

1. Identify schema differences.

Examples:

- new table
- column addition
- index creation
- constraint changes

2. Generate migration script.

3. Ensure migration safety:

- backward compatibility
- reversible migrations
- no destructive operations without confirmation

4. Generate rollback script.

Output:

migration.sql
rollback.sql
