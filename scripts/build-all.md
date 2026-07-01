# Build All — Architecture and Operations

The build-all system provides a single-command way to clone, build, and
validate the entire CaseHub ecosystem in dependency order. It runs both
locally and in CI, driven from a single source of truth.

---

## Single Source of Truth

```
build/modules-core.csv
build/modules-applications.csv
```

Each line is: `name,dep1,dep2,...`

- **First field** — module name (also the local clone directory under `casehub/`)
- **Remaining fields** — modules this one depends on for the incremental decision
- **Line order** — the build order. Earlier lines are built first.
- **No field** = no deps (e.g. `pages` builds standalone)

### Core modules (always built)

```
platform,parent
ledger,parent
eidos,ledger
neocortex,platform
connectors,parent
work,parent,ledger,connectors
qhorus,parent,ledger,work
pages
engine,parent,ledger,work
claudony,parent,ledger,work,qhorus
```

### Application modules (opt-in via `include_applications`)

```
openclaw,parent,platform,ledger,qhorus,engine
devtown,parent,ledger,work,qhorus,engine
aml,parent,ledger,work,qhorus,engine
clinical,parent,ledger,work,qhorus,engine
life,parent,ledger,work,qhorus,engine,openclaw
drafthouse,parent,qhorus
quarkmind,parent,ledger,work,qhorus,engine   # mdproctor/ org, needs GH_PAT
flow,parent,engine                           # mdproctor/ org, needs GH_PAT
```

**To add a module:** add a line to the appropriate CSV, commit. The pre-commit
hook regenerates `build-all.yml` automatically and stages it with your commit.

---

## Files

```
scripts/
  build-all.md              ← this file
  build-all-decision.sh     ← BUILD/TEST/SKIP decision function
  build-all-decision.bats   ← bats test suite (49 tests)
  generate-workflows.py     ← generates build step blocks in build-all.yml
  install-hooks.sh          ← installs the pre-commit hook

build/
  modules-core.csv          ← core module list + deps (single source of truth)
  modules-applications.csv  ← application module list + deps

.github/workflows/
  build-all.yml             ← CI workflow (partially generated from CSVs)
```

---

## Decision Logic — `build-all-decision.sh`

Called once per module during a build. Compares current-run SHAs against the
last successful run to decide how much work to do:

| Condition | Decision | Action |
|-----------|----------|--------|
| No previous state (first run) | `BUILD` | compile + test + `mvn install` |
| Module's own SHA changed | `BUILD` | compile + test + `mvn install` |
| A dependency's SHA changed, module unchanged | `TEST` | `mvn test` only (artifact in `.m2` is still current) |
| All SHAs match | `SKIP` | nothing |

```
build-all-decision.sh \
  --module engine \
  --current-sha <sha> \
  --previous-sha <sha|"none"> \
  --dep parent:<cur>:<prev> \
  --dep ledger:<cur>:<prev> \
  --dep work:<cur>:<prev>
```

Output to stdout: `BUILD`, `TEST`, or `SKIP`. Exit code always 0.

Tests: `bats scripts/tests/build-all-decision.bats`

---

## CI Workflow — `build-all.yml`

Triggered manually from GitHub Actions. Inputs:

| Input | Default | Description |
|-------|---------|-------------|
| `skip_tests` | false | Skip all tests (compile + install only) |
| `skip_integration_tests` | false | Skip ITs only, unit tests still run |
| `maven_args` | — | Extra Maven args passed to every step (e.g. `-T 1C`) |
| `include_applications` | false | Also build application modules |
| `force_rebuild` | false | Ignore cached state, rebuild everything |

`force_rebuild: true` is equivalent to the deleted `full-stack-build.yml` —
it bypasses all incremental decisions and runs `BUILD` on every module.

### Workflow steps

1. **Clone repositories** — reads CSVs, clones each repo in order
2. **Collect SHAs** — records HEAD SHA for every cloned repo, writes to
   `$GITHUB_OUTPUT` (for build step env vars) and `.build-shas/<name>` files
   (for Save build state)
3. **Restore build state** — loads `.incremental-state/shas.txt` from the
   Actions cache (keyed by branch + run ID)
4. **Load previous SHAs** — reads state file into `$GITHUB_OUTPUT` and
   `.build-shas-prev/<name>` files
5. **Restore Maven cache** — restores `.m2/repository/io/casehub` from cache
6. **Install parent POM** — always runs; ensures the current POM version is in `.m2`
7. **Build: \<module\>** ×N — one step per module (generated). Each step:
   - calls `build-all-decision.sh` with current + previous SHAs for itself and deps
   - writes decision to `.build-decisions/<name>`
   - runs `BUILD`, `TEST`, or `SKIP` accordingly
   - writes `success` or `failure` to `.build-outcomes/<name>`
8. **Save build state** — loops over CSVs, reads `.build-shas/`, `.build-shas-prev/`,
   and `.build-outcomes/` to decide which SHAs to persist for the next run
9. **Persist build state** — saves `.incremental-state/` to the Actions cache
10. **Build summary** — loops over CSVs, reads `.build-outcomes/` and
    `.build-decisions/` to render the GitHub step summary table
11. **Sync casehub-all** — on success, dispatches current SHAs to casehub-all

### File-based outcome tracking

Build steps write their results to files rather than relying on
`${{ steps.X.outcome }}` env var chains. This means the summary, state-save,
and casehub-all dispatch steps can all loop over the CSV without needing a
hardcoded list of module names in their `env:` sections.

```
.build-shas/<name>       ← current SHA (written by Collect SHAs)
.build-shas-prev/<name>  ← previous SHA (written by Load previous SHAs)
.build-outcomes/<name>   ← "success" or "failure" (written by each build step)
.build-decisions/<name>  ← "BUILD", "TEST", or "SKIP" (written by each build step)
.build-times/<name>      ← elapsed seconds (written by each build step)
```

---

## casehub-all Integration

On a successful build, the workflow dispatches an `ecosystem-build-succeeded`
event to `casehubio/casehub-all` containing the HEAD SHA of every built module.
casehub-all's `update-pointers.yml` receives this and updates its submodule
pointers to those SHAs.

This means casehub-all always points to the last known-good set of SHAs across
the entire ecosystem — a reproducible snapshot of a passing build.

The build runs on a 4-hour cron schedule in addition to manual dispatch.

---

## Generated Sections — `generate-workflows.py`

The build step blocks in `build-all.yml` (between the `BEGIN GENERATED` /
`END GENERATED` markers) are generated from the CSVs. Do not edit them by hand.

To regenerate manually:

```bash
python3 scripts/generate-workflows.py
```

The generator reads both CSVs and rewrites the marked section in `build-all.yml`.
If nothing changed it reports `unchanged` and exits cleanly.

---

## Pre-commit Hook — `install-hooks.sh`

Installs a git pre-commit hook that detects changes to either CSV and
automatically regenerates `build-all.yml`, then stages the updated file as
part of the same commit.

Install once after cloning:

```bash
bash scripts/install-hooks.sh
```

Workflow when you add a module:

```
1. Edit build/modules-core.csv or build/modules-applications.csv
2. git add build/modules-*.csv
3. git commit -m "..."
   → hook fires
   → generate-workflows.py runs
   → build-all.yml is updated and staged
   → commit includes both the CSV change and the regenerated YAML
```

---

## Secrets Required

| Secret | Used for |
|--------|----------|
| `GITHUB_TOKEN` | Cloning casehubio/* repos, reading GitHub Packages |
| `GH_PAT` | Cloning mdproctor/quarkmind and mdproctor/flow (private); dispatching to casehub-all |
