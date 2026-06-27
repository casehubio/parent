# Adding a New Repo to the CaseHub Ecosystem — Complete Checklist

Every step verified from practice. Missing any item produces a silent gap — a repo that builds
locally but isn't triggered by upstreams, doesn't appear in dashboards, or confuses the next
Claude session that opens it.

Work through the list top-to-bottom. Items within a section can often be parallelised.

---

## 0. Decide Before You Start

- [ ] **Tier** — Foundation / Integration / Application? Determines dependency direction.
- [ ] **Module structure** — Foundation: SPI module + runtime + deployment + optional adapters.
  Integration: core / casehub / app (+ python/ if needed). Application: api / app (hexagonal).
- [ ] **GitHub repo name** — short, lowercase, matches artifact-id root (`casehub-openclaw` →
  `casehubio/openclaw`).
- [ ] **Dependency graph** — which existing repos does this one depend on? This drives steps 3–5.
- [ ] **Downstream dependents** — which existing repos will depend on this one once it ships?
  This drives the dispatch chain (step 5).

---

## Conventions

These variables are used throughout the checklist. Set them once for your environment before starting.

| Variable | Meaning | Example |
|----------|---------|---------|
| `$GITHUB_USER` | Your personal GitHub username | `mdproctor` |
| `$CASEHUB_LOCAL` | Local root for project repos | `~/claude/casehub` |
| `$CASEHUB_WORKSPACE` | Local root for workspace repos | `~/claude/public/casehub` |

Workspace repos are named `wsp-casehub-<name>`, private, under `$GITHUB_USER`.

---

## 1. GitHub Repository

- [ ] `gh repo create casehubio/<name> --public --description "..."`
- [ ] Set default branch to `main` if not already.
- [ ] Configure merge strategy — rebase merge only, squash disabled:
  ```bash
  gh repo edit casehubio/<name> --enable-rebase-merge --no-squash-merge
  ```
- [ ] Clone locally: `git clone https://github.com/casehubio/<name>.git ../casehub/<name>`
- [ ] Set git user config in the new repo to match your identity.
- [ ] Fork to $GITHUB_USER personal account: `gh repo fork casehubio/<name> --clone=false`
- [ ] Rewire remotes — all repos follow `origin = $GITHUB_USER fork, upstream = casehubio org`:
  ```bash
  git -C ../casehub/<name> remote rename origin upstream
  git -C ../casehub/<name> remote add origin https://github.com/$GITHUB_USER/<name>.git
  ```
  Verify: `git remote -v` should show both `origin` ($GITHUB_USER) and `upstream` (casehubio).

---

## 2. Maven Project Skeleton (no code)

All pom.xml files must be populated and valid — IntelliJ must be able to open the project.

- [ ] Root `pom.xml`:
  - `<parent>` → `casehub-parent` 0.2-SNAPSHOT
  - `<artifactId>` → `casehub-<name>-parent`
  - `<modules>` listing all child modules
  - `<dependencyManagement>` — import `quarkus-bom`; pin all cross-module and foundation deps
  - `<repositories>` → `https://maven.pkg.github.com/casehubio/*`
  - `<distributionManagement>` → `https://maven.pkg.github.com/casehubio/<name>`
  - `<scm>` → GitHub URL

- [ ] Module pom.xml files (one per module):
  - `api/` — pure Java, zero framework, zero JPA. No `<build>` plugins needed beyond compiler.
    Add Jandex plugin if CDI beans live here.
  - `app/` or `runtime/` — Quarkus app with `<goal>build</goal>`. Full deps including:
    - `casehub-platform` at `<scope>runtime</scope>` (NOT test — PP-20260524-a8f597).
      AML follows this; clinical and devtown use compile default and currently work. The
      `runtime` scope is required when Quarkus augmentation validates CDI without the test
      classpath — if you see `UnsatisfiedResolutionException` for `PreferenceProvider` during
      augmentation, this is the fix. Set `<scope>runtime</scope>` proactively.
    - `casehub-platform-expression` if casehub-engine is a dep
    - All test deps (qhorus-testing, engine-testing, platform-testing, assertj, awaitility)
  - Integration tier core/ — Jandex plugin; no Quarkus build goal.
  - Integration tier casehub/ — Jandex plugin.
  - Integration tier app/ — Quarkus build goal.

- [ ] **Flyway version range** (app modules consuming casehub-work):
  - Domain migrations must start at V100+ (casehub-work owns V1–V21+)
  - Add `classpath:db/ledger/migration` to Flyway locations when casehub-ledger is on classpath
    (PP-20260524-10efef)
  - Add `classpath:db/qhorus/migration` when casehub-qhorus is on classpath

- [ ] Stub `src/main/java/.gitkeep`, `src/main/resources/.gitkeep`, `src/test/java/.gitkeep`
  in every module so IntelliJ sees the source roots and Git tracks the empty dirs.

- [ ] Stub `src/main/resources/application.properties` in the app module. Minimum content:
  ```properties
  quarkus.datasource.db-kind=h2
  quarkus.datasource.jdbc.url=jdbc:h2:mem:<name>;DB_CLOSE_DELAY=-1;MODE=PostgreSQL
  quarkus.flyway.migrate-at-start=true
  quarkus.flyway.locations=classpath:db/migration
  ```
  When casehub-qhorus is a dependency, add a named `qhorus` datasource alongside the
  default (see clinical `runtime/application.properties` for the full pattern including
  `%dev` profile overrides and per-datasource Flyway locations).
  When casehub-ledger is a dependency, add `classpath:db/ledger/migration` to Flyway
  locations (PP-20260524-10efef).
  For multi-datasource apps, use `quarkus.hibernate-orm.packages` to list all JPA
  packages that the default datasource should scan (aml pattern).

---

## 3. Metadata and Process Files

- [ ] `CLAUDE.md` — two-section file (workspace + project guide). Copy from aml or clinical
  as template. Include:
  - Workspace section: session start path, artifact locations table, structure, git discipline,
    **peer repos hard boundary** (list every other casehubio repo — never commit to these),
    routing table
  - Project section: platform context, project type, what it is, tutorial layers (if app tier),
    reference docs, build commands with `JAVA_HOME=$(/usr/libexec/java_home -v 26) mvn ...`,
    work tracking (issue tracking: enabled, GitHub repo: casehubio/<name>)
  - **Project Artifacts section:** declare which paths are project content (not workspace
    noise). At minimum: `CLAUDE.md` and `docs/`. Skills (git-squash, handover) use this to
    avoid filtering or dropping commits that touch project content. Without it, filter-repo
    may strip project docs from history.
  - **IntelliJ MCP Routing section:** declare which MCP servers are available. Currently
    only `mcp__intellij-index__*` is active (`mcp__intellij__*` is disabled due to memory
    leak). Include: how to auto-open projects via `project_path`, instruction to never ask
    the user to open a project manually.
  - **Work Tracking automatic behaviours:** under the `## Work Tracking` section, add:
    - Before implementation begins — check for an active issue
    - Every issue must be linked to its parent epic
    - Before any commit — confirm issue linkage
    - All commits reference an issue (`Refs #N` or `Closes #N`)
  - **Blog publishing:** CLAUDE.md must state that blog entries go in the workspace `blog/`
    directory and are published to `mdproctor.github.io` via the `publish-blog` skill. Verify
    `~/.claude/blog-routing.yaml` exists and has a routing entry for the project's blog path.
    If missing, create one before the first blog entry is written.
  - **Blog routing in workspace:** create `blog-routing.yaml` in the workspace directory
    (`$CASEHUB_WORKSPACE/<name>/blog-routing.yaml`) with `extends: ~/.claude/blog-routing.yaml`.
    The global config handles destination routing; the workspace file ensures the publish-blog
    skill finds the routing chain. Without it, blog entries are never published.
  - **Application-tier repos:** the project section must include a session-start directive to
    read `AGENTIC-HARNESS-GUIDE.md`:
    ```
    ## Session Start
    Read AGENTIC-HARNESS-GUIDE.md at session start alongside this CLAUDE.md.
    Path: `docs/AGENTIC-HARNESS-GUIDE.md` in `casehub-parent`
    (or via the symlinked workspace: `wksp/../../parent/docs/AGENTIC-HARNESS-GUIDE.md`)
    ```
    This guide covers build order, LAYER-LOG.md structure, the three-document design system,
    anti-patterns, retroactive work procedures, and ongoing maintenance protocols that apply
    to every harness application. Without it, Claude sessions drift into tutorial-first design
    and incorrect CDI displacement patterns within a few turns.

- [ ] **Run issue-workflow** — after CLAUDE.md is written, run the `issue-workflow` skill
  (Phase 0) to wire GitHub issue tracking. This creates the commit hook, enforces issue refs
  on every commit, and sets up the work tracking infrastructure. Do not skip — sessions without
  it drift into uncommitted work and lose traceability.

- [ ] `ARC42STORIES.MD` — create in project root even if no arc42 chapters exist yet.
  Copy the header and taxonomy table from `casehub-clinical` or `casehub-aml` as a template;
  set all chapter statuses to `🔲 pending (TBD)`. The file must exist so the `handover` skill's
  stale-scan step can run without errors and future sessions have a known starting point.

- [ ] `LAYER-LOG.md` — application tier: tutorial layer stubs (one per foundation module
  added, in adoption order). Integration tier: epic log format (one entry per epic).
  Do NOT leave this file empty — write at minimum the header and first entry stub.

- [ ] `README.md` — purpose, module structure, documentation links, current status (scaffold).

- [ ] `.gitignore` — copy from aml: `wksp`, `.DS_Store`, `target/`, `*.class`, `.idea/`

- [ ] `.githooks/pre-push` — copy the squash candidates check from any existing repo.
  Run `chmod +x .githooks/pre-push`.

---

## 4. CI Workflow

- [ ] `.github/workflows/publish.yml`:
  - Triggers: `repository_dispatch` (types: [upstream-published]), `push` (branches: [main]),
    `pull_request` (branches: [main]), `workflow_dispatch`
  - `repository_dispatch` trigger is **required on the publish workflow** — without it the
    repo does not rebuild when upstreams publish new snapshots. This is the most commonly
    missed item. Note: some repos have a separate `build.yml` (CI only) and `publish.yml`
    (publish + dispatch) — the `repository_dispatch` trigger belongs on `publish.yml`, not
    on a test-only build workflow. aml uses only `build.yml` (no publish.yml) and is
    missing this trigger as a result (casehubio/aml#34 filed).
  - Build step: `mvn --batch-mode install` on PR; `mvn --batch-mode deploy -DskipTests` on push
  - Trigger downstream CI step (if anything depends on this repo):
    ```yaml
    - name: Trigger downstream CI
      if: github.event_name != 'pull_request' && success()
      run: |
        for repo in <downstream-repo-1> <downstream-repo-2>; do
          gh api repos/casehubio/$repo/dispatches \
            -f event_type=upstream-published \
            -f client_payload[source]="${GITHUB_REPOSITORY}" \
            2>/dev/null && echo "  ✅ $repo triggered" || echo "  ⚠️  $repo trigger failed"
        done
      env:
        GH_TOKEN: ${{ secrets.GH_PAT }}
    ```
  - Secrets required: `GITHUB_TOKEN` (auto), `GH_PAT` (cross-repo dispatch — classic PAT,
    not fine-grained)

---

## 5. CI Dispatch Chain — Upstream Repos

This is the step most likely to be missed. For each repo that the new repo **depends on**,
check whether that repo's publish workflow already dispatches to the new repo. If not, update it.

**The actual dispatch map (verified against workflow files, 2026-05-25; neural-text added 2026-06-04):**

```
parent       → platform, ledger, connectors
platform     → ledger, connectors, neural-text   ← neural-text added (platform#63 pending)
ledger       → work, qhorus
connectors   → work
work         → engine
qhorus       → engine, claudony
engine       → flow                ← engine#350 must add openclaw here
claudony     → (nothing)
openclaw     → life
neural-text  → (nothing yet — eidos/openclaw/engine will add when wired)
```

Note: engine triggers `flow` (quarkus-flow), not claudony directly — claudony is triggered by
qhorus. Verify the actual workflow file before assuming a dependency implies a dispatch.

For a new **foundation** repo: check if the repos it depends on dispatch to it. File issues
on peer repos if they do not — do not commit to peer repos from this session.

For a new **integration** repo: check which foundation repo is the last in your dependency
chain and verify it dispatches to you. For openclaw: engine (engine#350 pending).

For a new **application** repo: typically triggered by the integration repo it uses as
WorkerProvisioner. Verify openclaw (or claudony) dispatches to it.

**Key constraint:** dispatching requires `GH_PAT` (a classic PAT with `repo` scope and
`workflow` scope). `GITHUB_TOKEN` is repo-scoped only and returns 403 on cross-repo dispatch.

---

## 6. Parent BOM (`pom.xml`)

- [ ] Add `<dependency>` entries for every artifact the new repo publishes, under
  `<!-- casehub-<name> -->` comment block in `<dependencyManagement>`.
- [ ] All new artifacts must pin to `${casehub.version}`.
- [ ] Run `mvn install` in parent to verify the BOM is syntactically valid.

---

## 7. Parent Platform Docs (`docs/PLATFORM.md`)

- [ ] **Repository Map table** — add row: `| casehub-<name> | [casehubio/<name>](...) | one-liner | Tier |`
- [ ] **Build / Dependency Order** — add the new repo in the correct topological position.
- [ ] **Cross-Repo Dependency Map** — add a row for every cross-repo dependency the new repo
  declares (both directions if relevant). Protocol: cross-repo-optional-dep-table-registration.md
- [ ] **Capability Ownership table** — add any new capabilities this repo provides.

---

## 8. Parent Applications Doc (`docs/APPLICATIONS.md`)

- [ ] **Repository Map table** — add row (application tier repos only).
- [ ] **Platform Dependencies** code block — add the new repo and its foundation deps.
- [ ] **Capability Ownership table** — add domain capability row.
- [ ] **Per-Repo Deep Dives table** — add raw URL row.

---

## 9. Build Infrastructure in Parent

The module list and dependency graph live in two CSV files — edit only those; the
build steps in `build-all.yml` are auto-generated by the pre-commit hook.

- [ ] **`build/modules-core.csv`** (foundation/orchestration/integration tier) or
  **`build/modules-applications.csv`** (application tier) — add one line:
  ```
  <name>,dep1,dep2,...
  ```
  First field = module name. Remaining fields = its dependencies (matches the `--dep` flags
  the decision script uses). Array order = build order — insert in the correct topological
  position. The pre-commit hook runs `scripts/generate-workflows.py` automatically and
  stages the updated `build-all.yml` with your commit.

  **Special cases** (handled by the generator — no extra action needed):
  - `pages` → cloned from `casehubio/casehub-pages`, built with yarn
  - `drafthouse` → built from `server/` subdirectory
  - `quarkmind`, `flow` → cloned from `mdproctor/` org using `GH_PAT`

- [ ] **`dashboard.yml`** — add `casehubio/<name>` to the `REPOS` printf list.

- [ ] **`pr-dashboard.yml`** — add `casehubio/<name>` to the `REPOS` printf list.

- [ ] **All modules must be in CI.** Do not add modules to `build/modules-local.csv` —
  every repo should be in the GitHub build and publish architecture via `modules-core.csv`
  or `modules-applications.csv`. Local-only modules are invisible to the ecosystem and
  silently drift out of sync with upstream changes.

---

## 10. Parent README (`README.md`)

- [ ] Add build status badge row under the correct section (Foundation / Integration / Applications).
  Badge URL pattern: `https://github.com/casehubio/<name>/actions/workflows/publish.yml/badge.svg?branch=main`
  Note: check the actual workflow filename in the new repo — it may differ from `publish.yml`
  (engine uses `maven.yml`, claudony uses `ci.yml`).

---

## 11. Parent Dashboard HTML (`docs/index.html`)

- [ ] **Foundation/Integration repos** → add `'<name>'` to the `PLATFORM_REPOS` array.
- [ ] **Application repos** → add `{ org: 'casehubio', name: '<name>' }` to `APP_REPOS`.
  For repos not in the casehubio org (e.g. quarkmind): use `org: 'mdproctor'` or appropriate.

---

## 12. Casehubio Website (`casehubio.github.io`)

- [ ] **SVG architecture diagram** — add the repo name as a `<text>` element in the correct tier
  band (FOUNDATION / RUNTIME / APPLICATIONS). Check x-coordinates don't overlap existing labels.
- [ ] **Foundation tab** or **Applications tab** — add a `<div class="project-card">` block with
  `card-repo`, `card-headline`, `card-desc`, and `card-link`.

---

## 13. Per-Repo Deep Dive in Parent (`docs/repos/<name>.md`)

- [ ] Create `docs/repos/casehub-<name>.md` following the pattern of closest existing
  deep-dive (qhorus.md for integration tier, clinical.md for application tier).
  Sections: Purpose, Key Abstractions, Depends On, Depended On By, Does NOT Do, Current State,
  Design Documents.

---

## 14. Workspace Setup

Each new repo gets its **own isolated workspace git repo** (`wsp-casehub-<name>`). Never commit new workspace directories into the parent workspace — they must have their own git history.

- [ ] Create workspace dir:
      `mkdir -p $CASEHUB_WORKSPACE/<name>/{adr,blog,plans,snapshots,specs}`
- [ ] Create `proj` symlink:
      `ln -s $CASEHUB_LOCAL/<name> $CASEHUB_WORKSPACE/<name>/proj`
- [ ] Create `CLAUDE.md` symlink:
      `ln -s $CASEHUB_LOCAL/<name>/CLAUDE.md $CASEHUB_WORKSPACE/<name>/CLAUDE.md`
- [ ] Create `wksp` symlink in project root:
      `ln -s $CASEHUB_WORKSPACE/<name> $CASEHUB_LOCAL/<name>/wksp`
- [ ] Create `HANDOFF.md` stub in workspace dir.
- [ ] Create `IDEAS.md` stub in workspace dir.
- [ ] Create `INDEX.md` stubs in each artifact subdir (`adr/` `blog/` `plans/` `snapshots/` `specs/`) — git cannot track empty dirs.
- [ ] Create `.gitignore` in workspace dir:
      ```
      proj
      CLAUDE.md
      .DS_Store
      ```
- [ ] `gh repo create $GITHUB_USER/wsp-casehub-<name> --private`
- [ ] `git init $CASEHUB_WORKSPACE/<name>`
- [ ] `git -C $CASEHUB_WORKSPACE/<name> remote add origin https://github.com/$GITHUB_USER/wsp-casehub-<name>.git`
- [ ] `git -C $CASEHUB_WORKSPACE/<name> add .`
- [ ] `git -C $CASEHUB_WORKSPACE/<name> commit -m "init: workspace scaffold for casehub-<name>"`
- [ ] `git -C $CASEHUB_WORKSPACE/<name> push -u origin main`
- [ ] Add `/<name>` to parent workspace `.gitignore` (`$CASEHUB_WORKSPACE/.gitignore`)
- [ ] Commit and push the parent workspace `.gitignore` update.

---

## 15. Spec Docs in the New Repo

- [ ] Create `docs/specs/` directory.
- [ ] Write scoped spec files relevant to the repo:
  - Integration repos: invocation model, mesh fit, key capabilities
  - Application repos: use case spec, actor model, domain design
  - Foundation repos: SPI design, adapter strategy, permission constraints
- [ ] Do NOT duplicate content from the research spec in parent — reference it.

**Spec and ADR promotion:** specs are drafted in the workspace (`$CASEHUB_WORKSPACE/<name>/specs/`).
When a spec is finalized and referenced by implementation, promote it into the project repo
(`docs/specs/`) via the `update-primary-doc` skill. Similarly, ADRs drafted in the workspace
(`$CASEHUB_WORKSPACE/<name>/adr/`) must be promoted to `docs/adr/` in the project repo before
they are referenced from PLATFORM.md or ARC42STORIES.MD. Workspace copies are personal working
drafts — the project repo copy is the authoritative record.

---

## 16. Epic Issues

- [ ] Create Epic 1 (scaffold) — mark as complete if scaffold is done in this session.
- [ ] Create epics for each subsequent milestone/layer (one issue per epic).
- [ ] For application repos: create one epic per tutorial layer (Layer 1 through Layer N).
- [ ] For integration repos: create one epic per major integration milestone.
- [ ] For foundation repos: create epics for SPI, default adapter, and each optional adapter.
- [ ] Link any "blocked by" relationships explicitly in the issue body.

---

## 17. First Commit and Push

- [ ] `git add .` in the new repo — verify status shows only expected files.
- [ ] Commit with message: `chore(#1): scaffold casehub-<name> — Maven structure, docs, CI`
- [ ] `git push origin main`
- [ ] Verify CI workflow appears in GitHub Actions (may take 30s to register).

---

## 18. Parent Commit and Push

- [ ] Stage all parent changes: pom.xml, PLATFORM.md, APPLICATIONS.md, docs/repos/<name>.md,
  README.md, docs/index.html, build/modules-core.csv (or modules-applications.csv),
  build-all.yml (auto-regenerated by pre-commit hook), dashboard.yml, pr-dashboard.yml
- [ ] Commit with message: `chore: register casehub-<name> across parent infrastructure`
- [ ] Push to upstream: `git push upstream main`

---

## 19. Workspace Repo Push

- [ ] `git -C $CASEHUB_WORKSPACE/<name> push`

---

## 20. Post-Bootstrap Verification

- [ ] `mvn validate` in new repo — confirms pom.xml hierarchy is valid.
- [ ] `gh repo view casehubio/<name>` — confirms GitHub repo exists and is accessible.
- [ ] `gh workflow list --repo casehubio/<name>` — confirms publish.yml is registered.
- [ ] Dashboard HTML loads the new repo in the correct section.
- [ ] README badges render (may take one CI run to show green).
- [ ] Parent BOM entry: `mvn dependency:resolve -Dartifact=io.casehub:casehub-<name>-app:0.2-SNAPSHOT` — verifies BOM entry is valid after new repo has published once.
- [ ] **All modules publishing:** after the first CI run, verify every module's artifact
  is available in GitHub Packages. Multi-module repos must list all child modules in
  `<modules>` and each child must have correct `<parent>` reference. A missing module
  silently fails to publish — downstream repos get `Could not resolve` at build time.
  Check: `gh api /orgs/casehubio/packages?package_type=maven | jq '.[].name' | grep <name>`
- [ ] **Blog routing functional:** verify `blog-routing.yaml` exists in the workspace dir
  and extends the global config. Run `ls $CASEHUB_WORKSPACE/<name>/blog-routing.yaml`.

---

## 21. Cascade Chain Verification

Map the new repo into the existing dispatch chain and verify:

- [ ] Every upstream that this repo depends on either already dispatches to it or has a filed
  issue requesting the dispatch to be added (cross-repo constraint — cannot commit from this session).
- [ ] The new repo's publish.yml dispatches to every repo that depends on it.
- [ ] The complete chain from parent → ... → new repo → ... → leaf is unbroken.
- [ ] **CSV files reflect the module:** verify `build/modules-applications.csv` (or
  `modules-core.csv`) contains a line for this repo with correct dependency list.
  Verify `build-all.yml` was regenerated by the pre-commit hook. A missing CSV line
  means the repo is invisible to the full-stack build — it builds in isolation but
  is never triggered by upstream changes in the incremental build.
- [ ] **Dashboard includes the repo:** verify `dashboard.yml` and `pr-dashboard.yml`
  both list `casehubio/<name>` in their REPOS arrays. A missing entry means the repo's
  CI status is invisible in the ecosystem dashboard.

**Known gaps at time of writing:**
- casehubio/engine#350 — engine must add `openclaw` to its dispatch list.

---

## 22. Memory Update

- [ ] Update your Claude memory for the parent project to reflect the new repos (path is developer-specific).

---

## Common Mistakes (verified from practice)

| Mistake | Symptom | Fix |
|---|---|---|
| Missing `repository_dispatch` trigger in publish.yml | New repo never rebuilds on upstream changes — only on direct push | Add `repository_dispatch: types: [upstream-published]` to `on:` block |
| Wrong scope for casehub-platform in app module | All @QuarkusTest pass; augmentation fails ~20s later with `UnsatisfiedResolutionException` | Use `<scope>runtime</scope>` in app modules, `<scope>test</scope>` in library modules (PP-20260524-a8f597) |
| Domain Flyway migrations start at V1 | Startup failure: "Found more than one migration with version 1" after casehub-work added | Rename domain migrations to V100+ before wiring casehub-work |
| Missing `classpath:db/ledger/migration` in Flyway locations | Test failure: "Table LEDGER_ENTRY not found" | Add to `quarkus.flyway.locations` (PP-20260524-10efef) |
| Upstream repo not dispatching to new repo | New repo always stale after upstream publishes | File issue on upstream peer repo; add to dispatch list in their publish.yml |
| wksp symlink missing from project root | `work-start` and other skills can't find the workspace | `ln -s $CASEHUB_WORKSPACE/<name> $CASEHUB_LOCAL/<name>/wksp` |
| Workspace git not initialized | Sessions bleed into parent workspace; branches and artifacts from multiple projects entangle in parent git history | Run Step 14 git init steps; add `/<name>` to parent workspace `.gitignore` |
| CLAUDE.md missing peer repos hard boundary section | Claude session in new repo may accidentally commit to sibling repos | Add complete `Peer Repos — Hard Boundary` section listing all sibling repos |
| Engine workflow not updated | openclaw never triggered by engine changes | File issue on casehubio/engine (cannot commit from parent session) — engine#350 pending |
| Assuming engine triggers claudony | Claudony trigger broken if engine changes | Engine triggers `flow` not claudony; claudony is triggered by qhorus — verify actual workflow files, don't assume from the dep graph |
| `docs/index.html` PLATFORM_REPOS not updated | Repo missing from CI dashboard | Add to `PLATFORM_REPOS` or `APP_REPOS` array |
| casehubio.github.io not updated | New repo absent from public landing page | Add SVG text element + project card in correct tier tab |
| README.md badges missing | No visible build status for the new repo from the parent | Add badge row under correct section |
| CSV files not updated | `build-all.yml` clone/build steps missing the new repo; local `build-all.sh` also skips it | Add line to `build/modules-core.csv` or `modules-applications.csv`; pre-commit hook regenerates `build-all.yml` automatically |
| `blog-routing.yaml` missing | Blog entries written to workspace never get published to mdproctor.github.io | Check `~/.claude/blog-routing.yaml`; create routing entry for the new project's blog path |
| `ARC42STORIES.MD` missing | `handover` skill's arc42 stale-scan step errors on every session wrap | Create stub with all chapters `🔲 pending (TBD)` — even an empty template is enough |
| Issue-workflow not run | Commits go without issue refs; traceability lost from first session | Run `issue-workflow` skill Phase 0 immediately after CLAUDE.md is written |
| CLAUDE.md missing Project Artifacts section | git-squash filter-repo may strip project docs from history; skills treat project content as workspace noise | Add `## Project Artifacts` with paths that are project content (`CLAUDE.md`, `docs/`) |
| CLAUDE.md missing IntelliJ MCP Routing section | Session uses wrong MCP server or tries disabled `mcp__intellij__*` | Add section declaring `mcp__intellij-index__*` as only available server; note `mcp__intellij__*` is disabled |
| CLAUDE.md Work Tracking missing automatic behaviours | Issue creation, epic linkage, and commit refs are not enforced — sessions drift into untracked work | Add 4 automatic behaviour rules under `## Work Tracking` (issue-before-code, epic linkage, commit linkage, no orphan issues) |
| Workspace `blog-routing.yaml` missing | `publish-blog` skill can't find routing chain; blog entries never published even though global config exists | Create `blog-routing.yaml` in workspace dir with `extends: ~/.claude/blog-routing.yaml` |
| Module not in parent `<modules>` list | Child module builds locally but never publishes — downstream repos get `Could not resolve` | Verify every child module is listed in root pom.xml `<modules>` and has correct `<parent>` reference |
