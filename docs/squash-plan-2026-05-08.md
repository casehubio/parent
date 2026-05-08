# Parent — Squash Plan (v2)
*Generated: 2026-05-08*  
*Working branch: `squash/wip-main-20260508-115155`*  
*Fixes applied: stale-ref priority, CI arc detection*  
*This is the plan — execution waits for YES.*

---

## Phase 0 — filter-repo (complete)

| | |
|---|---|
| Stripped | `HANDOFF.md` and `blog/` entries |
| Commits pruned (became empty) | 7 |
| Commits remaining for compaction | 89 |

---

## Summary

| | |
|---|---|
| Already clean (no action) | 36 commits |
| Compaction groups | 14 |
| Commits to absorb | 39 |
| **Estimated result** | **97 → ~50 commits — 39 absorbed, no content lost** |

---

## Already Clean — 36 commits (no action needed)

*Representative: ci, dashboard, platform, conventions*

---

## Compaction Groups — 14 groups

## feat: auto-deploy dashboard to GitHub Pages via Actions
*Compaction group 1 — 3 commits → 1*

| Commit | Action | Curated result |
|--------|--------|----------------|
| `49d50fe` feat: auto-deploy dashboard to GitHub Pages via Actions | ✅ KEEP | *(message adequate — unchanged)* |
| `cae27b1` fix(ci): fix false-green builds in dashboard and full-stack workflows | 🔽 SQUASH ↑ | *(absorbed — CI intermediate; superseded by final working state)* |
| `7049b14` fix(ci): fix clone auth, jq control-char errors, and repo scope | 🔽 SQUASH ↑ | *(absorbed — CI intermediate; superseded by final working state)*
📝 *body: full-stack-build.yml:* |

> **Result:** 1 commit.

---

## docs: add CLAUDE.md — ecosystem conventions, full-stack build, CI dashboards
*Compaction group 2 — 2 commits → 1*

| Commit | Action | Curated result |
|--------|--------|----------------|
| `a637d42` docs: add CLAUDE.md — ecosystem conventions, full-stack build, CI dashboard | ✅ KEEP | *(message adequate — unchanged)* |
| `7caa921` ci: fix dashboard repo name and PR dashboard base64 crash | 🔽 SQUASH ↑ | *(absorbed — CI intermediate; superseded by final working state)*
📝 *body: - dashboard.yml, pr-dashboard.yml: casehub-engine → engine (actual* |

> **Result:** 1 commit.

---

## docs: fix three broken CI badge links in README
*Compaction group 3 — 4 commits → 1*

| Commit | Action | Curated result |
|--------|--------|----------------|
| `4aa625b` docs: fix three broken CI badge links in README | ✅ KEEP | *(message adequate — unchanged)* |
| `2fbfb81` ci: change dashboard cadence to 15 minutes; page auto-refresh to 15 min | 🔽 SQUASH ↑ | *(absorbed — CI intermediate; superseded by final working state)*
📝 *body: Reduces unauthenticated API call frequency on the Pages site and keeps* |
| `55f4213` docs(claude): dashboard cadence 15 min, engine repo name correction | 🔽 SQUASH ↑ | *(absorbed — docs follow-on; message adequate)* |
| `0587780` ci: add casehub-connectors to full ecosystem build and dashboards | 🔽 SQUASH ↑ | *(absorbed — CI intermediate; superseded by final working state)*
📝 *body: aggregator.xml: casehub-connectors module added before quarkus-work* |

> **Result:** 1 commit.

---

## docs: remove remaining AgentMessageLedgerEntry stale refs in platform docs
*Compaction group 4 — 2 commits → 1*

| Commit | Action | Curated result |
|--------|--------|----------------|
| `74d6540` docs: remove remaining AgentMessageLedgerEntry stale refs in platform docs | ✅ KEEP | *(message adequate — unchanged)* |
| `336a9ee` chore: add casehub-assisteddev to ecosystem — repo list, dashboards, platfo | 🔽 SQUASH ↑ | *(absorbed — chore cleanup; message adequate)* |

> **Result:** 1 commit.

---

## docs(platform): add persistence module split rule — JPA entities must be in separate module
*Compaction group 5 — 2 commits → 1*

| Commit | Action | Curated result |
|--------|--------|----------------|
| `6db47a9` docs(platform): add persistence module split rule — JPA entities must be in | ✅ KEEP | *(message adequate — unchanged)* |
| `2fbe434` fix(ci): full-stack build now runs tests; add skip-ITs checkbox | 🔽 SQUASH ↑ | *(absorbed — CI intermediate; superseded by final working state)*
📝 *body: - Build each project from its own directory (cd <repo> && mvn install)* |

> **Result:** 1 commit.

---

## fix: update casehub-engine module references to casehub-engine-* artifactIds
*Compaction group 6 — 3 commits → 1*

| Commit | Action | Curated result |
|--------|--------|----------------|
| `6913508` fix: update casehub-engine module references to casehub-engine-* artifactId | ✅ KEEP | *(message adequate — unchanged)* |
| `efe684a` chore: move engine into casehub/ — update aggregator, workflow, docs | 🔽 SQUASH ↑ | *(absorbed — chore cleanup; message adequate)*
📝 *body: - aggregator.xml: casehub-engine → casehub/engine* |
| `41e75d8` chore: update ledger repo to casehubio/ledger — aggregator, workflows, docs | 🔽 SQUASH ↑ | *(absorbed — chore cleanup; message adequate)*
📝 *body: - pom.xml BOM: io.quarkiverse.ledger:quarkus-ledger* → io.casehub:casehub-ledger** |

> **Result:** 1 commit.

---

## refactor: rename quarkus-qhorus → qhorus/casehub-qhorus throughout docs and workflows
*Compaction group 7 — 7 commits → 1*
**Final message:** `refactor: rename quarkus-qhorus → qhorus/casehub-qhorus throughout docs and workflows; stale refs updated`

| Commit | Action | Curated result |
|--------|--------|----------------|
| `18fe74b` refactor: rename quarkus-qhorus → qhorus/casehub-qhorus throughout docs and | ✅ KEEP | *(see Final message above)* |
| `306b6e9` fix: update all stale repo name references post-rename | 🔽 SQUASH ↑ | *(absorbed — stale ref sweep; reflected in curated message)*
📝 *body: - full-stack-build.yml: module names aligned to short repo names* |
| `c5d4c6c` docs: fix stale repo name references post-rename | 🔽 SQUASH ↑ | *(absorbed — stale ref sweep; reflected in curated message)* |
| `90746bb` docs: fix stale repo name references post-rename | 🔽 SQUASH ↑ | *(absorbed — stale ref sweep; reflected in curated message)* |
| `e59acde` docs: fix stale repo name references post-rename | 🔽 SQUASH ↑ | *(absorbed — stale ref sweep; reflected in curated message)* |
| `bd912d7` chore: replace stale quarkus-* names with casehub-* across platform docs | 🔽 SQUASH ↑ | *(absorbed — stale ref sweep; reflected in curated message)*
📝 *body: Replaces quarkus-qhorus → casehub-qhorus and quarkus-ledger → casehub-ledger* |
| `38c46a4` chore: fix workflows — connectors/claudony into casehub/, rename repos to s | 🔽 SQUASH ↑ | *(absorbed — chore cleanup; message adequate)*
📝 *body: - full-stack-build.yml: clone connectors+claudony into casehub/; update MODULES/OUTCOMES* |

> **Result:** 1 commit.

---

## fix: complete CI/CD and build tooling for new repo layout
*Compaction group 8 — 12 commits → 1*

| Commit | Action | Curated result |
|--------|--------|----------------|
| `6df8cde` fix: complete CI/CD and build tooling for new repo layout | ✅ KEEP | *(message adequate — unchanged)* |
| `eaf1cd6` fix(ci): restore and correct full-stack-build.yml; fix dashboard repo names | 🔽 SQUASH ↑ | *(absorbed — CI intermediate; superseded by final working state)*
📝 *body: - Rewrote full-stack-build.yml from scratch with correct structure:* |
| `5a9296b` ci: add Clear Maven Cache workflow with per-repo selection | 🔽 SQUASH ↑ | *(absorbed — CI intermediate; superseded by final working state)*
📝 *body: Manually triggered workflow with a checkbox per repository (plus an* |
| `781f98f` ci: add pre/post state verification to Clear Maven Cache workflow | 🔽 SQUASH ↑ | *(absorbed — CI intermediate; superseded by final working state)*
📝 *body: Before deletion: lists each cache key, size, and branch ref.* |
| `f793335` ci: replace cache workflow with correct SNAPSHOT package deletion workflow | 🔽 SQUASH ↑ | *(absorbed — CI intermediate; superseded by final working state)*
📝 *body: Previous workflow targeted GitHub Actions runner caches (wrong).* |
| `3062d1f` ci: improve SNAPSHOT deletion with per-version output and verified absence | 🔽 SQUASH ↑ | *(absorbed — CI intermediate; superseded by final working state)*
📝 *body: Each deleted version is printed by name and ID with inline ok/FAILED.* |
| `d12e28e` ci: add GH_PAT scope checker workflow | 🔽 SQUASH ↑ | *(absorbed — CI intermediate; superseded by final working state)*
📝 *body: Reads X-OAuth-Scopes from the token's own API response headers and* |
| `e4791c6` ci: rewrite PAT checker to probe capabilities directly | 🔽 SQUASH ↑ | *(absorbed — CI intermediate; superseded by final working state)*
📝 *body: Header-based scope check fails for fine-grained PATs (no X-OAuth-Scopes).* |
| `605a68a` ci: add secret-presence check and expose auth error detail | 🔽 SQUASH ↑ | *(absorbed — CI intermediate; superseded by final working state)*
📝 *body: Checks GH_PAT is non-empty before attempting API calls.* |
| `34fb527` fix(ci): show actual error message on package delete failure | 🔽 SQUASH ↑ | *(absorbed — CI intermediate; superseded by final working state)* |
| `06683ca` fix(ci): fix set -e causing early exit on delete failure — use if-command p | 🔽 SQUASH ↑ | *(absorbed — CI intermediate; superseded by final working state)* |
| `84e4977` fix(ci): delete whole package when only one version remains (HTTP 400) | 🔽 SQUASH ↑ | *(absorbed — CI intermediate; superseded by final working state)*
📝 *body: GitHub returns 400 when deleting the last version — must use the* |

> **Result:** 1 commit.

---

## feat(ci): add workflow_dispatch to publish workflow
*Compaction group 9 — 3 commits → 1*

| Commit | Action | Curated result |
|--------|--------|----------------|
| `b02a5e4` feat(ci): add workflow_dispatch to publish workflow | ✅ KEEP | *(message adequate — unchanged)* |
| `19f5647` ci: standardise publish workflow — consistent build/test/publish/dispatch c | 🔽 SQUASH ↑ | *(absorbed — CI intermediate; superseded by final working state)* |
| `ef4ddee` ci: add group_filter to Clear SNAPSHOT Packages workflow | 🔽 SQUASH ↑ | *(absorbed — CI intermediate; superseded by final working state)*
📝 *body: Defaults to 'io.casehub' to prevent accidentally deleting external* |

> **Result:** 1 commit.

---

## feat(ci): add rebuild checkbox to clear-snapshot-packages workflow
*Compaction group 10 — 2 commits → 1*

| Commit | Action | Curated result |
|--------|--------|----------------|
| `0675ff2` feat(ci): add rebuild checkbox to clear-snapshot-packages workflow | ✅ KEEP | *(message adequate — unchanged)* |
| `4863928` ci: use GH_PAT for cross-repo repository_dispatch (GITHUB_TOKEN is repo-sco | 🔽 SQUASH ↑ | *(absorbed — CI intermediate; superseded by final working state)* |

> **Result:** 1 commit.

---

## test: rerun failing tests up to 2x to surface flaky vs broken
*Compaction group 11 — 2 commits → 1*

| Commit | Action | Curated result |
|--------|--------|----------------|
| `dedd76e` test: rerun failing tests up to 2x to surface flaky vs broken | ✅ KEEP | *(message adequate — unchanged)* |
| `7ff80a2` ci: exclude quarkus-langchain4j from standard build and package clear by de | 🔽 SQUASH ↑ | *(absorbed — CI intermediate; superseded by final working state)* |

> **Result:** 1 commit.

---

## docs(conventions): Qhorus EVENT content null + oversight channel allowedTypes
*Compaction group 12 — 2 commits → 1*

| Commit | Action | Curated result |
|--------|--------|----------------|
| `1e1bcb9` docs(conventions): Qhorus EVENT content null + oversight channel allowedTyp | ✅ KEEP | *(message adequate — unchanged)* |
| `8dea3ac` docs: session handover 2026-05-01 — CI chain repair | 🔽 SQUASH ↑ | *(absorbed — session handover survived filter-repo; mixed content)* |

> **Result:** 1 commit.

---

## docs: correct LangChain4j/CaseHub layering — three distinct levels, patterns not redundant at different granularities
*Compaction group 13 — 2 commits → 1*

| Commit | Action | Curated result |
|--------|--------|----------------|
| `7072de6` docs: correct LangChain4j/CaseHub layering — three distinct levels, pattern | ✅ KEEP | *(message adequate — unchanged)* |
| `ae1b52d` docs: session handover 2026-05-04 — platform positioning and incremental bu | 🔽 SQUASH ↑ | *(absorbed — session handover survived filter-repo; mixed content)* |

> **Result:** 1 commit.

---

## docs: update casehub-qhorus platform doc and add actor-type mapping convention
*Compaction group 14 — 7 commits → 1*
⚠️ **Net no-op pair:** absorbs both a migrate and restore — combined tree effect is zero for those files.

| Commit | Action | Curated result |
|--------|--------|----------------|
| `35303f1` docs: update casehub-qhorus platform doc and add actor-type mapping convent | ✅ KEEP | *(message adequate — unchanged)* |
| `ee9459c` chore: rename casehub-assisteddev to casehub-devtown across docs and workfl | 🔽 SQUASH ↑ | *(absorbed — chore cleanup; message adequate)* |
| `3f44903` chore: migrate CLAUDE.md and methodology artifacts to workspace | 🔽 SQUASH ↑ | *(absorbed — chore cleanup; message adequate)* |
| `0a7cb71` chore: restore CLAUDE.md to project repo (workspace symlinks to this) | 🔽 SQUASH ↑ | *(absorbed — chore cleanup; message adequate)* |
| `bda54ec` chore: move gastown/devtown analysis docs to casehub-devtown | 🔽 SQUASH ↑ | *(absorbed — chore cleanup; message adequate)* |
| `4c3b930` chore: ignore wksp symlink | 🔽 SQUASH ↑ | *(absorbed — chore cleanup; message adequate)* |
| `88e2cd0` chore: add aml and clinical to peer repos list | 🔽 SQUASH ↑ | *(absorbed — chore cleanup; message adequate)* |

> **Result:** 1 commit.

---

## AFTER — what `git log --oneline` will show (estimated)

```
  97  commits on main (original)
   -7  pruned by filter-repo
   -39  absorbed by squash
  ──────────────────────────────
   ~50  commits — no content lost
```

Sample (most recent 10 KEEP commits):
```
  87d511f  docs: add maven-submodule-folder-naming convention — short names, no repo prefix
  24906d5  docs: split application tier out of PLATFORM.md into APPLICATIONS.md
  bc0cbf0  docs: add per-repo deep-dives for casehub-devtown, casehub-aml, casehub-clinical
  608d0af  docs: restore PLATFORM.md (accidentally emptied in 41e75d8) and update for current re
  1875c9a  feat(ci): add include_applications input to incremental build — devtown/aml/clinical 
  35303f1  docs: update casehub-qhorus platform doc and add actor-type mapping convention
  7072de6  docs: correct LangChain4j/CaseHub layering — three distinct levels, patterns not redu
  ec19926  docs: tutorial strategy — layered examples, AML primary tutorial, clinical trials sho
  c2af024  docs: use case analysis — market fit and community fit scoring for two selected examp
  148d8ab  docs: revise gastown analysis — Doltgres closes time-travel/branching gaps, GDPR Art.
```

---

## Interval tree verification

  diff=0  [docs: add maven-submodule-folder-naming convention — short names, no r]
  diff=0  [docs: update gastown gaps analysis — P0.1 engine done, P1.4 closed, fi]
  diff=0  [fix(ci): fix set -e causing early exit on delete failure — use if-comm]
  diff=0  [refactor: rename quarkus-qhorus → qhorus/casehub-qhorus throughout doc]
  diff=0  [docs: update platform docs for qhorus normative ledger changes]

---

## Approval

Reply **YES** to execute, or tell me which groups to change.
