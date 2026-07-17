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
| `packages/blocks-ui-core` | Tokens (re-exported from pages-ui-tokens), DataSourceMixin + DataSourceAdapter + fetchSource + createTypedFetchSource + EMPTY_DATASET, TrendSourceMixin, renderSparkline (inline SVG polyline + gradient fill), EventStreamController (SSE reactive controller), event helpers (re-exported from pages-component), domain types (TrustLevel, trustLevelFromScore), SharedTimerController, blocks-confirm-dialog (FocusTrapMixin, danger/success/neutral variants), schema-form (JSON-schema-driven), renderPropertyTree (recursive nested objects), pulseAnimation CSS | Beta |
| `components/split-workbench` | Generic split-pane layout shell — draggable divider, localStorage-persisted ratio, CSS container query responsive mode (single-panel below 768px), selection coordination via pages-event topics | Beta |
| `components/list-pane` | Data list wrapping `<pages-table>` — paginated mode, single selection, client-sort/filter, emits selection events on topic. Uses DataSourceMixin for endpoint-driven data. | Beta |
| `components/detail-pane` | Tabbed detail view — lazily creates tab panels via `TabDefinition[]`, receives selected item via topic events, keyboard tab navigation | Beta |
| `components/grouped-data-view` | Grouped tabular data — wraps `<pages-grouped-view>`, three presets (sectioned/spreadsheet/list), configurable group ordering/styling, expand/collapse | Beta |
| `components/work-item-inbox` | Work item inbox — queue pill bar, scope context, filter bar, SSE lifecycle, three-tab perspective (My Work / Claimable / All) | Beta |
| `components/work-item-row` | Single work item row component (legacy — inbox now uses pages-table) | Deprecated |
| `components/work-item-detail` | Work item detail panel — action bar, activity tab, relations tab with semantic type inverses | Beta |
| `components/work-item-workbench` | Full workbench — split-pane layout with inbox (left) and detail (right), keyboard shortcuts | Beta |
| `components/notification-inbox` | Notification inbox — bell with unread badge, inbox with tabs/filters/SSE, subscription list CRUD | Beta |
| `components/sla-indicator` | SLA deadline indicator — countdown, breach state, escalation badge, threshold-based colour transitions | Stable |
| `components/kpi-metric-row` | KPI metric cards — responsive grid with sparklines, trends, status colours, density property (comfortable/compact/dense), reactive endpoint | Stable |
| `components/approval-gate` | Approval gate — structured decision point with quorum, evidence slots, SLA integration, confirmation dialog | Beta |
| `components/audit-trail-viewer` | Audit trail viewer — ledger entries with pages-table, Merkle verification banner, attestations, actor/type/date filters, GDPR erasure handling | Beta |
| `components/blocks-timeline` | Pluggable timeline — strategy-based content (event chronology, state progression, commitment lifecycle), three layouts (vertical, horizontal, compact), render callbacks. Replaces case-timeline. | Beta |
| `components/trust-score-panel` | Trust score panel — SVG gauge, per-capability breakdown table, trend sparkline, maturity badges, compact badge mode | Beta |
| `components/channel-activity` | Qhorus channel activity — 8 sub-elements (feed, message, reaction-bar, input, emoji-picker, thread, nav, member-panel). Message grouping (2-min window), speech-act types (QUERY, COMMAND, RESPONSE, etc.), commitment states, DOMPurify + marked rendering. Promoted from connectors. | Beta |
| `components/similarity-panel` | Similar past cases — similarity bar + outcome badges via pages-table. Uses DataSourceMixin or direct data. Promoted from clinical. | Beta |
| `components/compliance-summary` | Regulation compliance grid — status badges (MET/PARTIAL/GAP/BREACHED), evidence links via pages-table. Uses DataSourceMixin. Promoted from clinical. | Beta |
| `components/trust-feedback-display` | Post-gate trust score delta — decision/attestation badges, trust before→after, full card and compact modes. Promoted from clinical. | Beta |
| `components/sla-breach-policy` | SLA breach escalation tiers — active tier highlighting, pulseAnimation on active tier, optional embedded sla-indicator countdown. Promoted from clinical. | Beta |
| `components/gdpr-erasure-action` | GDPR data erasure form — two-phase (input → confirmation dialog → receipt), blocks-confirm-dialog with persistent/danger variant, ALREADY_WITHDRAWN handling. Promoted from clinical. | Beta |

**Maturity levels:**
- **Stable** — API locked, used in production apps, full test coverage
- **Beta** — API stable, tests exist, used in staging apps or feature-flagged in prod
- **Deprecated** — being replaced, do not use in new code

---

## Key Components

### split-workbench + list-pane + detail-pane

Generic split-pane architecture replacing the monolithic work-item-workbench pattern. Three composable components:
- `<split-workbench>` — draggable divider, responsive single-panel mode, selection coordination via topic events
- `<list-pane>` — wraps `<pages-table>` with DataSourceMixin, emits selection events
- `<detail-pane>` — lazy tab panel creation, receives items via selection events

work-item-workbench still exists but new compositions should use split-workbench + list-pane + detail-pane.

**Consumers:** openclaw, devtown, aml, clinical, drafthouse, life, soc, ops

### grouped-data-view

Grouped tabular data with configurable visual modes — three presets (sectioned, spreadsheet, list) via `<pages-grouped-view>`. Custom group ordering, styling callbacks, expand/collapse.

**Consumers:** clinical, aml (regulation grouping, category views)

### channel-activity

Qhorus channel activity — eight sub-elements covering the full messaging lifecycle: feed (message grouping, threading, auto-scroll), individual messages, reactions, input with speech-act type selector, emoji picker, threaded replies, channel navigation, member panel with presence. Speech-act types: QUERY, COMMAND, RESPONSE, STATUS, DONE, FAILURE, DECLINE, HANDOFF, EVENT. DOMPurify + marked for markdown rendering. Promoted from connectors.

**Consumers:** drafthouse, claudony, devtown, clinical (multi-agent deliberation applications)

### notification-inbox

Notification UI — bell with unread badge, inbox with tabs/filters/SSE, subscription list CRUD.

**Consumers:** all applications (platform-level feature)

### audit-trail-viewer

Ledger entry viewer — pages-table rendering, Merkle verification banner, attestations, actor/type/date filters, GDPR erasure handling.

**Consumers:** aml, clinical, devtown, life, soc (compliance-heavy applications)

### blocks-timeline

Pluggable timeline — strategy-based content with three strategies: event chronology (case events), state progression (qhorus workflows), commitment lifecycle (COMMANDED → ACKNOWLEDGED → DONE/DECLINED). Three layouts (vertical, horizontal, compact), render callback resolution, temporal weighting. Replaces case-timeline.

**Consumers:** aml, clinical, life, ops, drafthouse, devtown (case-centric and workflow applications)

### trust-score-panel

Trust score visualisation — SVG gauge, per-capability breakdown table, maturity badges, compact badge mode.

**Consumers:** aml, devtown, clinical, life, ops (trust-aware routing applications)

## Data Architecture

### DataSourceMixin vs EventStreamController

Two complementary data-fetch patterns in blocks-ui-core:

**DataSourceMixin** — Lit mixin for pull-based data loading (REST endpoints). Adds `endpoint`, `loading`, `error`, `dataSet` properties. Wraps `DataSourceAdapter` → `DataSourceController` from pages-component. Used by: similarity-panel, compliance-summary, grouped-data-view, list-pane.

**EventStreamController** — Lit `ReactiveController` for push-based data (SSE streams). Wraps `EventStream` from pages-data. Provides `latest`, `all`, and `status` (ConnectionStatus). Batches events by default. Connects/disconnects on host lifecycle.

Components can use both — DataSourceMixin for initial load, EventStreamController for live updates.

### Shadow DOM select gotcha

The `<select>` element inside Shadow DOM can silently reset to the first option when `.value` is set before `<option>` children have rendered. The gdpr-erasure-action component demonstrates the workaround: dispatch a `change` event explicitly after setting the value programmatically.

---

## Depends On

- `casehub-pages` — `@casehubio/pages-data`, `@casehubio/pages-component`, `@casehubio/pages-ui-tokens`, `@casehubio/pages-primitives` (a11y mixins, pages-modal, focus trap), `@casehubio/pages-table` (data table component, migrated from blocks-ui)

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
