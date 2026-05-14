---
id: PP-20260512-coord
title: "Maven coordinate standard for all casehubio repos"
type: rule
scope: universal
applies_to: "All casehubio Maven repos"
severity: important
refs: [maven-submodule-folder-naming.md, artifact-rename-propagation.md]
violation_hint: "Inconsistent coordinates break the cross-repo dependency map and make impact analysis unreliable"
created: 2026-05-12
---

# Maven Coordinate Standard — All CaseHub Repos

**Applies to:** Every `pom.xml` across every casehubio repo  
**Severity:** Important — inconsistency breaks the cross-repo dependency map and makes artifact renames undetectable

## The Standard

| Dimension | Rule | Example |
|-----------|------|---------|
| `groupId` | `io.casehub` for every module in every repo | `io.casehub` |
| `version` | `0.2-SNAPSHOT` platform-wide; bumped together | `0.2-SNAPSHOT` |
| Root parent `artifactId` | `casehub-{repo}-parent` | `casehub-work-parent` |
| Child module `artifactId` | `casehub-{repo}-{function}` | `casehub-work-queues` |
| Runtime module `artifactId` | `casehub-{repo}` (no `-runtime` suffix) | `casehub-work` |
| Child module `<parent><artifactId>` | Must match the root parent exactly | `casehub-work-parent` |
| Folder name | Short and descriptive — **no repo prefix** | `queues/` not `casehub-work-queues/` |

The folder name rule is documented in detail in [maven-submodule-folder-naming.md](maven-submodule-folder-naming.md).

## Standard Module `artifactId` Suffixes

| Module role | `artifactId` suffix | Folder name |
|------------|-------------------|-------------|
| Public SPI / API | `-api` | `api` |
| Runtime implementation | *(none — just `casehub-{repo}`)* | `runtime` |
| Quarkus deployment processor | `-deployment` | `deployment` |
| Test utilities | `-testing` | `testing` |
| Runnable examples parent | `-examples` | `examples` |
| Integration tests | `-integration-tests` | `integration-tests` |
| Capability module | `-{capability}` | `{capability}` |

## Examples

```
casehub-ledger-parent       ← root pom
  casehub-ledger-api        ← api/ folder
  casehub-ledger            ← runtime/ folder (no -runtime suffix)
  casehub-ledger-deployment ← deployment/ folder

casehub-work-parent
  casehub-work-api          ← api/
  casehub-work-core         ← core/
  casehub-work              ← runtime/
  casehub-work-queues       ← queues/
  casehub-work-notifications ← notifications/
```

## Verification Checklist

Run before any commit touching `pom.xml`:

- [ ] All `<groupId>` elements are `io.casehub`
- [ ] All `<version>` elements match the platform version
- [ ] Root `<artifactId>` is `casehub-{repo}-parent`
- [ ] Every child `<parent><artifactId>` matches the root exactly
- [ ] Child `<artifactId>` follows `casehub-{repo}-{function}`
- [ ] Folder name for each module is the short form (see folder naming protocol)
- [ ] Any new cross-repo `<dependency>` is registered in [PLATFORM.md — Cross-Repo Dependency Map](../PLATFORM.md)

## Anti-Patterns

```xml
<!-- Wrong groupId -->
<groupId>dev.claudony</groupId>                  ✗
<groupId>io.casehub.claudony</groupId>           ✗
<groupId>io.casehub</groupId>                    ✓

<!-- Wrong root artifactId -->
<artifactId>casehub-devtown</artifactId>         ✗  (missing -parent)
<artifactId>claudony-parent</artifactId>         ✗  (wrong prefix)
<artifactId>casehub-devtown-parent</artifactId>  ✓

<!-- Wrong child artifactId -->
<artifactId>devtown-domain</artifactId>          ✗  (missing casehub- prefix)
<artifactId>claudony-core</artifactId>           ✗  (wrong prefix)
<artifactId>casehub-devtown-domain</artifactId>  ✓

<!-- Wrong parent reference in child pom -->
<artifactId>casehub-devtown</artifactId>         ✗  (points to old non-parent artifactId)
<artifactId>casehub-devtown-parent</artifactId>  ✓
```
