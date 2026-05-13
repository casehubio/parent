# parent Workspace

**Project repo:** /Users/mdproctor/claude/casehub/parent
**Workspace type:** public

## Session Start

Run `add-dir /Users/mdproctor/claude/casehub/parent` before any other work.

## Artifact Locations

| Skill | Writes to |
|-------|-----------|
| brainstorming (specs) | `specs/` |
| writing-plans (plans) | `plans/` |
| handover | `HANDOFF.md` |
| idea-log | `IDEAS.md` |
| design-snapshot | `snapshots/` |
| java-update-design / update-primary-doc | `design/JOURNAL.md` (created by `epic`) |
| adr | `adr/` |
| write-blog | `blog/` |

## Structure

- `HANDOFF.md` — session handover (single file, overwritten each session)
- `IDEAS.md` — idea log (single file)
- `specs/` — brainstorming / design specs (superpowers output)
- `plans/` — implementation plans (superpowers output)
- `snapshots/` — design snapshots with INDEX.md (auto-pruned, max 10)
- `adr/` — architecture decision records with INDEX.md
- `blog/` — project diary entries with INDEX.md
- `design/` — epic journal (created by `epic` at branch start)

## Git Discipline

Two git repositories are active in every session:
- **Workspace** (`/Users/mdproctor/claude/public/casehub`) — methodology artifacts: handover, blog (staging before publish), plans, snapshots
- **Project repo** (`/Users/mdproctor/claude/casehub/parent`) — source code, ADRs (`docs/adr/`), specs

Before any git operation, run `git rev-parse --show-toplevel` to confirm which repo is currently active. Do not assume — the session may have opened in either. cd to the correct repo before staging:
- Source code commits → project repo
- Methodology artifacts → workspace


## Rules

- All methodology artifacts go here, not in the project repo
- Promotion to project repo is always explicit — never automatic
- Workspace branches mirror project branches — switch both together

## Routing

| Artifact   | Destination | Notes |
|------------|-------------|-------|
| adr        | project     | lands in `docs/adr/` |
| blog       | workspace   | staged here; published to mdproctor.github.io via publish-blog |
| design     | workspace   | epic journal (`design/JOURNAL.md`) |
| snapshots  | workspace   | |
| specs      | project     | lands in project `docs/` |
| plans      | workspace   | |
| handover   | workspace   | |

---

# CaseHub Parent

## Project Type

type: java

## Repository Role

Root parent POM for the CaseHub ecosystem. Owns shared build configuration, CI/CD workflows, cross-module conventions, and the full-stack build orchestration.

**Peer repos (each has its own Claude session — do not commit to these):**
ledger, connectors, work, qhorus, engine, claudony, quarkus-langchain4j, devtown, aml, clinical

## Build Commands

```bash
# Install parent POM only
mvn --batch-mode install

# Publish to GitHub Packages (CI only — requires GITHUB_TOKEN)
mvn --batch-mode deploy -DskipTests
```

## CI/CD Workflows

| Workflow | Trigger | Purpose |
|---|---|---|
| `publish.yml` | push/main, dispatch, manual | Publish parent POM; dispatch to ledger + connectors |
| `full-stack-build.yml` | manual only | Full sequential rebuild of all repos — always rebuilds everything |
| `incremental-full-stack-build.yml` | manual only | SHA-keyed incremental build — BUILD/TEST/SKIP per module based on what changed |
| `clear-snapshot-packages.yml` | manual only | Delete SNAPSHOT artifacts from GitHub Packages |

**Key rule:** Cross-repo `repository_dispatch` requires `GH_TOKEN: ${{ secrets.GH_PAT }}` (classic PAT). `GITHUB_TOKEN` is repo-scoped only and returns 403 on cross-repo calls.

**langchain4j** is excluded from standard builds by default. Tick `include_langchain4j` only when that fork has changed.

## Cross-Repo Conventions

Conventions shared across all modules live in `docs/protocols/`. Each file is self-contained. See `docs/protocols/INDEX.md` for the full list.

**Critical:** Never commit or push to peer repo directories (`../ledger`, `../work`, etc.). Each repo has its own Claude session. For cross-repo fixes, create a GitHub issue on the target repo instead.

## Scripts

`scripts/incremental-build-decision.sh` — pure bash decision function for the incremental build. Given a module's current SHA, previous SHA, and dep SHAs, outputs `BUILD`, `TEST`, or `SKIP`. No side effects.

`scripts/tests/incremental-build-decision.bats` — bats test suite (49 tests) covering all BUILD/TEST/SKIP scenarios. Run with: `bats scripts/tests/incremental-build-decision.bats`

Prereq: `brew install bats-core`

## Testing

Surefire is configured in this parent POM with `rerunFailingTestsCount=2` — failing tests are retried twice before being marked as failures, surfacing flaky vs consistently broken.

**Config architecture:** https://raw.githubusercontent.com/mdproctor/parent/main/docs/config-architecture.md

## Writing Style Guide

**The writing style guide at `~/claude-workspace/writing-styles/blog-technical.md` is mandatory for all blog and diary entries.** Load it in full before drafting. Complete the pre-draft voice classification (I / we / Claude-named) before generating any prose. Do not show a draft without verifying it against the style guide.

---

## Project Artifacts

Paths that are project content (not workspace noise). Skills use this to avoid
filtering or dropping commits that touch these paths.

| Path | What it is |
|------|------------|
| `CLAUDE.md` | Project conventions |
| `docs/` | Platform documentation (PLATFORM.md, APPLICATIONS.md, repo deep-dives) |
| `docs/adr/` | Architecture decision records |


## Development Workflow

Before designing: `superpowers:brainstorming`
Before implementing: `superpowers:test-driven-development`
For all Java work: `java-dev` (loads `testing-principles` + `ide-tooling`)
Before committing: `superpowers:requesting-code-review`
After implementation: `implementation-doc-sync` (scoped doc sweep)

**Prompt snippet:** `docs/prompt-snippets.md` — paste the work-item snippet at the start of each issue to enforce the above chain explicitly.

Living docs — check for drift after significant changes:
- `docs/PLATFORM.md`
- `docs/APPLICATIONS.md`
- `docs/repos/`

## Work Tracking

**Issue tracking:** enabled
**GitHub repo:** casehubio/parent
**Changelog:** GitHub Releases
