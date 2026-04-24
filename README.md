# casehub-parent

Org-level parent POM and BOM for the [casehubio](https://github.com/casehubio) ecosystem, plus tooling for full-stack local builds and CI/CD.

## Build status

| Repository | Status |
|:-----------|:------:|
| [casehub-parent](https://github.com/casehubio/casehub-parent) | [![casehub-parent](https://github.com/casehubio/casehub-parent/actions/workflows/publish.yml/badge.svg?branch=main)](https://github.com/casehubio/casehub-parent/actions/workflows/publish.yml) |
| [quarkus-ledger](https://github.com/casehubio/quarkus-ledger) | [![quarkus-ledger](https://github.com/casehubio/quarkus-ledger/actions/workflows/publish.yml/badge.svg?branch=main)](https://github.com/casehubio/quarkus-ledger/actions/workflows/publish.yml) |
| [quarkus-work](https://github.com/casehubio/quarkus-work) | [![quarkus-work](https://github.com/casehubio/quarkus-work/actions/workflows/publish.yml/badge.svg?branch=main)](https://github.com/casehubio/quarkus-work/actions/workflows/publish.yml) |
| [quarkus-qhorus](https://github.com/casehubio/quarkus-qhorus) | [![quarkus-qhorus](https://github.com/casehubio/quarkus-qhorus/actions/workflows/publish.yml/badge.svg?branch=main)](https://github.com/casehubio/quarkus-qhorus/actions/workflows/publish.yml) |
| [casehub-engine](https://github.com/casehubio/casehub-engine) | [![casehub-engine](https://github.com/casehubio/casehub-engine/actions/workflows/publish.yml/badge.svg?branch=main)](https://github.com/casehubio/casehub-engine/actions/workflows/publish.yml) |
| [claudony](https://github.com/casehubio/claudony) | [![claudony](https://github.com/casehubio/claudony/actions/workflows/publish.yml/badge.svg?branch=main)](https://github.com/casehubio/claudony/actions/workflows/publish.yml) |
| [quarkus-langchain4j](https://github.com/casehubio/quarkus-langchain4j) | [![quarkus-langchain4j](https://github.com/casehubio/quarkus-langchain4j/actions/workflows/publish.yml/badge.svg?branch=main)](https://github.com/casehubio/quarkus-langchain4j/actions/workflows/publish.yml) |

> Full detail (timestamps, SHAs, all org repos): [Build Status Dashboard workflow](https://github.com/casehubio/casehub-parent/actions/workflows/dashboard.yml)

---

## Contents

- [The BOM](#the-bom)
- [Ecosystem projects](#ecosystem-projects)
- [Local full-stack build](#local-full-stack-build)
  - [Incremental build logic](#incremental-build-logic)
  - [Replaying a build](#replaying-a-build)
- [CI/CD pipeline](#cicd-pipeline)
- [The quarkus-langchain4j fork](#the-quarkus-langchain4j-fork)
- [Adding a new project](#adding-a-new-project)
- [Local developer setup](#local-developer-setup)

---

## The BOM

`casehub-parent` is the Maven Bill of Materials for all casehubio projects. Every project in the ecosystem imports it so that cross-project dependency versions are managed in one place.

### What the BOM provides

| Artifact | GroupId | What it is |
|---|---|---|
| `quarkus-ledger` | `io.quarkiverse.ledger` | Immutable audit ledger base |
| `quarkus-ledger-deployment` | `io.quarkiverse.ledger` | Extension deployment module |
| `quarkus-work-api` | `io.quarkiverse.work` | Work item SPI |
| `quarkus-work-core` | `io.quarkiverse.work` | Work item core |
| `quarkus-work` | `io.quarkiverse.work` | Work item runtime |
| `quarkus-work-deployment` | `io.quarkiverse.work` | Work item deployment |
| `quarkus-work-ledger` | `io.quarkiverse.work` | Optional ledger integration for work items |
| `quarkus-qhorus` | `io.quarkiverse.qhorus` | AI agent communication mesh |
| `quarkus-qhorus-deployment` | `io.quarkiverse.qhorus` | Qhorus deployment module |
| `quarkus-qhorus-testing` | `io.quarkiverse.qhorus` | Test utilities for Qhorus consumers |
| `casehub-ledger` | `io.casehub` | CaseHub audit ledger integration |

All are managed at the same version (`${casehub.version}`, currently `0.2-SNAPSHOT`).

The BOM also imports `io.quarkus.platform:quarkus-bom` to manage Quarkus extension versions.

### Using the BOM

Add to your project's `<dependencyManagement>` section:

```xml
<dependencyManagement>
  <dependencies>
    <dependency>
      <groupId>io.casehubio</groupId>
      <artifactId>casehub-parent</artifactId>
      <version>0.2-SNAPSHOT</version>
      <type>pom</type>
      <scope>import</scope>
    </dependency>
  </dependencies>
</dependencyManagement>
```

Then declare casehubio dependencies without versions:

```xml
<dependency>
  <groupId>io.quarkiverse.ledger</groupId>
  <artifactId>quarkus-ledger</artifactId>
</dependency>
<dependency>
  <groupId>io.quarkiverse.qhorus</groupId>
  <artifactId>quarkus-qhorus</artifactId>
</dependency>
```

### Why a separate BOM rather than inheritance

Each project in the ecosystem has a different Maven parent (`quarkiverse-parent` for extensions, internal root POMs for multi-module projects). Maven only allows one parent per project, so a shared parent would break existing inheritance chains. Importing the BOM via `<scope>import</scope>` achieves centralised version management without requiring a shared parent.

---

## Ecosystem projects

| Repo | GroupId | Remote |
|---|---|---|
| `quarkus-ledger` | `io.quarkiverse.ledger` | `casehubio/quarkus-ledger` |
| `quarkus-work` | `io.quarkiverse.work` | `casehubio/quarkus-work` |
| `quarkus-qhorus` | `io.quarkiverse.qhorus` | `casehubio/quarkus-qhorus` |
| `casehub-engine` | `io.casehub` | `casehubio/casehub-engine` |
| `claudony` | `dev.claudony` | `casehubio/claudony` |
| `quarkus-langchain4j` | (upstream fork) | `casehubio/quarkus-langchain4j` |

Dependency order (each project may depend on those above it):

```
quarkus-ledger
    ↑
quarkus-work
    ↑
quarkus-qhorus    casehub-engine
    ↑                   ↑
         claudony
```

---

## Local full-stack build

For day-to-day development, use `build-all.sh`. It clones or updates all ecosystem repos, records the SHA of each, pins each to that SHA, and runs an incremental Maven build.

### Quick start

```bash
git clone https://github.com/casehubio/casehub-parent.git
cd casehub-parent
./build-all.sh
```

All repos are cloned into subdirectories of `casehub-parent/`. These directories are gitignored — they are not tracked by this repository.

### Build options

```bash
./build-all.sh                  # incremental build (default)
./build-all.sh --no-cache       # ignore cache, rebuild everything
./build-all.sh --skip-tests     # skip test-only phase for TEST-state modules
./build-all.sh -DskipTests      # pass-through to Maven: skip all tests
./build-all.sh -T 1C            # parallel Maven build
```

All unrecognised flags are passed through to Maven.

### Incremental build logic

Each module is classified into one of three states before building. The state is determined by comparing the current HEAD SHA of each repo against the SHA recorded in the most recent successful build log (the cache manifest).

| State | Condition | Action |
|---|---|---|
| **BUILD** | Own SHA changed since last build | Full compile + test + `mvn install` |
| **TEST** | Own SHA unchanged, but a transitive casehub dependency is in BUILD state | `mvn test` only — tests run against the newly installed dep artifacts, no recompile |
| **SKIP** | Own SHA and all transitive casehub dep SHAs unchanged | Nothing — artifact already in local `.m2` is current |

The rationale for the TEST state: if `quarkus-ledger` changes but `quarkus-work`'s own code does not, `quarkus-work` doesn't need recompiling — its bytecode is the same. But its tests should run against the new `quarkus-ledger` to catch integration regressions.

The dependency graph used for propagation:

```
quarkus-ledger      → (no casehub deps)
quarkus-work        → quarkus-ledger
quarkus-qhorus      → quarkus-ledger, quarkus-work
casehub-engine      → quarkus-ledger, quarkus-work
claudony            → quarkus-ledger, quarkus-work, quarkus-qhorus
```

Example output:

```
==> Incremental analysis...
    quarkus-ledger       BUILD   (own SHA changed)
    quarkus-work         TEST    (dep changed, rerun tests against new artifacts)
    quarkus-qhorus       TEST    (dep changed, rerun tests against new artifacts)
    casehub-engine       TEST    (dep changed, rerun tests against new artifacts)
    claudony             SKIP    (SHA and all deps unchanged)

==> Installing: quarkus-ledger
==> Retesting against updated deps: quarkus-work,quarkus-qhorus,casehub-engine
```

### SHA logs and the build cache

Every `build-all.sh` run writes a timestamped SHA log to `build-logs/`:

```
build-logs/
  20260424T143022.shas   ← each run writes one file
  20260424T091511.shas
  20260423T220034.shas
```

Each log records the exact HEAD SHA of every repo at build time:

```
# casehubio full-stack build
# timestamp: 20260424T143022
# branch:    main

quarkus-ledger=a2636e132b43bc0faad66cf587ab5b30996ff3df
quarkus-work=e085d64c1f2a93b7d0f4e89a3c12d45e678f901a
quarkus-qhorus=ef89aaa3b7c1d20f4e5a67b89c0d12e3f456789a
casehub-engine=fccb647d8e2f31a05b6c78d90e1f23a4b5678901
claudony=3fbeac7e9f0a12b34c56d78e90f1a2b3c4567890
```

The most recent log is used as the cache manifest for the next build. Build logs are committed to this repository as a permanent record of what built together successfully.

### Replaying a build

To reproduce an exact prior build:

```bash
./replay.sh build-logs/20260424T143022.shas
./replay.sh build-logs/20260424T143022.shas -DskipTests
```

`replay.sh` clones or updates each repo, checks out the exact SHA from the log, and runs the full Maven build via `aggregator.xml`. The result is byte-for-byte identical to the original build.

### The Maven aggregator

`aggregator.xml` lists all ecosystem repos as Maven reactor modules. Maven reads each project's own `pom.xml` and resolves the build order from actual `<dependency>` declarations — the order in the aggregator file is advisory only.

```bash
# Run directly if repos are already cloned and pinned
mvn install -f aggregator.xml
mvn install -f aggregator.xml -pl quarkus-ledger,quarkus-work   # partial build
```

The aggregator is not published to Maven. It is a local build tool only.

---

## CI/CD pipeline

Each project in the ecosystem has its own GitHub Actions workflow (`.github/workflows/publish.yml`) that builds and publishes to GitHub Packages on every push to `main`. Projects are built and published independently — there is no cross-repo trigger chain.

### Per-project publish workflow

Every ecosystem repo contains:

```yaml
- name: Set up Java 21
  uses: actions/setup-java@v4
  with:
    java-version: '21'
    distribution: 'temurin'
    server-id: github
    server-username: GITHUB_ACTOR
    server-password: GITHUB_TOKEN

- name: Build and publish
  run: mvn --batch-mode deploy
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

`mvn deploy` publishes artifacts to `https://maven.pkg.github.com/casehubio/<repo>`. Consumers resolve them via the `github-casehubio` repository entry in their root pom:

```xml
<repositories>
  <repository>
    <id>github-casehubio</id>
    <url>https://maven.pkg.github.com/casehubio/*</url>
    <snapshots><enabled>true</enabled></snapshots>
  </repository>
</repositories>
```

### casehub-parent publish

`casehub-parent` publishes its BOM on every push to `main`. This must be published before any other project can resolve `io.casehubio:casehub-parent:0.2-SNAPSHOT` in CI.

### Build order in CI

Because each project publishes independently, upstream artifacts must be available in GitHub Packages before downstream CI can run. The natural order is:

1. `casehub-parent` → publishes BOM
2. `quarkus-ledger` → depends on BOM
3. `quarkus-work` → depends on BOM + `quarkus-ledger`
4. `quarkus-qhorus` → depends on BOM + `quarkus-ledger` + `quarkus-work`
5. `casehub-engine` → depends on BOM + `quarkus-ledger` + `quarkus-work`
6. `claudony` → depends on BOM + `quarkus-qhorus`

If `quarkus-ledger` CI hasn't published yet when `quarkus-work` CI runs, `quarkus-work` will fail with `Could not resolve io.quarkiverse.ledger:quarkus-ledger:0.2-SNAPSHOT`. Re-running the failing job after the upstream publish completes resolves this.

### `quarkus-langchain4j`

`casehubio/quarkus-langchain4j` is a fork of the upstream Quarkus LangChain4j project maintained here until upstream fixes are merged and published. It is **not** configured with casehubio CI/CD and does not use the casehub-parent BOM. It is included in the ecosystem only as a build dependency; consuming projects reference it at whatever version casehub-engine declares.

---

## The quarkus-langchain4j fork

The casehubio ecosystem depends on [quarkus-langchain4j](https://github.com/quarkiverse/quarkus-langchain4j) for AI agent capabilities. However, fixes required by the ecosystem are not yet merged into an upstream release. Until those PRs land and a new release is published, the ecosystem uses a casehubio-maintained fork.

### Why the fork exists

`casehub-engine` depends on specific `quarkus-langchain4j` behaviour that contains fixes not present in the latest public release. Depending directly on the public release would produce runtime failures in casehub-engine.

### How it works

The fork lives at `casehubio/quarkus-langchain4j`. It contains:
- All upstream code from `quarkiverse/quarkus-langchain4j` at a chosen base commit
- The specific fix commits cherry-picked on top

The fork publishes its artifacts to casehubio GitHub Packages as version `999-SNAPSHOT` (the fork's own working version) via `.github/workflows/casehub-publish.yml`. This workflow is **casehubio-specific and must not be included in upstream PRs**.

### What consumers reference

Consumers declare `999-SNAPSHOT` for langchain4j artifacts rather than the public release version:

```xml
<!-- In casehub-engine pom.xml -->
<version.io.quarkiverse.langchain4j>999-SNAPSHOT</version.io.quarkiverse.langchain4j>
```

The `github-casehubio` repository is already configured in all casehubio project poms, so `999-SNAPSHOT` resolves from GitHub Packages without any additional setup.

### Why `999-SNAPSHOT` keeps the pom clean

The fork's `pom.xml` in git already declares `999-SNAPSHOT` — no version changes are committed to the fork. The `casehub-publish.yml` workflow simply runs `mvn deploy` against the existing pom. This means any fix commits cherry-picked back to the upstream repo contain no casehubio-specific changes — only the functional fix.

### Pushing fixes upstream

When a fix is ready to contribute upstream:
1. Create a branch from the base commit (before the casehub cherry-picks)
2. Cherry-pick only the functional fix commits — **not** `casehub-publish.yml`
3. Open a PR against `quarkiverse/quarkus-langchain4j`

The `.github/workflows/casehub-publish.yml` file is the only casehubio-specific file in the fork. It is not part of any fix commit.

### Removing the fork

When the required fixes are merged upstream and a new release is published:
1. Update `version.io.quarkiverse.langchain4j` in `casehub-engine` to the new upstream release version
2. Remove the fork from `build-all.sh` REPOS list
3. Remove the wildcard GitHub Packages URL still resolves other artifacts — no other config changes needed
4. Archive `casehubio/quarkus-langchain4j`

---

## Adding a new project

1. Create the repo under `casehubio/`
2. Add the casehub-parent BOM import to its `<dependencyManagement>` section
3. Add the `github-casehubio` repository entry to its root pom
4. Add `<distributionManagement>` pointing to `https://maven.pkg.github.com/casehubio/<repo>`
5. Create `.github/workflows/publish.yml` (copy from any existing ecosystem repo)
6. Add the repo and its casehub dependencies to the `DEPS` map in `build-all.sh`
7. Add the repo to the `REPOS` array in `build-all.sh` in dependency order
8. Add the repo as a `<module>` in `aggregator.xml`
9. Add the repo's publishable artifacts to `pom.xml` (the BOM) in this repo
10. Add the cloned directory name to `.gitignore`

---

## Local developer setup

Consuming projects pull artifacts from GitHub Packages, which requires authentication even for public repos.

Add to `~/.m2/settings.xml`:

```xml
<settings>
  <servers>
    <server>
      <id>github-casehubio</id>
      <username>YOUR_GITHUB_USERNAME</username>
      <password>YOUR_GITHUB_PAT</password>
    </server>
    <server>
      <id>github</id>
      <username>YOUR_GITHUB_USERNAME</username>
      <password>YOUR_GITHUB_PAT</password>
    </server>
  </servers>
</settings>
```

The PAT needs `read:packages` scope for consuming artifacts and `write:packages` scope for publishing.

In CI, `GITHUB_TOKEN` is used automatically — no PAT setup required.

For local development where you are actively changing multiple projects simultaneously, use `build-all.sh` rather than relying on GitHub Packages — it builds everything from source and installs to your local `.m2`.
