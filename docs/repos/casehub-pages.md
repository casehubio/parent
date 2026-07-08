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
| `@casehubio/pages-data` | DataSet model, operations engine, external data extraction, JSONata. Push wire protocol (`EventConnection`, `PushSource`, `WebSocketSource`). General-purpose `SSEManager` (connection pooling, named event support, reconnection). |
| `@casehubio/pages-ui` | YAML parser, DashBuilder backward compat layer, component model. |
| `@casehubio/pages-viz` | Web Component chart/table/metric wrappers (ECharts integration). |
| `@casehubio/pages-component` | CSS grid layout renderer, interactive containers, panel hosting. Exports `ConfigurablePanel` and `DataReceiver` interfaces for hosted components. |
| `@casehubio/pages-runtime` | Site orchestrator: `loadSite()` API, navigation, data pipeline, layout serialization (`LayoutStore`, `createLocalLayoutStore`). |
| `@casehubio/pages-tsconfig` | Shared TypeScript config base (project references, strict mode). |
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
| `casehub-pages-push` | Typed wire protocol SDK: `PushMessage` (server→client builders), `PushRequest` (sealed client→server parser with ack/error correlation), `TopicRegistry` (wildcard-aware connection tracking), `EventStore` SPI + `InMemoryEventStore` (bounded per-topic event replay). jackson-core only, no Quarkus. |
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

**Capacity:** configurable per-topic, defaults to 100 events.

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

### Removal of pages-primitives

`@casehubio/pages-primitives` removed — `casehub-blocks-ui` is now the canonical source for shared UI components (case timelines, trust score panels, channel activity feeds).

**Migration:** applications importing `@casehubio/pages-primitives` components now import from `@casehubio/blocks-ui-core` instead. All primitives (schema forms, filter chips, scope selector) migrated to blocks-ui.

**Reason:** blocks-ui components are domain-aware (trust scores, case lifecycles) but app-agnostic. Primitives were too generic to be useful — better to compose from casehub-pages core APIs (`ConfigurablePanel`, `DataReceiver`, `pages-event`).

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

### Async Render Correctness

Generation counter lift, staleness guard, rejection handling for ECharts rendering.

**Problem:** Rapid dataset changes (e.g., live push) could trigger overlapping async renders. Stale render completing after fresh render overwrote correct state.

**Fix:** Each render tagged with generation counter. Render completion checks if counter matches current — if stale, result discarded.

**Refs:** commit `2582b21` — "async render correctness — generation counter lift, staleness guard, rejection handling".

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
- Push protocol maturation (topic wildcard patterns, event replay)
- ECharts component expansion (new chart types)
- Layout persistence (REST API backend)
- Design token refinement (OKLCH scale tuning)

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
