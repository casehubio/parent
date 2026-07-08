# UI Architecture

> **Scope:** pages → blocks-ui → app UI layering, composition patterns, component catalogue
> **Audience:** App builders primarily; platform builders extending pages/blocks-ui
> **Key repos:** casehub-pages (infrastructure), casehub-blocks-ui (domain components)
> **Protocols:** custom-event-shadow-dom, lit-immutable-collections

## Overview

CaseHub UI is built in three layers. Each layer has a clear boundary and defined contracts. Apps compose UIs by combining infrastructure (pages), domain components (blocks-ui), and app-specific panels.

## Three-Layer Model

```
┌────────────────────────────────────────────────┐
│ Layer 3: App UI (aml, devtown, drafthouse)    │
│ App-specific panels, domain logic, workflows  │
│ Consumes: pages APIs + blocks-ui components   │
└────────────────────────────────────────────────┘
                    ↓
┌────────────────────────────────────────────────┐
│ Layer 2: blocks-ui (domain components)        │
│ Shared, domain-aware UI components            │
│ Consumes: pages APIs (registerPanel, events)  │
│ Examples: work-item-inbox, trust-score-panel  │
└────────────────────────────────────────────────┘
                    ↓
┌────────────────────────────────────────────────┐
│ Layer 1: pages (infrastructure)               │
│ Dashboard rendering, layout, data pipeline    │
│ Web Components, ECharts, JSONata, SSE         │
└────────────────────────────────────────────────┘
```

**Key principle:** Layers are unidirectional. blocks-ui depends on pages, apps depend on both. pages knows nothing about domain concepts (work items, trust scores, agents). blocks-ui knows CaseHub domain concepts but not app-specific workflows.

## Layer 1: pages (Infrastructure)

**Repository:** casehub-pages

**What it provides:** Dashboard rendering infrastructure — YAML-driven layout, data operations, visualization components, iframe-isolated microfrontends, server-sent events.

### Core Packages

**TypeScript Packages:**

- `@casehubio/pages-ui-tokens` — OKLCH 12-step design tokens (colour scales, spacing, typography, elevation, motion, radius). Theme generation and injection.
- `@casehubio/pages-data` — DataSet model, operations engine, external data extraction, JSONata. Push wire protocol (`EventConnection`, `PushSource`, `WebSocketSource`). General-purpose `SSEManager` (connection pooling, named event support, reconnection).
- `@casehubio/pages-ui` — YAML parser, DashBuilder backward compat, component model.
- `@casehubio/pages-viz` — Web Component chart/table/metric wrappers (ECharts).
- `@casehubio/pages-component` — CSS grid layout renderer, interactive containers.
- `@casehubio/pages-runtime` — Site orchestrator: `loadSite()` API, navigation, data pipeline, layout serialization (`LayoutStore`, `createLocalLayoutStore`).

**Iframe Component API:**

- `@casehubio/pages-iframe-api` — Component controller for iframe-isolated components.
- `@casehubio/pages-iframe-dev` — Development utilities for component testing.
- `@casehubio/pages-echarts-base` — Reusable ECharts wrapper library.

**Standalone Components:**

- `@casehubio/pages-component-echarts` — Apache ECharts visualizations.
- `@casehubio/pages-component-llm-prompter` — LLM prompt engineering UI.
- `@casehubio/pages-component-svg-heatmap` — SVG-based heatmaps.

**Java Backend:**

- `casehub-pages-push` — Typed wire protocol SDK: `PushMessage` (server→client builders), `PushRequest` (sealed client→server parser with ack/error correlation), `TopicRegistry` (wildcard-aware connection tracking), `EventStore` SPI + `InMemoryEventStore` (bounded per-topic event replay). jackson-core only, no Quarkus.

### Key Contracts

#### ConfigurablePanel

**Purpose:** Register a custom panel that can be embedded in a pages dashboard via YAML `hostPanel` directive.

**Registration:**

```typescript
import { registerPanel } from '@casehubio/pages-runtime';

registerPanel('work-item-inbox', {
  create: (config: unknown) => {
    const element = document.createElement('work-item-inbox');
    // Apply config...
    return element;
  }
});
```

**YAML usage:**

```yaml
layout:
  - type: hostPanel
    panelType: work-item-inbox
    config:
      queueId: "my-queue"
```

#### DataReceiver

**Purpose:** Components that consume data from pages data pipeline implement this interface (implicit contract — duck typing).

**Contract:**

```typescript
interface DataReceiver {
  receiveData(data: unknown): void;
}
```

When a component is bound to a data source in YAML (`dataRef: "myData"`), the pages runtime calls `element.receiveData(data)` whenever the data changes.

#### pages-event

**Purpose:** Custom events for inter-component communication. All blocks-ui components communicate via `pages-event` — no direct component-to-component coupling.

**Dispatch:**

```typescript
this.dispatchEvent(new CustomEvent('pages-event', {
  bubbles: true,
  composed: true,
  detail: {
    type: 'work-item-selected',
    workItemId: 'WI-123'
  }
}));
```

**Listen:**

```typescript
document.addEventListener('pages-event', (e: CustomEvent) => {
  if (e.detail.type === 'work-item-selected') {
    // Handle selection...
  }
});
```

**Why CustomEvent, not typed events:** Framework-agnostic. Works with Lit, React, Vue, vanilla JS. Shadow DOM boundary is crossed via `composed: true`.

### Data Flow

```
YAML definition
    ↓
pages-ui (parse) → DataSet model
    ↓
pages-data (resolve) → operations (filter, sort, transform)
    ↓
pages-component (layout) → CSS Grid
    ↓
pages-viz (render) → ECharts / table / metric
    ↓
User interaction → pages-event (filter/sort/select)
    ↓
Back to data layer (re-resolve)
```

### SSE Integration

**Purpose:** Server-sent events for real-time data updates.

**Client-side:** `SSEManager` (from `@casehubio/pages-data`) — connection pooling, named event support, automatic reconnection.

**Server-side:** `casehub-pages-push` (Java) — typed wire protocol, topic registry, event store for replay.

**Protocol:**

1. Client subscribes via `SSEManager.subscribe(url, eventTypes)`
2. Server sends `PushMessage` events (topic + payload + sequence)
3. Client fires `pages-event` with the payload
4. Components listen for `pages-event` and update their data

## Layer 2: blocks-ui (Domain Components)

**Repository:** casehub-blocks-ui

**What it provides:** Shared UI components for CaseHub applications. Each component consumes pages APIs but knows nothing about a specific app's domain model.

### Component Catalogue

**Work Management:**

- `work-item-inbox` — Three-tab perspective (My Work / Claimable / All). Queue pill bar, scope context bar, filter bar with counts, summary bar. Uses `data-table` for rendering. SSE lifecycle for real-time updates.
- `work-item-detail` — Action bar, activity tab, relations tab.
- `work-item-workbench` — Split-pane layout (inbox left, detail right). Keyboard shortcuts (`Ctrl+K` for command palette, `j`/`k` for navigation).
- `work-item-row` (legacy) — Single work item row. Replaced by `data-table` in inbox.

**Data Display:**

- `data-table` — Generic data table. Three display modes (auto/paginated/scroll). CSS Grid rendering. Virtual scroll engine. `ColumnDef<R>` data model. Multi-mode selection. Client-side sorting. Column visibility. ARIA grid. 2D keyboard navigation. CSS `::part()` row styling.
- `kpi-metric-row` — KPI metric cards. Responsive grid with sparklines, trends, status colours.
- `case-timeline` — Case lifecycle timeline. Status progression, milestone markers, agent activity.

**Approvals and SLA:**

- `approval-gate` — Structured decision point. Quorum, evidence slots, SLA integration, confirmation dialog.
- `sla-indicator` — SLA deadline indicator. Countdown, breach state, escalation badge, threshold-based colour transitions.

**Trust and Channels:**

- `trust-score-panel` — Agent trust score visualisation. Bayesian Beta scores, trend lines, per-capability breakdown.
- `channel-activity` — Qhorus channel activity feed. Message stream, commitment status, speech act badges.

### Design Philosophy

**Framework-agnostic:** Web Components where possible. No React, Vue, or Angular dependency in blocks-ui. Apps can use any framework.

**Dataset contracts:** Each component defines what data shape it consumes (TypeScript interface). The data source is external (pages data pipeline, REST API, SSE).

**Event-driven communication:** Components emit `pages-event` for state changes. Other components listen. No direct coupling.

**Standalone testable:** Every component works in a test harness AND embedded via pages `hostPanel`. Test harness uses `@casehubio/pages-iframe-dev`.

**Shared theme:** `BlocksTheme` (from `blocks-ui-core`) provides consistent design tokens. All components consume the theme.

### blocks-ui-core

**Shared utilities for all blocks-ui components:**

- **Theme:** `BlocksTheme` — OKLCH-based colour scales, spacing, typography. Injects CSS custom properties.
- **Dataset helpers:** Typed interfaces for common data shapes (work item, trust score, case).
- **Event contracts:** TypeScript types for `pages-event` detail payloads.
- **A11y mixins:** Shared ARIA attribute helpers, keyboard navigation utilities.
- **SSE manager:** Wrapper around `@casehubio/pages-data` SSE with blocks-ui conventions.
- **SharedTimerController:** Lit reactive controller for shared timers (e.g. "time ago" labels that update every 30s across all components).
- **blocks-confirm-dialog:** Shared confirmation dialog Web Component (used by approval-gate, work-item-detail).
- **schema-form:** JSON Schema-driven form generator (used for dynamic config panels).

### Maturity Levels

Components are tagged with maturity levels (internal tracking — not exposed in the component API):

- **Alpha** — experimental, API unstable
- **Beta** — API stabilising, used in 1 app
- **Stable** — API stable, used in 2+ apps, full test coverage

**Current stable components:** `data-table`, `work-item-inbox`, `trust-score-panel`.

## Layer 3: App UI (aml, devtown, drafthouse, etc.)

**What apps provide:** Domain-specific panels, workflows, and orchestration.

### Composition Pattern

Apps compose UIs via **Quinoa + pages runtime + hostPanel**:

1. **Quinoa** (Quarkus extension) serves the pages webapp from `src/main/webui/`
2. **pages runtime** loads YAML dashboard definitions from the server
3. **hostPanel** embeds blocks-ui components and app-specific panels

**Example (AML investigation dashboard):**

```yaml
# aml/src/main/resources/dashboards/investigation.yaml
title: Investigation Dashboard
layout:
  - type: hostPanel
    panelType: work-item-inbox
    config:
      queueId: "aml-investigations"
  - type: hostPanel
    panelType: aml-transaction-graph
    config:
      caseId: "{{ caseId }}"
```

**How it works:**

1. AML app registers both blocks-ui panels (`work-item-inbox`) and app-specific panels (`aml-transaction-graph`) via `registerPanel()`
2. Quinoa serves the YAML and the webapp bundle
3. pages runtime parses the YAML, creates the panels, wires data bindings
4. SSE updates flow from the AML backend → pages-push → SSEManager → components

### App-Specific Panels

**What belongs in the app layer:**

- Domain logic (AML: transaction graph analysis, fraud scoring)
- Workflow orchestration (clinical: trial protocol state machine)
- App-specific data fetching (devtown: GitHub PR comments)
- Backend integration (aml: call AML REST API, not pages data pipeline)

**What does NOT belong in the app layer:**

- Generic work item rendering → use `work-item-inbox` from blocks-ui
- Generic data tables → use `data-table` from blocks-ui
- Trust score visualisation → use `trust-score-panel` from blocks-ui

**Boundary rule:** If 2+ apps need the same component, extract it to blocks-ui. If it's app-specific, keep it in the app repo.

## How Apps Compose UIs

### AML (Anti-Money Laundering)

**Key panels:**
- `work-item-inbox` (blocks-ui) — investigation queue
- `aml-transaction-graph` (aml-specific) — network graph of related transactions
- `trust-score-panel` (blocks-ui) — investigator trust scores
- `approval-gate` (blocks-ui) — SAR filing approval

**Data sources:** AML REST API (alerts, transactions, entities), ledger REST API (trust scores), SSE (real-time alert updates).

### DevTown (PR Review)

**Key panels:**
- `work-item-inbox` (blocks-ui) — PR review queue
- `devtown-pr-diff` (devtown-specific) — side-by-side diff viewer
- `channel-activity` (blocks-ui) — deliberation channel feed
- `trust-score-panel` (blocks-ui) — reviewer trust scores

**Data sources:** GitHub API (PRs, comments, commits), work REST API (work items), SSE (PR state changes).

### Drafthouse (Content Review)

**Key panels:**
- `work-item-inbox` (blocks-ui) — content moderation queue
- `drafthouse-content-viewer` (drafthouse-specific) — multi-format content renderer (text, image, video)
- `case-timeline` (blocks-ui) — moderation history
- `approval-gate` (blocks-ui) — escalation gate

**Data sources:** Drafthouse REST API (content items, moderation actions), SSE (real-time content updates).

## Build and Development

### pages Build

```bash
# Full build (development)
yarn install && yarn build

# Production build (includes examples gallery)
yarn build:prod

# Targeted builds
yarn build:packages   # Shared TypeScript packages only
yarn build:components # Iframe components (packages must be built first)
yarn build:webapp     # Final webapp assembly

# Type checking (incremental cross-package)
yarn typecheck

# Linting (ESLint with strict-type-checked rules)
yarn lint
```

### blocks-ui Build

```bash
yarn install
yarn build
yarn test
yarn typecheck
```

### App Integration

Apps consume pages + blocks-ui via:

1. **NPM packages:** `@casehubio/pages-runtime`, `@casehubio/pages-data`, `@casehubio/blocks-ui-core`, `@casehubio/data-table`, etc.
2. **Quinoa:** Quarkus extension that serves the webapp bundle
3. **registerPanel():** Apps register their panels at webapp startup

## Extension Points

### Custom Panels

Implement a Web Component, register it with pages runtime:

```typescript
class MyCustomPanel extends LitElement {
  receiveData(data: unknown) {
    // Handle data updates...
  }

  render() {
    return html`<div>...</div>`;
  }
}

customElements.define('my-custom-panel', MyCustomPanel);
registerPanel('my-custom-panel', {
  create: (config) => {
    const element = document.createElement('my-custom-panel');
    // Apply config...
    return element;
  }
});
```

### Custom Data Sources

Implement a `DataSource` (pages-data contract):

```typescript
class MyApiDataSource implements DataSource {
  async fetch(): Promise<unknown> {
    const response = await fetch('/api/my-data');
    return response.json();
  }
}
```

### Custom Visualizations

Extend `@casehubio/pages-viz` or create a standalone component:

```typescript
class MyChartComponent extends LitElement {
  receiveData(data: ChartData) {
    // Render chart...
  }
}
```

## Testing

### pages Tests

- **Vitest / Jest** — unit tests for all packages
- **Component tests** — `@casehubio/pages-iframe-dev` test harness for iframe components

### blocks-ui Tests

- **Vitest** — unit tests for all components
- **Playwright** (future) — E2E tests for interaction flows

### App Tests

- **Quarkus Test** — backend integration tests
- **Playwright** — E2E tests for full workflows (pages + blocks-ui + app panels)

## See Also

- [pages Repository](https://github.com/casehubio/pages) — infrastructure layer
- [blocks-ui Repository](https://github.com/casehubio/blocks-ui) — domain component catalogue
- [Protocols: custom-event-shadow-dom](https://github.com/casehubio/garden/blob/main/docs/protocols/casehub/custom-event-shadow-dom.md)
- [Protocols: lit-immutable-collections](https://github.com/casehubio/garden/blob/main/docs/protocols/casehub/lit-immutable-collections.md)
