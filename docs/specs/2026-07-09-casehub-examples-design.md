# casehub-examples: Aggregated Examples Repository

> **Date:** 2026-07-09
> **Status:** Draft
> **GitHub repo:** `casehubio/examples`

---

## 1. Problem

CaseHub has runnable examples spread across 9+ repos. A developer evaluating the platform
must clone multiple repos, figure out prerequisites per repo, and navigate inconsistent
README formats to find and run examples. There is no single place to browse, compare,
and run all CaseHub examples.

## 2. Solution

A single read-only repository (`casehubio/examples`) that aggregates the `examples/`
directory from every CaseHub repo that has one. Users clone one repo and can browse and
run all examples — Maven, Docker Compose, and TypeScript — without knowing about the
multi-repo structure.

The repo is synced automatically after every successful full build, using the same
`ecosystem-build-succeeded` dispatch that already syncs `casehub-all`. SHAs are pinned
to the last successful build — examples always match a known-good state.

## 3. Naming Conventions

| Context | Convention | Example |
|---------|-----------|---------|
| GitHub repo name | Short, no `casehub-` prefix | `casehubio/examples` |
| Directory names in this repo | `<short-repo-name>-examples` | `ledger-examples/`, `work-examples/` |
| Maven artifact IDs | `casehub-` prefix | `casehub-ledger-examples` |
| Source repo example folders | Short name `examples/` | `ledger/examples/` |

The `-examples` suffix on directory names disambiguates — all source repos call their
directory `examples/`, so the repo name prefix is needed in the aggregate.

## 4. Repository Structure

```
casehubio/examples/
├── pom.xml                          ← standalone aggregator (not in official build chain)
├── README.md                        ← landing page: overview, prerequisites, quick start
├── ADDING-EXAMPLES.md               ← LLM-executable checklist for onboarding new repos
├── sync-config.json                 ← maps source repos to directory names and types
├── .github/workflows/
│   └── sync-examples.yml            ← triggered by ecosystem-build-succeeded
│
├── ledger-examples/                 ← synced from ledger/examples/ via subtree-split
│   ├── README.md
│   ├── order-processing/
│   ├── merkle-verification/
│   └── ...                          ← 13 standalone Quarkus apps
│
├── work-examples/                   ← synced from work/examples/
│   ├── README.md
│   └── src/...                      ← single Quarkus app, 17 scenarios
│
├── qhorus-examples/                 ← synced from qhorus/examples/
│   ├── README.md
│   ├── agent-communication/
│   ├── normative-layout/
│   └── type-system/
│
├── eidos-examples/                  ← synced from eidos/examples/
│   ├── README.md
│   └── agent-scenarios/
│
├── desiredstate-examples/           ← synced from desiredstate/examples/
│   ├── README.md
│   ├── pipeline/
│   ├── dungeon/
│   ├── expansion/
│   └── spatial/
│
├── neocortex-examples/              ← synced from neocortex/examples/
│   ├── README.md
│   ├── example-cbr/
│   ├── example-rag-pipeline/
│   └── example-text-analysis/
│
├── openclaw-examples/               ← synced from openclaw/examples/ (Docker Compose)
│   ├── README.md
│   ├── incident-response/
│   ├── multi-agent-dev-team/
│   └── trading-oversight/
│
├── blocks-ui-examples/              ← synced from blocks-ui/examples/ (TypeScript/Vite)
│
└── pages-examples/                  ← synced from pages/examples/ (TypeScript/webpack)
```

## 5. Sync Mechanism

### 5.1 Approach: subtree-split in CI

Each sync cycle runs entirely in CI on throwaway clones. Source repos are never
modified. The `--squash` flag produces one commit per sync per repo — `git log
ledger-examples/` shows a sequence of squashed sync commits, each with the
source SHA range in the commit message for traceability. Individual source
commits are not preserved in the aggregator; developers who need per-commit
history should consult the source repo. The benefit over file-copy is that git
tracks per-file diffs within each squash — `git diff` between syncs shows
exactly which files changed and how, rather than replacing all files each time.

### 5.2 Workflow: `sync-examples.yml`

Triggered by:
- `repository_dispatch` type `ecosystem-build-succeeded`
- `workflow_dispatch` (manual)

**Per source repo (from `sync-config.json`):**

1. Clone source repo at pinned SHA (from `client_payload.shas`) into `/tmp/<repo>`
2. Check that `examples/` directory exists — skip silently if absent
3. Run `git subtree split --prefix=examples -b examples-only` on the throwaway clone
4. In the casehub-examples checkout:
   - First time: `git subtree add --prefix=<repo>-examples /tmp/<repo> examples-only --squash`
   - Subsequent: `git subtree pull --prefix=<repo>-examples /tmp/<repo> examples-only --squash`
5. Clean up `/tmp/<repo>`

After all repos are processed successfully, push to main.

**Failure handling:**

- **Per-repo failure:** If a subtree-split or subtree-pull fails for one repo (e.g.,
  merge conflict from directory restructuring), the workflow logs the failure, skips
  that repo, and continues processing remaining repos. The final push includes all
  repos that succeeded.
- **Build verification:** After all subtree operations, the workflow runs `mvn test
  --fail-at-end` on the aggregator. If the build fails, the workflow does NOT push —
  it fails the GitHub Actions run, leaving the repo at the last known-good state.
- **Notification:** Failed sync runs post a GitHub Actions workflow failure. Repository
  watchers receive standard GitHub notification. No custom alerting beyond this —
  the sync runs on every successful build, so transient failures self-heal on the
  next build.
- **Concurrent runs:** GitHub Actions serialises workflow runs on the same branch via
  `concurrency: { group: sync-examples, cancel-in-progress: false }`. A second
  dispatch queues behind the first; no push conflict is possible.
- **SHA mismatch:** If a repo's SHA is not in the dispatch payload, the workflow
  skips it (uses whatever is already in the aggregator for that repo).

### 5.2b Local sync script: `sync.sh`

A developer who wants their local clone at HEAD (rather than the last
successful build SHA) runs:

```bash
./sync.sh              # update all subtrees to HEAD of each source repo
```

The script reads `sync-config.json`, clones each source repo at HEAD into
a temp directory, runs `git subtree split --prefix=examples`, and
`git subtree pull --prefix=<repo>-examples ... --squash`. Same mechanics
as the CI workflow but targeting HEAD instead of pinned SHAs.

This is analogous to casehub-all's `sync.sh` (which runs
`git submodule update --remote --merge`), adapted for subtrees.

### 5.3 Initial seeding

The first sync for each repo uses `git subtree add`. The workflow checks whether
the `<repo>-examples/` directory already exists in the working tree:
- **Directory absent:** `git subtree add --prefix=<repo>-examples ...`
- **Directory present:** `git subtree pull --prefix=<repo>-examples ...`

### 5.4 sync-config.json

```json
{
  "repos": [
    {"name": "ledger",      "org": "casehubio", "type": "maven"},
    {"name": "work",        "org": "casehubio", "type": "maven"},
    {"name": "qhorus",      "org": "casehubio", "type": "maven"},
    {"name": "eidos",       "org": "casehubio", "type": "maven"},
    {"name": "desiredstate", "org": "casehubio", "type": "maven"},
    {"name": "neocortex",   "org": "casehubio", "type": "maven"},
    {"name": "openclaw",    "org": "casehubio", "type": "docker"},
    {"name": "blocks-ui",   "org": "casehubio", "type": "typescript"},
    {"name": "pages",       "org": "casehubio", "type": "typescript"}
  ]
}
```

Only repos with an existing `examples/` directory are listed. Adding a repo to
`sync-config.json` is the deliberate opt-in — gated by the ADDING-EXAMPLES.md
checklist (§8). Repos without examples (e.g., blocks) are added when ready, not
pre-populated.

The `type` field determines whether the repo's examples are included in the
aggregator POM (`maven`) or only in the README with standalone run instructions
(`docker`, `typescript`).

### 5.5 Dispatch integration

`sync-casehub-all.py` in parent is extended to dispatch to both repos:

```python
# Existing: dispatch to casehub-all
subprocess.run(['gh', 'api', 'repos/casehubio/casehub-all/dispatches', '--input', '-'], ...)

# New: also dispatch to examples
subprocess.run(['gh', 'api', 'repos/casehubio/examples/dispatches', '--input', '-'], ...)
```

Same payload, same SHAs. The examples workflow reads `sync-config.json` to know
which repos to sync and skips any repo whose SHA is not in the payload.

**SHA key convention:** `sync-casehub-all.py` converts dashes to underscores in
SHA keys (`blocks-ui` → `blocks_ui`). The sync workflow must apply the same
transformation when looking up `client_payload.shas[name.replace('-', '_')]`.

## 6. Aggregator POM

The top-level `pom.xml` is a **standalone aggregator** — it does not inherit from
`casehub-parent` and is not part of the official CaseHub build chain.

```xml
<groupId>io.casehub</groupId>
<artifactId>casehub-examples</artifactId>
<packaging>pom</packaging>
```

**Module listing:** Only Maven example sets. Each `<module>` entry points at the
example set's own aggregator POM — one entry per repo. The example set's aggregator
handles listing its own subdirectories as modules.

work, qhorus, and eidos already have aggregator POMs in their `examples/` directory.
ledger, desiredstate, and neocortex currently lack one — each needs a minimal
`<packaging>pom</packaging>` with `<modules>` listing its subdirectories. This is a
one-file prerequisite change per repo (alongside the `<relativePath/>` fix), tracked
as implementation work items. Without it, new examples added to these repos are synced
but silently excluded from the build because the casehub-examples POM doesn't list them.

Non-Maven example sets (openclaw, blocks-ui, pages) are excluded from the POM.

**Parent POM resolution:** Example POMs follow two patterns across the ecosystem:

- **Standalone** (ledger): No parent inheritance. Each example POM declares its own
  `groupId`, imports the Quarkus BOM directly, and declares CaseHub dependency versions
  explicitly. These work without modification after subtree-split.
- **Parent-inherited** (work, qhorus, eidos, desiredstate, neocortex): POMs inherit
  from their source repo's parent POM (e.g., `casehub-work-parent:0.2-SNAPSHOT`).
  After subtree-split, the parent POM is not in the extracted tree.

For parent-inherited examples to build after extraction, two prerequisites apply:

1. **Source repo POMs must set `<relativePath/>`** (empty, self-closing) in their
   `<parent>` block. This tells Maven to skip the filesystem parent lookup and resolve
   directly from the configured repository. Without this, Maven either warns (no
   explicit relativePath) or resolves the wrong POM (explicit relativePath like
   `../../pom.xml` pointing at the aggregator instead of the source parent).
   This is a one-time change per source repo — it does not affect the source repo
   build because Maven still resolves the parent from the reactor.
2. **GitHub Packages must be configured** as a Maven repository, so Maven can resolve
   the parent POMs. This is already a prerequisite for dependency resolution (below).

The `<relativePath/>` changes are prerequisite work items for each source repo, tracked
alongside this spec's implementation.

**Profile handling:** The qhorus examples POM has a `with-llm-examples` profile that
includes the `agent-communication` module. The aggregator does NOT activate this
profile by default — `mvn test` runs only the CI-safe examples (type-system,
normative-layout). The root README documents activating the profile for developers
who want to run LLM examples: `mvn test -Pwith-llm-examples -pl qhorus-examples`.

**Dependency resolution:** The source examples depend on CaseHub modules (SNAPSHOT or
release versions). Prerequisites depend on the current release lifecycle:

- **Now (pre-release):** Configure GitHub Packages as a Maven repository (one-time setup)
- **Future (released to Maven Central):** No special config needed

The README documents the current prerequisite in a single "Prerequisites" section.

## 7. Root README

Structure:

1. **What this is** — one paragraph: clone one repo, run all CaseHub examples
2. **Prerequisites** — Java version, Maven, repository config (GitHub Packages
   or Maven Central depending on release stage)
3. **Quick start** — `git clone`, `mvn test` for all Maven examples, or
   `mvn quarkus:dev -pl ledger-examples/order-processing` for a specific one
4. **Example sets table** — each row links to the child README,
   shows the type (Quarkus / Docker Compose / TypeScript), and summarises
   the capabilities demonstrated
5. **Running non-Maven examples** — per-type prerequisites and pointers to each
   set's own README:
   - **openclaw** (Docker Compose): requires Docker. Images are built from the
     source repo — the README documents `docker compose up` and any required
     environment variables. No external registry dependency.
   - **blocks-ui** (TypeScript/Vite): requires Node.js 20+. Run `npm install`
     then `npm run dev`. May require a running CaseHub backend — documented
     per example.
   - **pages** (TypeScript/webpack): requires Node.js 20+. Run `npm install`
     then `npm run dev`. Playwright tests require `npx playwright install`.
6. **About this repo** — read-only, synced from source repos after each successful
   full build, links to source repos for contributions/bug fixes

## 8. ADDING-EXAMPLES.md

An LLM-executable checklist — instructions for a Claude session to follow when
onboarding a new repo's examples into casehub-examples.

Steps:

1. Verify the source repo has an `examples/` directory with at least one runnable example
2. Verify example POMs either use standalone pattern (like ledger) or have
   `<relativePath/>` in their `<parent>` block
3. Verify the source repo has an aggregator POM at `examples/pom.xml` that lists all
   example subdirectories as `<modules>`. If not, create one — this ensures new examples
   added to the source repo are automatically included in the aggregator build.
4. Add the repo to `sync-config.json` — name, org, type (maven/docker/typescript).
   This is the deliberate opt-in — repos not in this file are never synced.
5. Run the sync locally to pull the examples via subtree-split
6. If Maven: update the top-level `pom.xml` — add a single `<module>` entry for the
   repo's example set directory (e.g., `<module>ledger-examples</module>`). The repo's
   own aggregator POM handles its internal modules.
7. Verify the build — `mvn test` passes with the new examples included
8. Update the root `README.md` — add a row to the example sets table
9. Commit and push — the automated sync keeps it current from here

## 9. What This Design Does NOT Cover

These are follow-up concerns, not part of this implementation. Each will be tracked
as a GitHub issue on the appropriate repo when this spec is accepted:

- **Capability matrix standardisation** — creating a consistent `CAPABILITIES.md`
  format across source repos. Requires touching each source repo. (Issue on parent)
- **README template standardisation** — making prerequisites, run instructions,
  and structure consistent across example READMEs. Requires touching each source repo.
  (Issue on parent)
- **POJO examples** — all current examples require Quarkus. Plain-Java examples
  using only the API/SPI modules may be added later. (Issue on examples repo)
- **Renaming `casehub-`-prefixed repos** — `casehub-desiredstate`, `casehub-pages`,
  `casehub-ras`, `casehub-ops` violate the short-name convention. Separate fix.
  (Issue on parent)
- **Web page integration** — linking examples into a documentation website or
  tutorials portal. Future work. (Issue on examples repo)

## 10. Relationship to Prior Decisions

### 10.1 tutorial-strategy.md §11

`docs/tutorial-strategy.md` §11 decided "Examples in each project repo, not a
separate tutorials repo." This design does not contradict that — examples remain
in their source repos as the source of truth. `casehub-examples` is a read-only
aggregation for convenience, not a replacement. Edits always happen in the source
repo and flow down via the sync.

**Drift mitigation:** The §11 concern was specifically about drift between separated
examples and their source. The sync mechanism addresses this:

- **Staleness detection:** The sync commits include the source SHA in the commit
  message. The root README can display a "last synced" timestamp per example set.
  If the aggregator is more than one build behind (e.g., sync failures), this is
  visible.
- **Self-healing:** The sync runs on every `ecosystem-build-succeeded` dispatch.
  Transient failures (one bad subtree-pull) self-heal on the next successful build
  — no manual intervention required.
- **Build verification:** The sync workflow runs `mvn test` before pushing. If
  extracted examples don't build, the push is blocked — the aggregator never
  enters a broken state.
- **Single source of truth:** All edits happen in source repos. The aggregator
  has no PRs, no direct commits. There is no "two sources of truth" — the
  aggregator is a derived artifact, like generated documentation.

### 10.2 casehub-all

`casehub-all` is an existing read-only meta-repo that aggregates all CaseHub repos
using git submodules, synced on the same `ecosystem-build-succeeded` dispatch. It
serves a different purpose: full-ecosystem checkout for developers who want to
build, explore, or navigate across all repos simultaneously.

`casehub-examples` differs in three ways:

1. **Scope:** Only `examples/` directories, not full repos. A user cloning
   casehub-examples gets ~50MB of runnable examples, not ~2GB of platform code.
2. **Mechanism:** Subtree-split extracts subdirectories with commit history.
   Submodules (casehub-all's approach) point at full repo checkouts — there is no
   way to filter a submodule to a subdirectory.
3. **Audience:** Evaluators and new developers who want to run examples without
   understanding the multi-repo structure. casehub-all targets contributors who
   need the full source.

The two repos share infrastructure (same dispatch trigger, same SHAs) but serve
complementary audiences. Extending casehub-all with an "examples view" is not
feasible — submodules are full-repo pointers, not directory filters.

## 11. Decisions

| Decision | Rationale |
|----------|-----------|
| Subtree-split sync over submodules | Submodules point at full repos, not subdirectories. Subtree-split extracts just `examples/`. The split runs on throwaway clones — source repos are never touched. |
| Subtree-split over file-copy | File copy replaces all files each sync — git sees every file as changed. Subtree-split with `--squash` produces minimal diffs (only actually-changed files appear in the diff) and records the source SHA range for traceability. Individual source commits are not preserved — consult the source repo for per-commit history. |
| Standalone aggregator POM | Not part of the official build chain. Example sets have their own dependency resolution — the aggregator just orchestrates `mvn test` across them. |
| Include non-Maven examples | All example types belong — but only Maven ones are in the POM. Docker Compose and TypeScript examples have standalone run instructions. |
| Read-only repo | Bug fixes go to the source repo. casehub-examples syncs on next successful build. Avoids bidirectional complexity. |
| Short directory names with `-examples` suffix | Source repos all use `examples/` internally. The suffix disambiguates in the aggregate while following the short-name convention. |
| Same `ecosystem-build-succeeded` trigger | One event, multiple consumers. SHAs are always from a known-good build state. |
