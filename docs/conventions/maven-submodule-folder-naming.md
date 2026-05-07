# Convention: Maven Submodule Folder Names Are Short — No Repo Prefix

**Applies to:** All multi-module casehub repos  
**Severity:** Important — prefix creep makes repos harder to navigate and is inconsistent with Quarkus extension conventions

## Rule

Submodule folder names are short and descriptive. They do not repeat the repo name as a prefix. The repo directory provides the context — the folder does not need to restate it.

The `artifactId` in `pom.xml` carries the fully qualified name. The folder does not.

## Standard Names

**Role modules** — every extension has these, always use these exact names:

| Role | Folder name | ArtifactId pattern |
|------|------------|-------------------|
| Public API / SPI | `api` | `casehub-{repo}-api` |
| Runtime implementation | `runtime` | `casehub-{repo}` |
| Quarkus deployment processor | `deployment` | `casehub-{repo}-deployment` |
| Test utilities | `testing` | `casehub-{repo}-testing` |
| Runnable examples | `examples` | `casehub-{repo}-examples` |
| Integration tests | `integration-tests` | `casehub-{repo}-integration-tests` |

**Capability modules** — short descriptive name, no prefix:

```
queues           not casehub-work-queues
ai               not casehub-work-ai
ledger           not casehub-work-ledger
notifications    not casehub-work-notifications
blackboard       not casehub-engine-blackboard
persistence-memory   not casehub-persistence-memory
work-adapter     not casehub-work-adapter
```

## Examples

```
casehub/ledger/          ← repo root
  api/                   ← artifactId: casehub-ledger-api       ✓
  runtime/               ← artifactId: casehub-ledger            ✓
  deployment/            ← artifactId: casehub-ledger-deployment ✓
  examples/              ← artifactId: casehub-ledger-examples   ✓

casehub/work/
  api/                   ← artifactId: casehub-work-api          ✓
  core/                  ← artifactId: casehub-work-core         ✓
  runtime/               ← artifactId: casehub-work              ✓
  queues/                ← artifactId: casehub-work-queues       ✓
  ai/                    ← artifactId: casehub-work-ai           ✓
  notifications/         ← artifactId: casehub-work-notifications ✓

casehub/devtown/
  domain/                ← artifactId: casehub-devtown-domain    ✓
  review/                ← artifactId: casehub-devtown-review    ✓
  queue/                 ← artifactId: casehub-devtown-queue     ✓
  app/                   ← artifactId: casehub-devtown-app       ✓
```

## Anti-Pattern

```
casehub/work/
  casehub-work-api/      ✗  redundant prefix
  casehub-work-queues/   ✗  redundant prefix

casehub/devtown/
  devtown-domain/        ✗  redundant prefix
  devtown-review/        ✗  redundant prefix
```

## Repos Already Correct

`casehub-ledger` and `casehub-qhorus` follow this convention. Use them as the reference.

## Repos With Deviations (tracked in workspace plan)

`casehub-work`, `casehub-engine`, `casehub-connectors`, `casehub-claudony`, `casehub-devtown` — see `~/claude/public/casehub/plans/module-naming-alignment.md`.
