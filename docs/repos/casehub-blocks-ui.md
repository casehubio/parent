# casehub-blocks-ui — Platform Deep Dive

**GitHub:** [casehubio/blocks-ui](https://github.com/casehubio/blocks-ui)
**Platform doc:** [PLATFORM.md](https://raw.githubusercontent.com/casehubio/parent/main/docs/PLATFORM.md)

---

## Purpose

Shared UI components for CaseHub applications. Composed from casehub-pages primitives (`registerPanel`, `hostPanel`, `pages-event`, dataset contracts). Domain-aware but app-agnostic — components know about trust scores, case timelines, and channel activity, but not about AML investigations or clinical trials.

The UI parallel to `casehub-blocks` (shared Java coordination patterns composed from qhorus, engine, work primitives).

---

## Module Structure

| Package | Purpose |
|---------|---------|
| `packages/blocks-ui-core` | Shared theme, dataset helpers, event contracts |
| `components/case-timeline` | Case lifecycle timeline — status progression, milestones, agent activity |
| `components/trust-score-panel` | Agent trust score visualisation — Bayesian Beta scores, trend lines |
| `components/channel-activity` | Qhorus channel activity feed — message stream, commitment status |

---

## Depends On

- `casehub-pages` — `@casehubio/pages-data`, `@casehubio/pages-component` for dataset contracts and component API

## Depended On By

Application repos embed components via `hostPanel` + `registerPanel` in their pages dashboards.

---

## Current State

Scaffold — Yarn workspace, TypeScript, 3 stub components. No implementation yet.
