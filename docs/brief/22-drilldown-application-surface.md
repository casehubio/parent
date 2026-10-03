# Drill-Down: The Application Surface

*Two repos, 45 packages, 1,350 source files — the web framework and
domain component library that render the platform.*

---

## Architecture Overview

The Application Surface is delivered by two repos: **Pages** (28
TypeScript packages + 17 Java backend modules) provides the web
component framework, data pipeline, push infrastructure, playbook
engine, graph editor, and design token system. **Blocks UI** (60 Lit
web components across 9 packages) provides domain-specific
components that render case management, trust, communication, agent
identity, and operational state.

Every CaseHub web application (10+ across the platform) consumes
Pages via Quinoa + Maven SNAPSHOT distribution. Each app includes
Java push modules in its POM and a `src/main/webui/` workspace with
TypeScript sources. `.casehub-packages/` resolves local package
dependencies. One framework, one distribution model, one component
lifecycle across the entire platform.

The data pipeline flows: YAML dashboard declaration → `loadSite()`
parser → DataSetScope construction → CSS grid layout → DataSource
wiring → component rendering. Components subscribe to typed
DataSources. DataSources connect to backend data providers (REST,
SQL with push-down, IoTDB, Prometheus). Cross-filter state management
propagates user interactions across the dashboard.

---

## SPI Contracts

### Data Pipeline

| Interface | Package | Purpose |
|-----------|---------|---------|
| `DataSource` | `pages-data` | Typed data provider abstraction. 14 implementations: REST (mutable + immutable), static, derived, filtered, grouped, sorted, paginated, aggregated, merged, SQL push-down, IoTDB, Prometheus, WebSocket stream. |
| `DataSetScope` | `pages-data` | Scoped data context — components within a scope share DataSources and cross-filter state. |
| `DataTransformer` | `pages-data` | JSONata transformation pipeline. Declarable in YAML. Chains with DataSource output. |

### Component Hosting

| Interface | Package | Purpose |
|-----------|---------|---------|
| `hostPanel` | `pages-host` | Panel hosting contract — three consumption tiers: standalone (full page), panel-hosted (within workbench), inline (embedded in data context). |
| `configure()` | `pages-component` | Initialization pattern — every Blocks UI component exposes a `configure()` method for host integration. Consistent across all 60 components. |
| `DataSourceMixin` | `pages-data` | Lit mixin providing DataSource connectivity to any web component. Handles subscription lifecycle, error isolation, and teardown. |
| `PushMixin` | `pages-push` | Lit mixin providing push protocol connectivity. SSE reconnect awareness. Topic subscription management. |

### Push Infrastructure

| Interface | Package | Purpose |
|-----------|---------|---------|
| `TopicRegistry` | `pages-push-api` | Segment-trie topic routing with wildcard patterns: `*` (single segment), `#` (multi-segment). |
| `EventStore` | `pages-push-api` | Durable event storage SPI. InMemory (testing), PostgreSQL/JDBC (production), Redis Streams (high-throughput). |
| `EventBroadcaster` | `pages-push-core` | Store-and-forward: new subscriptions replay last N events. Typed `PushMessage` builders. Sealed `PushRequest` parser. |

### Playbook Framework

| Interface | Package | Purpose |
|-----------|---------|---------|
| `@ScenarioAction` | `pages-scenario` | CDI pattern for backend step handlers. Any service registers as a playbook step handler. |
| `StepRunner` | `pages-yaml-core` | Step execution with `DeadlineContext` and `QuorumTracker`. 13-layer `DecoratorChain` pipeline. |
| `Portability` | `pages-yaml-core` | Cross-runtime validation: `universal`, `java`, `ts`, `both`. Actions declare supported runtimes; system validates before execution. |
| `@McpDomain("aria")` | `pages-mcp` | MCP/GraphQL domain resolver exposing UI automation as MCP tools. Agents interact with dashboards. |

### Graph Editing

| Interface | Package | Purpose |
|-----------|---------|---------|
| `StencilGrammar` | `pages-graph-core` | Containment/connection rules with cardinality constraints. Domain-specific editor grammars. |
| `DomainAdapter<T>` | `pages-graph-core` | Model translation between graph nodes and domain objects. Typed generics. |
| `EditPolicy` | `pages-graph-core` | 7 interaction hooks for domain-controlled editing behaviour. |
| `PersistenceSPI` | `pages-graph-core` | Optimistic concurrency. `GitHubBackend` implementation for version-controlled diagram storage. |

### Design Tokens

| Interface | Package | Purpose |
|-----------|---------|---------|
| `TokenPipeline` | `pages-ui-tokens` | OKLCH 12-step colour scale generation. Token categories: colour, spacing, typography, elevation, motion, radius, density. |
| `ThemePicker` | `pages-ui-tokens` | Theme selection web component. Pluggable pipeline with transforms and presets. |

---

## Data Model

### YAML Dashboard Declaration

```yaml
site:
  title: Operations Dashboard
  layout:
    columns: 3
    rows: auto
  datasets:
    incidents:
      source: rest
      url: /api/incidents
      transform: "$.data[status='OPEN']"
    metrics:
      source: iotdb
      query: "SELECT avg(cpu) FROM devices GROUP BY 1h"
  components:
    - type: timeseries
      dataset: metrics
      position: {col: 1, row: 1, span: 2}
    - type: table
      dataset: incidents
      position: {col: 3, row: 1}
```

`loadSite()` parses this into a typed `SiteModel`, builds
`DataSetScope`, creates CSS grid layout, wires DataSources to
components. 30+ component types with full type guards.

### Blocks UI Component Taxonomy

| Package | Components | Domain model rendered |
|---------|-----------|---------------------|
| Case lifecycle | 7 | `CaseDefinition`, `CasePlanModel`, SWF workflows, HTN plans. Visual editing + runtime overlay. |
| Work & tasks | 6 | `WorkItem`, `SlaState`, `ApprovalGate`, `DelegationChain`. SLA countdown, M-of-N quorum. |
| Trust & audit | 6 | `TrustScore` (Bayesian Beta), `RoutingRationale`, `MerkleChain` verification. Score → routing → audit. |
| Communication | 4 + dozens of sub-elements | `Channel`, `SpeechAct`, `Commitment` (7 states), `Conversation` with convergence. |
| Document review | 9 panels | `DebateEntry` (18 types), `ReviewPoint`, `AgentRole` (6 roles), brainstorm convergence. |
| Agent identity | 5 + 2 avatar packages | `AgentDescriptor` 4-layer model, personality selection, LLM config, avatar generation. |
| Evolution | 2 | `EvolutionStream`, deny/watch patterns, gate policies, KPI metrics. |
| Operations | 5 | K8s clusters, service topology, `ReconciliationStatus`, `DimensionDashboard`. |
| Layout | 6 | `SplitWorkbench` (draggable), `CaseExplorer` (entity browser), session management. |

### Push Wire Protocol

```
PushMessage (typed builders)
├── DataUpdate    — component data change
├── Notification  — user notification
├── Command       — ARIA command execution
└── Correlation   — command result correlation

PushRequest (sealed parser)
├── Subscribe     — topic + replay count
├── Unsubscribe   — topic release
└── Acknowledge   — delivery confirmation
```

WebSocket + SSE transports. Topic routing via segment-trie. CDI
producers for drop-in Quarkus integration — not limited to Pages
apps. The engine and other backend services use `casehub-pages-push`
for real-time data delivery.

---

## Runtime Behaviour

### Data Pipeline Execution

1. `loadSite()` parses YAML site definition
2. DataSources instantiated per the `datasets` section — type
   determines provider (REST, SQL, IoTDB, Prometheus, static)
3. `DataTransformer` applies JSONata expressions to DataSource output
4. `DataSetScope` created — components within scope share data and
   cross-filter state
5. CSS grid layout computed from `position` declarations
6. Components rendered — each receives typed data via
   `DataSourceMixin` subscription
7. User interactions (filter, sort, select) propagate through
   cross-filter state management to all components in scope
8. For SQL push-down sources: filter/sort/group operations serialise
   to the backend and translate to native SQL — large datasets
   processed server-side

### Playbook Execution

1. YAML playbook parsed (cross-parser consistency: TS and Java
   parsers produce identical models)
2. Call graph validated — hierarchical composition with cycle
   detection
3. `StepRunner` executes steps through 13-layer `DecoratorChain`:
   deadline tracking, quorum coordination, error isolation
4. For UI steps: ARIA walker traverses rendered DOM using
   accessibility semantics — `aria-label`, roles, states
5. For backend steps: `@ScenarioAction` CDI handlers execute domain
   operations
6. For agent steps: `@McpDomain("aria")` resolver exposes UI state
   as MCP tools — agents observe and interact with dashboards
7. Virtual clock controls temporal execution — fast-forward through
   time-dependent scenarios
8. Narrative content renders tutorial overlays for interactive
   learning mode

### Graph Editor Lifecycle

1. `StencilGrammar` loaded for target domain (case, SWF, HTN, org)
2. `DomainAdapter<T>` translates domain model to graph nodes
3. ELK layout engine computes positions (stack-column, radial,
   hierarchical algorithms)
4. React Flow 12 renders via Lit web component bridge
5. `EditPolicy` 7 hooks govern interactions: canAdd, canRemove,
   canConnect, canMove, canSplit, canSplice, canResize
6. Mutations applied to immutable model (add/remove/split/splice)
7. `PersistenceSPI` saves with optimistic concurrency (ETag-based)
8. Runtime overlays render badges, heatmaps, status highlights on
   live instances

---

## Extension Points

| Extension | How to add |
|-----------|-----------|
| New DataSource type | Implement `DataSource` interface, register provider. Available in YAML `datasets` declarations. |
| New chart type | Add component to pages-chart package, register type guard, provide Zod schema for LSP intelligence. |
| New Blocks UI component | Create Lit component with `configure()` pattern, `DataSourceMixin`/`PushMixin` as needed. Three-tier consumption automatic. |
| New graph stencil domain | Define `StencilGrammar` with containment/connection rules. Implement `DomainAdapter<T>` for model translation. |
| New playbook step | Annotate CDI bean method with `@ScenarioAction`. Automatically available in YAML playbooks. |
| New push EventStore | Implement `EventStore` SPI. InMemory, PostgreSQL, Redis exist. New backends (e.g. Kafka) follow the same contract. |
| New design theme | Set base OKLCH values in theme definition. 12-step scale derives automatically. Semantic role tokens map from scale steps. |
| New composable facet | Implement `Facet` SPI with MCP tools, artifacts, and state. Facets compose independently (e.g. voice auto-activates notes). |

---

## Module Map

### Pages (28 TS + 17 Java)

| Module | What it provides | Key types |
|--------|-----------------|-----------|
| `pages-data` | DataSource pipeline, 14 implementations | `DataSource`, `DataSetScope`, `DataTransformer` |
| `pages-chart` | 15 chart types | Bar, Line, Timeseries, Heatmap, Treemap, Meter, etc. |
| `pages-table` | Virtual-scroll data table | Cell spanning, tree data, grouped views |
| `pages-form` | Schema-driven forms | Nested objects, arrays, `$ref` resolution |
| `pages-yaml-core` | YAML composition engine | `VariableResolver`, `ForEachExpander`, `YamlModule`, `StepRunner` |
| `pages-graph-core` | Graph editing infrastructure | `StencilGrammar`, `DomainAdapter<T>`, `EditPolicy` |
| `pages-graph-renderer` | ELK layout + React Flow bridge | Stack-column, radial layouts, runtime overlays |
| `pages-aria` | ARIA UI automation (40 TS files) | Walker, executor, scheduler, tutorial host |
| `pages-scenario` | Scenario compilation (25 Java files) | Model, compiler, call graph validator |
| `pages-push` | Push infrastructure (4 Java modules) | `TopicRegistry`, `EventStore`, `EventBroadcaster` |
| `pages-ui-tokens` | OKLCH design token system | Token generation CLI, theme pipeline, 22 styled components |
| `pages-schema` | 45+ Zod component schemas | LSP intelligence, type-aware completions and diagnostics |
| `pages-lsp` | LSP server (Node.js) | Completion, diagnostics, hover, refactoring, jq expression intelligence |
| `pages-mcp` | MCP/GraphQL ARIA resolver | `@McpDomain("aria")` — UI automation as MCP tools |
| `pages-builder` | Visual builder (pre-alpha) | Component catalog, property palette, document model |

### Blocks UI (60 components, 9 packages)

| Package | Count | Key components |
|---------|-------|---------------|
| `casehub-case` | 7 | casehub-diagram, swf-diagram, htn-diagram, diagram-workbench, case-explorer |
| `casehub-work` | 6 | work-item-inbox, work-item-workbench, approval-gate, sla-indicator |
| `casehub-trust` | 6 | trust-score-panel, routing-rationale, audit-trail-viewer, trust-workbench |
| `casehub-comms` | 4 | channel-activity (12 sub-elements), conversation-viewer, commitment-viz, notification-inbox |
| `casehub-review` | 9 | document-workbench: debate-feed, document-diff, review-tracker, context-gauge, brainstorm-options |
| `casehub-agent` | 5+2 | agent-personality-workbench, agent-catalog, avatar-step, agent-avatar-2d (4 SVG collections) |
| `casehub-evolution` | 2 | evolution-config (deny/watch/gate editors), evolution-workbench (KPI, streams, inbox) |
| `casehub-ops` | 5 | cluster-panel, topology-viewer, reconciliation-status, dimension-dashboard |
| `casehub-layout` | 6 | split-workbench, list-pane, detail-pane, case-explorer, session-workbench |
