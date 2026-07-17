# casehub-pages — Platform Deep Dive

**GitHub:** [casehubio/casehub-pages](https://github.com/casehubio/casehub-pages)  
**Platform doc:** [PLATFORM.md](https://raw.githubusercontent.com/casehubio/parent/main/docs/PLATFORM.md)

**Tier:** Foundation — UI Infrastructure

---

## Purpose

Web component framework for composable data dashboards. YAML-declarable layouts with CSS grid rendering, JSONata-powered data pipelines, Apache ECharts visualizations, and iframe-isolated React components. Designed as the UI foundation for CaseHub applications — enables non-developers to author interactive dashboards without writing code.

Replaces GWT-based dashbuilder/melviz with a 100% TypeScript stack. Integrates with Quarkus via Quinoa for zero-config bundling and hot reload during development.

---

## Module Structure

### Core Packages (`packages/`)

| Package | Purpose |
|---------|---------|
| `@casehubio/pages-ui-tokens` | OKLCH 12-step design tokens — color scales, spacing, typography, elevation, motion, radius. Theme generation and injection. Must build before `pages-viz`. |
| `@casehubio/pages-data` | DataSet model (`TypedDataSet`, `TypedRow`, `Column`, `ColumnType`), operations engine (`FilterOp`/`GroupOp`/`SortOp` pipeline with `F*G*S?` ordering), external data extraction, JSONata. Push wire protocol (`EventStream`, `EventStreamPool` connection multiplexer). DataSource abstraction (`DataSource`/`DataSink`/`MutableDataSource` with source implementations: REST, SSE, WebSocket, CSV, inline, simulated, composite, replay, recording). `DataSetManager` (CRUD via `DataSetEvent`, typed lookups with pagination). Filter model type safety: per-type discriminated unions (`NumericFilter`/`StringFilter`/`DateFilter`) resolved via `resolveFilterTypes()`. `ScenarioController` for demo/scenario playback. |
| `@casehubio/pages-ui` | YAML parser (including `grouped-view` desugar with group strategies: distinct, fixedCalendar, dynamicRange, dynamic), DashBuilder backward compat layer, component model. |
| `@casehubio/pages-viz` | Web Component chart/table/metric wrappers (ECharts integration). |
| `@casehubio/pages-component` | CSS grid layout renderer, interactive containers, panel hosting. Exports `ConfigurablePanel` and `DataReceiver` interfaces, `DataSourceController`, expression evaluation (`evaluateExpression`, `createRowContext`), `RowStyleRule` for conditional row styling. |
| `@casehubio/pages-primitives` | Accessibility mixins and modal infrastructure: `FocusTrapMixin` (slot-aware focus trap), `RovingTabindexMixin` (2D keyboard navigation with configurable direction), `KeyboardShortcutMixin`, `LiveRegionMixin`, `<pages-modal>` (dialog component). |
| `@casehubio/pages-table` | Data table component (`<pages-table>`) — migrated from blocks-ui. Three display modes (auto/paginated/scroll), virtual scroll engine, CSS Grid rendering, `TableColumnConfig`/`ColumnRenderer` data model, multi-mode selection, client-side sorting and filtering, column visibility, ARIA grid, 2D keyboard navigation via `RovingTabindexMixin`, row-detail expansion (`getRowDetail`, `detailMode: single/multi`), jump-to-page, page size selector, tree/hierarchical data (`getChildren`, `buildTreeIndex`), CSV export, conditional row accent (`getRowAccent`). |
| `@casehubio/pages-runtime` | Site orchestrator: `loadSite()` API, navigation, data pipeline, layout serialization (`LayoutStore`, `createLocalLayoutStore`). |
| `@casehubio/pages-tsconfig` | Shared TypeScript config base (project references, maximum strict mode: `strict`, `noUncheckedIndexedAccess`, `exactOptionalPropertyTypes`, `noImplicitOverride`, `verbatimModuleSyntax`). |
| `@casehubio/pages-webpack-base` | Shared Webpack config presets. |

### Iframe Component API (`packages/`)

| Package | Purpose |
|---------|---------|
| `@casehubio/pages-iframe-api` | Component controller for iframe-isolated components. Provides `postMessage`-based protocol for configuration, data delivery, and lifecycle events. |
| `@casehubio/pages-iframe-dev` | Development utilities for component testing. |
| `@casehubio/pages-echarts-base` | Reusable ECharts wrapper library for iframe components. |

### Standalone Components (`components/`)

| Package | Purpose |
|---------|---------|
| `@casehubio/pages-component-echarts` | Apache ECharts visualizations (iframe-isolated). |
| `@casehubio/pages-component-llm-prompter` | LLM prompt engineering UI (iframe-isolated). |
| `@casehubio/pages-component-svg-heatmap` | SVG-based heatmaps (iframe-isolated). |
| `@casehubio/pages-component-terminal` | Terminal emulator component (iframe-isolated). |

### Backend (Java) (`backend/`)

| Module | Purpose |
|--------|---------|
| `casehub-pages-push` | Typed wire protocol SDK: `PushMessage` (server→client builders with event sequence numbers), `PushRequest` (sealed client→server parser with ack/error correlation), `TopicRegistry` (wildcard-aware connection tracking), `EventStore` SPI + `InMemoryEventStore` (bounded per-topic event replay), `EventBroadcaster` (store + fan-out to subscribed sessions via `SessionSender`), `SessionSender` SPI, `JsonWriter` SPI, `StoredEvent`, `PushColumn`. jackson-core only, no Quarkus. |
| `casehub-pages-push-runtime` | Quarkus CDI producers for push infrastructure: `PushProducers` creates `TopicRegistry`, `EventStore` (@DefaultBean InMemoryEventStore, configurable `max-events-per-topic`), `JsonWriter` (@DefaultBean Jackson ObjectMapper), `EventBroadcaster`. Drop-in for any Quarkus app needing server-push. |
| `casehub-pages-auth` | Authentication token handling for backend data providers. |
| `casehub-pages-data` | Backend data provider adapters (SQL, relay proxy). |
| `casehub-pages-data-sql` | SQL-based data provider with frontend push-down integration. |
| `casehub-pages-layout` | Layout persistence SPI. |
| `casehub-pages-layout-sqlite` | SQLite-based layout store. |

### Assembly

| Package | Purpose |
|---------|---------|
| `@casehubio/pages-webapp` | Webpack orchestrator — assembles final application bundle. |
| `@casehubio/pages-examples` | Interactive dashboard examples gallery (port 8080). |

---

## Key Abstractions

### ConfigurablePanel Interface

Pre-attachment configuration contract for hosted Web Components. Defined in `@casehubio/pages-component/dist/model/hosting.js`.

```typescript
interface ConfigurablePanel<P extends Record<string, unknown> = Record<string, unknown>> {
  configure(props: P): void;
}
```

**Call timing:** `configure(props)` is called before the element is appended to the DOM — before `connectedCallback()` fires. Components should store configuration without triggering rendering at this point.

**Re-configuration:** `configure()` may be called again after initial render (e.g., navigation to a different item). Implementations must handle re-entry: tear down prior state and re-initialize with the new props.

**Props content:** `props` contains the YAML `panelProps` values. The generic `P` gives component authors type safety for their specific props shape; the runtime calls with `Record<string, unknown>`.

### DataReceiver Interface

Data delivery contract for components receiving pipeline data. Defined in `@casehubio/pages-component/dist/model/hosting.js`.

```typescript
interface DataReceiver {
  dataSet: unknown;
  error: string;
}
```

**Mutual-clearing invariant:** implementations must clear `error` when `dataSet` is set, and clear `dataSet` when `error` is set. The pipeline delivers one or the other per cycle, never both — but stale values from a prior cycle must not persist alongside fresh values from the current one.

### DataSet Model

Core data model from `@casehubio/pages-data`. Columnar representation with typed operations.

| Type | Purpose |
|------|---------|
| `DataSet` | Immutable dataset with columns and rows. |
| `Column` | Column metadata: `id`, `name`, `type` (TEXT, NUMBER, DATE, LABEL). |
| `DataSetOp` | Operations: filter, sort, group, select. |
| `applyOps(dataset, ops[])` | Apply operation pipeline to a dataset. |

**External data:** `resolveExternalDataSet()` — fetches data from external sources (CSV, JSON, metrics endpoints). Supports JSONata transformation via `extractDataSet()`.

### pages-event System

Custom event protocol for cross-component communication. Emitted by `emitPagesEvent(target, detail)`, observed via `onPagesEvent(target, handler)`.

**Event types:**
- `pages-filter` — filter change from a chart drill-down or filter widget
- `pages-sort` — sort change from a table header click
- `pages-navigation` — page navigation request

Events propagate through the data pipeline — `DataPipeline.createDataPipeline()` wires pipeline refresh on filter/sort events.

### Composition Pattern

```
YAML → @casehubio/pages-ui (parse) → @casehubio/pages-data (resolve)
  → @casehubio/pages-component (layout) → @casehubio/pages-viz (render)
  → pages-filter/pages-sort events → back to data layer
```

**Entry point:** `loadSite(config, options)` from `@casehubio/pages-runtime`.

**Flow:**
1. `loadSite()` parses YAML, builds `DataSetScope` (all datasets), `PageIndex` (navigation structure)
2. Calls `renderLayout()` from `@casehubio/pages-component` — creates CSS grid layout
3. For each panel, calls `createDataPipeline()` — wires dataset resolution, operations, and delivery to the component via `DataReceiver`
4. Components emit `pages-event` on user interaction (filter, sort) → pipeline re-evaluates → fresh data delivered

### Layout Serialization

**`LayoutStore` SPI** (from `@casehubio/pages-runtime`):

```typescript
interface LayoutStore {
  load(pageId: string): Promise<LayoutState | null>;
  save(pageId: string, state: LayoutState): Promise<void>;
}
```

**Implementations:**
- `createLocalLayoutStore()` — localStorage-backed (client-side persistence)
- `createRestLayoutStore(baseUrl)` — REST API–backed (server-side persistence)

Backend Java module `casehub-pages-layout-sqlite` provides SQLite-backed persistence for Quarkus apps.

### Quinoa Integration Pattern

Quarkus apps embed casehub-pages via the Quinoa extension. Zero-config bundling and hot reload.

**Typical Quarkus app structure:**
```
src/main/webui/           # casehub-pages workspace
  package.json
  webpack.config.js
  src/
    index.ts              # loadSite() entry point
    dashboards/
      main.yaml           # YAML dashboard definitions
```

**Build flow:**
1. Quinoa detects `package.json` in `src/main/webui/`
2. Runs `yarn build` during Quarkus build
3. Copies dist output to `META-INF/resources/`
4. Serves as static assets at runtime

**Hot reload:** Quinoa proxies Webpack dev server during `quarkus:dev` — changes to `main.yaml` or TypeScript sources trigger instant browser refresh.

---

## Push Wire Protocol

Typed WebSocket protocol for server→client data push. Implemented in Java (`casehub-pages-push`) and TypeScript (`@casehubio/pages-data`).

### Server→Client Messages (`PushMessage`)

Fluent builders in Java for typed message construction:

| Builder | Purpose |
|---------|---------|
| `PushMessage.dataUpdate(topic, payload)` | Deliver fresh data for a topic. |
| `PushMessage.listenAck(topic, requestId)` | Acknowledge listen request (client→server). |
| `PushMessage.error(requestId, message)` | Signal error for a request. |
| `PushMessage.keepAlive()` | Heartbeat to prevent connection timeout. |

### Client→Server Messages (`PushRequest`)

Sealed parser in Java for inbound message validation:

| Request Type | Purpose |
|--------------|---------|
| `LISTEN` | Subscribe to a topic (supports wildcards). |
| `UNLISTEN` | Unsubscribe from a topic. |

**Correlation:** client includes `requestId` in LISTEN/UNLISTEN → server echoes in `listenAck()` or `error()` response.

### Topic Routing

`TopicRegistry` (Java) — segment trie for wildcard-aware connection tracking.

**Pattern support:**
- `cases.123.events` — literal match
- `cases.*.events` — single-segment wildcard
- `cases.#` — multi-segment wildcard (all descendants)

**Usage:** when a server pushes `PushMessage.dataUpdate("cases.456.events", data)`, the registry returns all WebSocket sessions subscribed to `cases.456.events`, `cases.*.events`, or `cases.#`.

### Event Store

`EventStore` SPI (Java) + `InMemoryEventStore` — bounded per-topic event replay buffer.

**Purpose:** new subscriptions receive the last N events for a topic immediately upon LISTEN, before any fresh pushes. Prevents "late joiner" data loss.

**Capacity:** configurable per-topic, defaults to 100 events (push-runtime default: 1000).

### EventBroadcaster

`EventBroadcaster` (Java) — store-and-forward push broadcaster. `broadcast(topic, payload)` appends the event to `EventStore` (for replay on reconnect), then fans out the wire message to all sessions subscribed to the topic via `TopicRegistry.connections()`. Validates that broadcast topics contain no wildcards. Supports both raw JSON string and typed object broadcast (serialized via `JsonWriter` SPI).

**CDI integration:** `casehub-pages-push-runtime` provides `PushProducers` — `@ApplicationScoped` CDI producers for `TopicRegistry`, `EventStore` (`@DefaultBean`, configurable `casehub.pages.push.max-events-per-topic`), `JsonWriter` (`@DefaultBean` Jackson ObjectMapper), and `EventBroadcaster`. Quarkus apps add the dependency and get server-push infrastructure with zero boilerplate.

### TypeScript Client

`@casehubio/pages-data` exports three client APIs:

| API | Purpose |
|-----|---------|
| `createWebSocketSource(config)` | WebSocket-based push source (full protocol support). |
| `createSseSource(config)` | SSE-based push source (server→client only, no ack). |
| `createEventConnection(config)` | Event-only WebSocket (no data delivery, just listen/unlisten). |

**SSEManager:** general-purpose SSE client with connection pooling, named event support (`event: topic-name`), and automatic reconnection.

---

## Recent Evolution

### melviz → casehub-pages Rename

Forked from melviz (itself a fork of dashbuilder). Completed migration to 100% TypeScript. All GWT code removed (`_legacy/` reference only, not built).

**Key changes:**
- Package namespace: `@melviz/*` → `@casehubio/pages-*`
- Repo: `melviz/pages` → `casehubio/casehub-pages`
- Java group: `org.melviz` → `io.casehub`

### pages-primitives — Accessibility Mixins and Modal

`@casehubio/pages-primitives` provides foundational a11y infrastructure consumed by both `pages-table` and `blocks-ui` components:

- **FocusTrapMixin** — slot-aware focus trap that correctly handles slotted content in shadow DOM. Traps Tab/Shift+Tab within the component boundary.
- **RovingTabindexMixin** — 2D keyboard navigation (Arrow keys) with configurable direction and selector. Used by `pages-table` for ARIA grid navigation.
- **KeyboardShortcutMixin** — declarative keyboard shortcut binding for components.
- **LiveRegionMixin** — ARIA live region management for screen reader announcements.
- **`<pages-modal>`** — dialog component with focus trap, backdrop, close-on-escape.

Previously removed, pages-primitives was re-created with a narrower scope: pure a11y infrastructure rather than domain-aware UI components (those remain in blocks-ui).

### pages-table — Data Table Migration

`@casehubio/pages-table` (`<pages-table>`) migrated from `blocks-ui` `data-table` component. Now a pages-tier package, consumed by both blocks-ui components and application dashboards directly.

Key capabilities:
- Three display modes: auto (threshold-based), paginated, scroll (virtual)
- Virtual scroll engine with viewport-ahead/behind calculation
- CSS Grid rendering with `TableColumnConfig` / `ColumnRenderer` data model
- Multi-mode selection (none/single/multi) with keyboard support
- Row-detail expansion via `getRowDetail` callback, `detailMode` (single/multi)
- Jump-to-page navigation and page-size selector
- Tree/hierarchical data via `getChildren` + `buildTreeIndex` + expand state
- CSV export (`tableToCsv`, `downloadCsv`, `copyToClipboard`)
- Conditional row styling via `RowStyleRule` expressions and `getRowAccent`
- 2D keyboard navigation via `RovingTabindexMixin` from pages-primitives
- Client-side sorting (multi-column via sort stack) and filtering

### PagesGroupedView — Grouped Tabular Data

`GroupedViewProps` in `@casehubio/pages-component` defines the typed contract for grouped data display. Three presets: `spreadsheet` (group as table row), `sectioned` (group as section heading + table content), `list` (section heading + list content). Supports multi-level grouping (`GroupingKey | GroupingKey[]`), aggregation bindings per column, configurable group ordering, expand/collapse, row accent colouring, and optional `renderAfterHeader` callback for custom group decorations.

`GroupNode` type provides the tree structure: name, depth, startRow, rowCount, children, and optional aggregates. Consumed by `blocks-ui`'s `<grouped-data-view>` component.

### OKLCH Token System

New design token system based on OKLCH color space (perceptually uniform, wide-gamut). 12-step scales for all hue families.

**Before:** Hardcoded CSS colors scattered across components.

**After:** All colors reference design tokens — `--color-primary-9`, `--color-accent-5`, etc. Theme switching via `applyTheme(LIGHT_THEME)` or `applyTheme(DARK_THEME)`.

**Integration:** `@casehubio/pages-ui-tokens` exports token generation utilities. `@casehubio/pages-viz` consumes tokens for chart theming.

### ConfigurablePanel + DataReceiver Interfaces

New interfaces (added recently) formalize the hosting contract for iframe and non-iframe components.

**Before:** Implicit contract — components expected to have `dataSet` property, but no type enforcement.

**After:** `ConfigurablePanel` + `DataReceiver` — explicit interfaces in `@casehubio/pages-component`. Components implement both to be pipeline-compatible.

**Impact:** Enables static type checking for component registration. Runtime validates interface conformance via `instanceof` before attaching to the pipeline.

### Push Runtime Module

`casehub-pages-push-runtime` (new backend module) — Quarkus CDI producers for the push infrastructure. `PushProducers` creates `@ApplicationScoped` beans for `TopicRegistry`, `EventStore` (configurable `casehub.pages.push.max-events-per-topic`, default 1000), `JsonWriter`, and `EventBroadcaster`. Drop-in dependency for any Quarkus app needing server-push — no boilerplate CDI wiring required.

`EventBroadcaster` — store-and-forward push broadcaster. `broadcast(topic, payload)` appends to `EventStore` (for replay on reconnect), then fans out to all sessions matching the topic via `TopicRegistry.connections()`. Validates no wildcards in broadcast topics. Supports both raw JSON and typed object broadcast (serialized via `JsonWriter`).

### DataSet Manager and Pipeline

`DataSetManager` in `@casehubio/pages-data` — typed dataset management with `get`, `remove`, `has`, `apply` (event-driven updates), `lookup` (with pagination via `rowOffset`/`rowCount`), and `age` (staleness tracking). Lookup resolves filter types against column metadata before applying ops.

`DataSetEvent` — typed event system for dataset mutations (replaces ad-hoc updates).

### TypedDataSet Native

The data model is now fully typed throughout the pipeline: `TypedDataSet`, `TypedRow`, `Column` with `ColumnType` (TEXT, NUMBER, DATE, LABEL), `ColumnId`. Filter expressions carry resolved types from column metadata. Sort operations use `SortColumn` with column reference. The pipeline operates on typed data end-to-end rather than converting at boundaries.

### Async Render Correctness

Generation counter lift, staleness guard, rejection handling for ECharts rendering.

**Problem:** Rapid dataset changes (e.g., live push) could trigger overlapping async renders. Stale render completing after fresh render overwrote correct state.

**Fix:** Each render tagged with generation counter. Render completion checks if counter matches current — if stale, result discarded.

**Refs:** commit `2582b21` — "async render correctness — generation counter lift, staleness guard, rejection handling".

### DataSource Abstraction

Unified data provider interface in `@casehubio/pages-data`. Three core types: `DataSource` (`connect(sink)`/`disconnect()`), `DataSink` (`apply(event)`/`error(err)`), and `MutableDataSource` (extends `DataSource` with `dispatch(action)` for CRUD). `DataAction` union: update/create/delete.

Twelve source implementations: `restSource`, `sseSource`, `wsSource`, `csvSource`, `inlineSource`, `joinSource`, `postMessageSource`, `serverQuerySource`, `composite` (multi-source), `simulated` (with mutation operators: transition/increment/decrement/addRow/removeRow/when), `replay` (recorded event playback), `recording` (captures events for replay).

`SourceFactory` creates sources from configuration. `ScenarioController` provides time-controllable scheduling for demo/scenario playback with play/pause/step/speed controls.

### TypeScript Strict Mode Enforcement

All packages share `@casehubio/pages-tsconfig` with maximum strictness: `strict`, `noUncheckedIndexedAccess` (array/map access yields `T | undefined`), `exactOptionalPropertyTypes` (no implicit `undefined` union), `noImplicitOverride`, `verbatimModuleSyntax`, `isolatedModules`. Applied consistently across all packages via project references.

---

## Depends On

- **Apache ECharts** — charting library
- **JSONata** — data transformation DSL
- **Yarn 4.10.3** — package manager (with workspaces)
- **TypeScript 5** — language
- **React 17** — iframe component framework
- **Webpack 5** — bundler
- **Vitest / Jest** — testing

---

## Depended On By

All CaseHub web applications:
- **casehub-platform** — main application (case management UI)
- **casehub-devtown** — agent development dashboard
- **casehub-clinical** — clinical trials dashboard
- **casehub-aml** — AML investigation dashboard
- **casehub-fsitrading** — trading surveillance dashboard
- **casehub-drafthouse** — legal document drafting UI
- **casehub-life** — life insurance underwriting dashboard

**Integration path:** Each app includes `casehub-pages-*` Java modules in its POM, Quinoa extension for bundling, and a `src/main/webui/` workspace with TypeScript sources.

**Component reuse:** Apps import `@casehubio/blocks-ui-*` components (case timeline, trust score panel, channel activity) and host them via `registerPanel()` + `hostPanel()` in their YAML dashboards.

**blocks-ui dependency:** `casehub-blocks-ui` depends on `@casehubio/pages-primitives` (a11y mixins for focus trap, roving tabindex, live regions) and `@casehubio/pages-table` (data table component). The data table was originally in blocks-ui and migrated to pages as a foundation-tier component.

---

## Build Commands

```bash
# Full build (development)
yarn install && yarn build

# Production build — includes examples gallery
yarn build:prod

# Targeted builds
yarn build:packages       # Shared TypeScript packages only
yarn build:components     # Iframe components only
yarn build:webapp         # Final webapp assembly only
yarn build:examples       # Examples gallery only

# Per-component build
yarn workspace @casehubio/pages-component-echarts run build

# Type checking
yarn typecheck

# Linting
yarn lint

# Examples dev server (port 8080)
yarn workspace @casehubio/pages-examples run serve
```

---

## Testing

```bash
# Run all tests
yarn test

# Run tests for a specific package
yarn workspace @casehubio/pages-data run test
```

**Test organization:**
- Unit tests: `.test.ts` files alongside source
- Integration tests: `examples/` workspace (end-to-end dashboard rendering)

---

## Current State

**Maturity:** Production-ready. Used by 8 CaseHub applications.

**Active development areas:**
- pages-table maturation (row-detail expansion, tree data, CSV export)
- Push runtime CDI integration (EventBroadcaster as drop-in for Quarkus apps)
- pages-primitives a11y infrastructure (focus trap, roving tabindex consumed by pages-table and blocks-ui)
- Data pipeline type safety (TypedDataSet, filter model, dataset manager)
- ECharts component expansion (new chart types)
- Layout persistence (REST API backend)

**Known limitations:**
- SSE push does not support client→server ack (WebSocket only)
- Layout serialization requires explicit `LayoutStore` configuration (no auto-discovery)
- Iframe components cannot access parent window DOM (security isolation)

---

## Protocol Documents

casehub-pages protocols live in `docs/protocols/`:
- `css-tokens.md` — OKLCH token system
- `event-contract.md` — pages-event protocol
- `web-component-strategy.md` — component registration and hosting
- `dataset-contract.md` — DataSet model and operations
- `iframe-component-api.md` — iframe message format and lifecycle

For cross-repo conventions (build order, version alignment, Quinoa integration), see `../garden/docs/protocols/` in the parent repo.
