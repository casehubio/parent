# Per-Repo Documentation Audit Process

Template for auditing each repo's documentation against current code.
Created as part of #433 — Documentation audit, RAG optimization & freshness gate.

## Prerequisites

- GitHub issue exists for the repo (e.g. #434 for platform)
- Access to the repo's git history, issues, and blog entries
- IntelliJ MCP available for semantic code navigation

## Process (7 steps)

### 1. Delta Analysis

Identify what changed since the guide was last updated:

```bash
git log --since=<guide-last-updated> --oneline
```

Classify changes by impact:
- New modules or removed modules
- Renamed types or moved packages
- New SPIs or changed SPI contracts
- Removed features or deprecated APIs
- Architectural shifts (new patterns, changed conventions)

### 2. Source Mining

Reconstruct the narrative behind changes using multiple sources:

- **Blog entries** — workspace `blog/` + published `casehubio.github.io/_articles/`
- **GitHub issues** — closed issues since last sync, linked PRs
- **Commit messages** — `git log --oneline` for the relevant period
- **ARC42STORIES.MD** — architectural layer changes

### 3. Guide Update

Fix consumer guide and contributor guide sections affected by the delta.
Prioritize accuracy over style — getting the facts right matters more
than perfect prose.

For each section:
1. Read the section's current claims
2. Verify each claim against the actual code (use IntelliJ MCP)
3. Fix incorrect claims with specific code references
4. Add missing capabilities that appeared since last sync
5. Remove documented features that no longer exist

### 4. Structural Anchor Insertion

Add YAML frontmatter with structural anchors to each updated section
(or new capability chunk if decomposing).

```yaml
---
capability: <topic>
audience: consumer
repo: casehub-<name>
anchors:
  classes:
    - io.casehub.<package>.<ClassName>
  spis:
    - io.casehub.<package>.spi.<SpiName>
  config-keys:
    - casehub.<module>.<property>
  protocols:
    - <protocol-name>
---
```

Every anchor must resolve in the codebase. Verify with `ide_find_class`
or `git ls-files`.

### 5. Guide Decomposition

Extract sections exceeding 40 lines into standalone capability chunks:

- Create `docs/guides/capabilities/<topic>.md` in the child repo
- Add YAML frontmatter with structural anchors
- Replace the section in the guide with a link: `→ [capabilities/<topic>.md](capabilities/<topic>.md)`
- Update `docs/capabilities.md` in parent (add the chunk link)

Follow the platform template:
`docs/repos/casehub-platform/capabilities/notifications.md`

### 6. Arc42Stories Check

If ARC42STORIES.MD exists, run the 3-check sweep:

1. **Issue status:** `gh issue view N` for every §12 reference
2. **Class name existence:** verify §9.4 Key files entries resolve
3. **File path validity:** verify all referenced paths still exist

### 7. Exit Criteria Verification

Before closing the issue, verify all three criteria:

- [ ] All consumer guide sections verified against current code
- [ ] All structural anchors validated (anchored class/SPI exists)
- [ ] Evidence commit with the fixes

Close the per-repo GitHub issue with the evidence commit SHA.

## Priority Order

Audit repos in dependency blast radius order:

| Wave | Repos | Rationale |
|------|-------|-----------|
| 1 (foundation) | platform, worker, ledger, connectors, work, qhorus, eidos, neocortex, engine, iot | API/SPI changes cascade to all consumers |
| 2 (orchestration) | ras, desiredstate, agency, mosaic, claudony, openclaw, workers, ops, pages | Integration layer |
| 3 (application) | devtown, aml, clinical, life, drafthouse, quarkmind, soc, fsitrading, chat-app | Leaf nodes |
