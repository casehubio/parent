# CaseHub Parent

## Project Type

type: java

## Repository Role

Root parent POM for the CaseHub ecosystem. Owns shared build configuration, CI/CD workflows, cross-module conventions, and the full-stack build orchestration.

**Peer repos (each has its own Claude session — do not commit to these):**
ledger, connectors, work, qhorus, engine, claudony, quarkus-langchain4j

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
| `full-stack-build.yml` | manual only | Sequential build of all repos in dependency order |
| `clear-snapshot-packages.yml` | manual only | Delete SNAPSHOT artifacts from GitHub Packages |

**Key rule:** Cross-repo `repository_dispatch` requires `GH_TOKEN: ${{ secrets.GH_PAT }}` (classic PAT). `GITHUB_TOKEN` is repo-scoped only and returns 403 on cross-repo calls.

**langchain4j** is excluded from standard builds by default. Tick `include_langchain4j` only when that fork has changed.

## Cross-Repo Conventions

Conventions shared across all modules live in `docs/conventions/`. Each file is self-contained. See `docs/conventions/INDEX.md` for the full list.

**Critical:** Never commit or push to peer repo directories (`../ledger`, `../work`, etc.). Each repo has its own Claude session. For cross-repo fixes, create a GitHub issue on the target repo instead.

## Testing

Surefire is configured in this parent POM with `rerunFailingTestsCount=2` — failing tests are retried twice before being marked as failures, surfacing flaky vs consistently broken.

## Writing Style Guide

**The writing style guide at `~/claude-workspace/writing-styles/blog-technical.md` is mandatory for all blog and diary entries.** Load it in full before drafting. Complete the pre-draft voice classification (I / we / Claude-named) before generating any prose. Do not show a draft without verifying it against the style guide.

## Work Tracking

**Issue tracking:** enabled
**GitHub repo:** casehubio/parent
**Changelog:** GitHub Releases
