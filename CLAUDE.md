# CLAUDE.md — casehub-parent

## Project Type

type: custom

## Purpose

`casehub-parent` is the org-level parent POM and BOM for all casehubio ecosystem projects. It:
- Declares dependency versions for shared artifacts (`quarkus-ledger`, `quarkus-work`, etc.)
- Provides the `aggregator.xml` for full-stack local builds
- Hosts ecosystem-wide CI dashboards and the full-stack build workflow

## Ecosystem Conventions

All casehubio projects align on these conventions:

**Quarkus version:** All projects use `3.32.2`. Property `quarkus.platform.version` in `pom.xml`. When bumping, bump all projects together.

**GitHub Packages — dependency resolution:** Each project's `pom.xml` has `<repositories>` with `id=github` pointing to `https://maven.pkg.github.com/casehubio/*`. CI uses `server-id: github` + `GITHUB_TOKEN` in `actions/setup-java`.

**Cross-project SNAPSHOT versions:** `quarkus-ledger` and `quarkus-work` are `0.2-SNAPSHOT` from GitHub Packages. The `casehub.version` property in this BOM manages all casehubio artifact versions.

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

| Repo | Purpose |
|------|---------|
| `quarkus-langchain4j` | Casehubio fork with unreleased fixes (999-SNAPSHOT) |
| `quarkus-ledger` | Immutable audit ledger extension |
| `quarkus-work` | Work routing and WorkBroker SPI |
| `quarkus-qhorus` | Agent communication mesh |
| `engine` | Hybrid choreography+orchestration engine (GitHub repo name is `casehubio/engine`; rename to `casehub-engine` pending) |
| `claudony` | Session management and Claudony dashboard |
