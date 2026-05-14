---
id: PP-20260512-arename
title: "Artifact rename propagation — update all cross-repo consumers before shipping"
type: rule
scope: universal
applies_to: "Any casehubio repo renaming a published artifactId"
severity: important
refs: [maven-coordinate-standard.md]
violation_hint: "Renaming an artifact without updating consumers causes build failures in dependent repos that are hard to trace"
created: 2026-05-12
---

# Artifact Rename Propagation

**Applies to:** Any rename of a published `artifactId` in any casehubio repo  
**Severity:** Important — a rename that ships without updating consumers breaks their builds silently until next full-stack run

## Why This Needs a Protocol

When `casehub-connectors` was renamed to `casehub-connectors-core`, the rename was applied to the connectors repo but two consumers (`casehub-work-notifications` and `casehub-devtown-app`) were missed. The cross-repo dependency map in PLATFORM.md would have caught this immediately — but only if the map had existed and been consulted.

## Rule

Before merging any commit that changes a `<artifactId>` in a published module:

1. **Look up the artifact** in the [Cross-Repo Dependency Map](../PLATFORM.md#cross-repo-dependency-map)
2. **Update every listed consumer** — in the same session, before pushing
3. **Register the change** — update the map itself if the artifact name changed

## Step-by-Step

### Step 1 — Identify all consumers

Check the Cross-Repo Dependency Map in PLATFORM.md for the artifact being renamed.

If the artifact is not in the map, it has no known cross-repo consumers — but verify:

```bash
# Search all local repos for the old artifactId
for repo in ledger connectors work qhorus engine claudony devtown aml clinical; do
  echo "=== $repo ==="
  grep -r "<artifactId>OLD_ARTIFACT_ID</artifactId>" ~/claude/casehub/$repo \
    --include="pom.xml" --exclude-dir=target 2>/dev/null
done
```

### Step 2 — Update consumers in dependency order

Update repos in this order (dependencies before dependents):

```
ledger → connectors → work → qhorus → engine → claudony → applications
```

For each consumer pom.xml: replace `<artifactId>old-name</artifactId>` with `<artifactId>new-name</artifactId>` everywhere it appears (dependency declarations AND dependencyManagement).

### Step 3 — Build-verify each updated consumer

Use `build_project` via IntelliJ MCP or `mvn validate` to confirm each consumer resolves the new coordinate before moving on.

### Step 4 — Update the Cross-Repo Dependency Map

In PLATFORM.md, update the artifact name in every row that listed the old name.

### Step 5 — Update the maven-coordinate-standard checklist if needed

If the rename involved a convention change (e.g., adding `-core` suffix), note it in [maven-coordinate-standard.md](maven-coordinate-standard.md).

## Cross-Repo Dependency Map

The authoritative registry is the **Cross-Repo Dependency Map** table in [PLATFORM.md](../PLATFORM.md#cross-repo-dependency-map).

**Keeping it current:**
- Adding a cross-repo `<dependency>` → add a row to the map
- Removing a cross-repo `<dependency>` → remove the row
- Renaming an artifact → update the artifact column for all affected rows

## What "Published" Means

An artifact is published if it appears in another repo's `pom.xml` as a `<dependency>`. Even SNAPSHOT artifacts must be treated as published — every repo in the platform is built in sequence and a broken coordinate halts the full-stack build.

Internal-only artifacts (modules that are only referenced within their own reactor via `${project.version}`) do not need cross-repo propagation but still follow the [coordinate standard](maven-coordinate-standard.md).
