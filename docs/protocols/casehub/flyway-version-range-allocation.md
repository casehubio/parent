---
id: PP-20260508-07b9f6
title: "Flyway migration version ranges are module-scoped and epic-branch-reserved — no overlap permitted"
type: rule
scope: platform
applies_to: "All casehub modules using Flyway"
severity: critical
refs:
  - docs/protocols/universal/flyway-migration-rules.md
violation_hint: "Overlapping version numbers cause FlywayException at startup even on a fresh greenfield install — uniqueness is enforced before any data is touched. Placing extension migrations inside db/migration/<module>/ (a subdirectory of the default path) causes the same failure: Flyway scans recursively, so any datasource scanning classpath:db/migration will also find them."
created: 2026-05-08
updated: 2026-05-18
---

# Convention: Flyway Migration Version Range Allocation

**Applies to:** All casehub modules using Flyway  
**Severity:** Critical — overlapping version numbers cause `FlywayException: Found more than one migration`
at startup, even on a fresh install with no existing data.

## Problem

Two sources of overlap, both fatal:

1. **Module-level:** Multiple optional modules in the same deployment each own a Flyway migration range.
   Overlap causes startup failure when both modules are on the classpath.

2. **Branch-level (sequential range only):** Two concurrent epic branches that each add migrations
   to the core V1–V999 sequential range can independently choose the same version number (e.g. both
   pick V23 as the next available). When both branches merge to main, Flyway sees duplicate V23 files
   and fails at startup — even on a greenfield install with no pre-existing data.

---

## Rule 1 — Module-level thousand-block allocation

Each module owns an exclusive thousand-block. New modules claim the next free block before writing
any migrations:

| Range | Module |
|---|---|
| V1–V999 | core runtime (sequential, one per feature) |
| V2000–V2999 | queues / ledger integration module |
| V3000–V3999 | notifications module |
| V4000–V4999 | AI module |
| V5000–V5999 | issue-tracker module |
| V6000+ | next new optional module |

## Rule 2 — Epic-branch V-number reservation (sequential V1–V999 range only)

Because multiple epic branches may run concurrently, and each independently picks the next sequential
V number, reservations must be made and recorded at **epic start** — not just at merge time.

### Step 1 — Scan all branches, not just main

At epic start, find the highest V number claimed across main **and all remote epic branches**:

```bash
# Highest V on main
git -C <project> log main --name-only --format="" \
  | grep -oP "(?<=V)\d+(?=__)" | sort -n | tail -1

# Highest V on any remote epic branch
git -C <project> fetch --all 2>/dev/null
git -C <project> log --remotes="*/epic-*" --name-only --format="" \
  | grep -oP "(?<=V)\d+(?=__)" | sort -n | tail -1
```

Take the maximum of the two. The next safe V number is `max + 1`.

### Step 2 — Record the reservation in `.meta`

Add `flyway-next-v: <N>` to `design/.meta` in the workspace before writing any migrations:

```
epic: epic-my-feature
project-sha: <sha>
date: 2026-05-18
issue: 123
flyway-next-v: 26
```

This makes the reservation visible to the branch hygiene scan so it can detect conflicts between
open epic branches before either merges.

### Step 3 — Name migrations from the reserved number

```sql
-- V26__my_feature_table_change.sql
-- V27__my_feature_second_change.sql  (if a second migration is needed)
```

### Step 4 — Re-verify at merge time

Before merging (or opening a PR), confirm the reserved V number is still free on current main:

```bash
git -C <project> log main --name-only --format="" \
  | grep -oP "(?<=V)\d+(?=__)" | sort -n | tail -1
```

If another epic merged first and took your number: **renumber** (file rename + commit).
This is safe at any time while no production installations exist.

### Renumbering safety boundary

**Renumbering is always safe until the first production deployment.** After a production database
has run a migration, renaming that migration file changes its checksum — Flyway will fail on next
startup and require `flyway repair`. This is why the greenfield period is the time to get numbering
right. Once a production deployment exists, treat V numbers as immutable.

---

## Rule 3 — Branch hygiene scan checks for V conflicts

The epic branch hygiene scan (Workflow C in the `epic` skill) compares `flyway-next-v` values across
all open epic branches. If two branches claim the same V number, it flags a conflict before either
branch attempts to merge:

```
⚠️  V number conflict detected:
   epic-my-feature     claims V26 (flyway-next-v in .meta)
   epic-other-feature  also claims V26 (migration file found on branch)

   Resolve: one branch must renumber before merging.
```

---

## Rule 4 — Scoped directories for named datasources (alternative)

Extensions that operate on their own **named datasource** can use a scoped migration directory
instead of claiming a version range block. Version numbers become module-local, eliminating the
need for global coordination:

- Place migrations in `db/<module>/migration/` (e.g. `db/qhorus/migration/`)
- Configure: `quarkus.flyway.<datasource>.locations=classpath:db/<module>/migration`

**⚠️ The path must be outside `db/migration/` entirely.** Flyway scans classpath locations
recursively — placing migrations at `db/migration/<module>/` puts them inside the default
datasource's scan root. Any app that has a second Flyway datasource scanning `classpath:db/migration`
will find both sets of files and fail with "Found more than one migration with version N" even
though the named datasource is correctly scoped. Use `db/<module>/migration/` as the root.

**`casehub-qhorus`** uses this pattern (`db/qhorus/migration/`). Rules 1–3 above apply only
to shared-datasource modules. Modules with isolated named datasources should prefer this approach.
