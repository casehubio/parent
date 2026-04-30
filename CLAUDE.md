# CLAUDE.md — casehub-parent

## Platform Architecture Documents

This repo hosts the canonical platform architecture documentation for the entire casehubio ecosystem.

**When updating platform docs (any `docs/PLATFORM.md` or `docs/repos/*.md` change):**
- Ensure the Capability Ownership table is accurate and complete
- Ensure boundary rules reflect current architectural decisions
- Ensure per-repo deep-dives match what is actually in those repos
- Commit and push so raw GitHub URLs resolve correctly for other repos

**Platform document locations:**
- Master: `docs/PLATFORM.md` ([raw](https://raw.githubusercontent.com/casehubio/casehub-parent/main/docs/PLATFORM.md))
- Per-repo deep-dives: `docs/repos/` ([directory](https://github.com/casehubio/casehub-parent/tree/main/docs/repos))

---

## Project Type

type: custom

## Purpose

`casehub-parent` is the org-level parent POM and BOM for all casehubio ecosystem projects. It:
- Declares dependency versions for shared artifacts (`casehub-ledger`, `casehub-work`, etc.)
- Provides the `aggregator.xml` for full-stack local builds
- Hosts ecosystem-wide CI dashboards and the full-stack build workflow

## Ecosystem Conventions

All casehubio projects align on these conventions:

**Quarkus version:** All projects use `3.32.2`. Property `quarkus.platform.version` in `pom.xml`. When bumping, bump all projects together.

**GitHub Packages — dependency resolution:** Each project's `pom.xml` has `<repositories>` with `id=github` pointing to `https://maven.pkg.github.com/casehubio/*`. CI uses `server-id: github` + `GITHUB_TOKEN` in `actions/setup-java`.

**Cross-project SNAPSHOT versions:** `casehub-ledger` and `casehub-work` are `0.2-SNAPSHOT` from GitHub Packages. The `casehub.version` property in this BOM manages all casehubio artifact versions.

**Publishing:** Each project publishes to `https://maven.pkg.github.com/casehubio/<repo>` via `mvn deploy` on push to `main`. Root aggregator POMs skip deployment (`maven.deploy.skip=true`); only deployable JAR modules override to `false`.

## Full-Stack Build

```bash
# Clone all repos alongside casehub-parent, then:
mvn install -f aggregator.xml          # build all in dependency order
mvn install -f aggregator.xml -DskipTests  # skip tests
./build-all.sh                         # incremental — only rebuilds changed modules
./build-all.sh --no-cache              # force full rebuild
```

Requires all repos cloned in the same parent directory as `casehub-parent`.

## CI Dashboards

Three GitHub Actions workflows:
- **`dashboard.yml`** — build status across all ecosystem repos (runs every 15 min, checks latest push-to-main run per repo)
- **`pr-dashboard.yml`** — open PRs and their CI status across all ecosystem repos (runs every 15 min)
- **`full-stack-build.yml`** — builds all repos in dependency order (manual trigger via `workflow_dispatch`)

Trigger manually: GitHub Actions → select workflow → "Run workflow".

## Repo List

| Repo | GitHub | Purpose |
|------|--------|---------|
| `quarkus-langchain4j` | casehubio/quarkus-langchain4j | Casehubio fork with unreleased fixes (999-SNAPSHOT) — temporary, not in BOM |
| `ledger` | casehubio/ledger | Immutable audit ledger + trust scoring (local dir: `casehub/ledger`) |
| `casehub-work` | casehubio/work | Human task lifecycle (WorkItem inbox, SLA, routing) |
| `quarkus-qhorus` | casehubio/quarkus-qhorus | Agent communication mesh |
| `engine` | casehubio/engine | Hybrid choreography+orchestration engine (local dir: `casehub-engine`) |
| `claudony` | casehubio/claudony | Remote Claude CLI sessions + ecosystem dashboard |
| `casehub-connectors` | casehubio/casehub-connectors | Outbound message connectors (Slack, Teams, SMS, email) |
| `casehub-assisteddev` | casehubio/casehub-assisteddev | AI-assisted development application (placeholder name) — first app layer built on CaseHub foundation |
| `casehub` | casehubio/casehub | **Retiring** — original POC, no new features |
