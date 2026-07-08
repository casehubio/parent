# casehub-blocks-ui — Platform Deep Dive

**GitHub:** [casehubio/blocks-ui](https://github.com/casehubio/blocks-ui)
**Platform doc:** [PLATFORM.md](https://raw.githubusercontent.com/casehubio/parent/main/docs/PLATFORM.md)

---

## Purpose

Shared UI components for CaseHub applications — the UI parallel to `casehub-blocks` (shared Java coordination patterns). Each component consumes `casehub-pages` APIs (`registerPanel`, `pages-event`, dataset contracts) but knows nothing about a specific app's domain model.

Domain-aware but app-agnostic — components know about trust scores, case timelines, channel activity, work items, and audit trails, but not about AML investigations, clinical trials, or governance processes. Applications compose these blocks into domain-specific dashboards.

---

## Design Philosophy

- Components should be framework-agnostic Web Components where possible
- Each component defines its dataset contract (what data shape it consumes)
- Components communicate via `pages-event` CustomEvent — no direct component-to-component coupling
- Components should work standalone in a test harness AND embedded via pages `hostPanel`
- Visual consistency through `--pages-*` CSS custom properties from `pages-ui-tokens`
- Design for the full platform: trust scores from ledger, channel activity from qhorus, case timelines from engine, work items from work, IoT device state from iot

---

## Module Structure

| Package | Purpose | Maturity |
|---------|---------|----------|
| `packages/blocks-ui-core` | Tokens (re-exported from pages-ui-tokens), DataEndpointMixin, a11y mixins, event helpers (re-exported from pages-component), domain types, SharedTimerController, blocks-confirm-dialog, schema-form | Beta |
| `components/data-table` | Generic data table with three display modes, virtual scroll, ARIA grid, 2D keyboard navigation | Stable |
| `components/work-item-inbox` | Work item inbox — queue pill bar, scope context, filter bar, SSE lifecycle, three-tab perspective (My Work / Claimable / All) | Beta |
| `components/work-item-row` | Single work item row component (legacy — inbox now uses data-table) | Deprecated |
| `components/work-item-detail` | Work item detail panel — action bar, activity tab, relations tab with semantic type inverses | Beta |
| `components/work-item-workbench` | Full workbench — split-pane layout with inbox (left) and detail (right), keyboard shortcuts | Beta |
| `components/notification-inbox` | Notification inbox — bell with unread badge, inbox with tabs/filters/SSE, subscription list CRUD | Beta |
| `components/sla-indicator` | SLA deadline indicator — countdown, breach state, escalation badge, threshold-based colour transitions | Stable |
| `components/kpi-metric-row` | KPI metric cards — responsive grid with sparklines, trends, status colours, density property (comfortable/compact/dense), reactive endpoint | Stable |
| `components/approval-gate` | Approval gate — structured decision point with quorum, evidence slots, SLA integration, confirmation dialog | Beta |
| `components/audit-trail-viewer` | Audit trail viewer — ledger entries with data-table, Merkle verification banner, attestations, actor/type/date filters, GDPR erasure handling | Beta |
| `components/case-timeline` | Case lifecycle timeline — vertical CSS timeline with 30+ event type nodes, compact dot strip mode, stream type filter | Beta |
| `components/trust-score-panel` | Trust score panel — SVG gauge, per-capability breakdown table, maturity badges, compact badge mode | Beta |
| `components/channel-activity` | Qhorus channel activity feed — message stream, commitment status, speech act badges | Beta |

**Maturity levels:**
- **Stable** — API locked, used in production apps, full test coverage
- **Beta** — API stable, tests exist, used in staging apps or feature-flagged in prod
- **Deprecated** — being replaced, do not use in new code

---

## Key Components

### data-table

Generic data table — three display modes (auto/paginated/scroll), CSS Grid rendering, virtual scroll engine, ColumnDef\<R\> data model, multi-mode selection, client-side sorting and filtering, column visibility, ARIA grid, 2D keyboard navigation, CSS ::part() row styling.

**Used by:** work-item-inbox, audit-trail-viewer, trust-score-panel (capability breakdown)

### work-item-workbench

Full work item management UI — split-pane layout with inbox (left) and detail (right), keyboard shortcuts, queue scope integration, SSE lifecycle for live updates.

**Consumers:** openclaw, devtown, aml, clinical, drafthouse, life, soc, ops

### notification-inbox

Notification UI — bell with unread badge, inbox with tabs/filters/SSE, subscription list CRUD.

**Consumers:** all applications (platform-level feature)

### audit-trail-viewer

Ledger entry viewer — data-table rendering, Merkle verification banner, attestations, actor/type/date filters, GDPR erasure handling.

**Consumers:** aml, clinical, devtown, life, soc (compliance-heavy applications)

### case-timeline

Case lifecycle timeline — vertical CSS timeline with 30+ event type nodes, compact dot strip mode, stream type filter.

**Consumers:** aml, clinical, life, ops, drafthouse (case-centric applications)

### trust-score-panel

Trust score visualisation — SVG gauge, per-capability breakdown table, maturity badges, compact badge mode.

**Consumers:** aml, devtown, clinical, life, ops (trust-aware routing applications)

### channel-activity

Qhorus channel activity feed — message stream, commitment status, speech act badges.

**Consumers:** drafthouse, claudony, devtown, clinical (multi-agent deliberation applications)

---

## Depends On

- `casehub-pages` — `@casehubio/pages-data`, `@casehubio/pages-component`, `@casehubio/pages-ui-tokens` for dataset contracts, component API, and design tokens

---

## Depended On By

Application repos embed components via `hostPanel` + `registerPanel` in their pages dashboards. Each application's dashboard composes blocks-ui components into domain-specific layouts.

---

## Configuration

Components read runtime configuration from dataset endpoints:
- Polling intervals (default 30s, configurable per component)
- SSE reconnection (exponential backoff, max 60s)
- Virtual scroll viewport (default 500px ahead/behind)
- Data table page size (default 25)

No build-time configuration — all Yarn workspace with TypeScript project references.
