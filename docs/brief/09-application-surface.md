# The Application Surface

*YAML-declarable interactive experiences — what users see, what agents observe.*

---

## What It Is

The Application Surface is how the platform presents itself to humans
and how agents observe platform state visually. Most enterprise
platforms leave UI as an exercise for the consumer — you get APIs and
build your own frontend. CaseHub ships a complete web framework, a
library of 60 domain-specific components, a data visualisation engine,
a playbook framework for automation, and visual tools for agent
configuration. All of it is declarable in YAML.

This isn't a generic component library. Every component understands the
platform's domain model — trust scores, SLA states, case lifecycle,
speech acts, audit trails, agent identity. A trust-score-panel doesn't
just render a number; it renders a Bayesian Beta gauge with
per-capability breakdown, trend sparklines, and drill-through to the
routing decision that used that score. A work-item-inbox doesn't just
list tasks; it shows SLA countdown, delegation chains, M-of-N quorum
progress, and approval gates with evidence attachments.

Two repos compose to deliver this:
- **Pages** (28 TypeScript packages + 17 Java modules) — the web
  component framework, data pipeline, push infrastructure, playbook
  engine, graph editor, and design token system
- **Blocks UI** (60 Lit web components across 9 packages) — the
  domain-specific components that render case management, trust,
  communication, agent identity, and operational state

---

## Key Capabilities

### Web Component Framework

The Pages framework provides the infrastructure that all CaseHub web
applications share. 28 TypeScript packages covering data pipelines,
event systems, forms, tables, primitives, and component hosting.

The data pipeline architecture is distinctive: YAML-declared dashboards
connect to typed DataSources through a resolution pipeline.
`loadSite()` parses YAML, builds DataSetScope, creates CSS grid
layouts, and wires data pipelines to components. 30+ component types
with full type guards. JSONata data transformation. 14 DataSource
implementations including mutable REST for CRUD operations.

Every CaseHub web application (10+ apps across the platform) consumes
Pages via Quinoa + Maven distribution. Each app includes the Java push
modules in its POM and a `src/main/webui/` workspace with TypeScript
sources — one consistent framework across the entire platform.

### Domain Components Library

60 Lit web components across 9 packages, each rendering a specific
aspect of the platform's domain model:

| Package | Components | What it renders |
|---------|-----------|-----------------|
| **Case lifecycle** | casehub-diagram, swf-diagram, htn-diagram, diagram-workbench, case-flow-viewer, case-dependency-graph, case-explorer | Visual editing + live monitoring of case definitions, SWF workflows, and HTN plans with drill-down navigation |
| **Work & tasks** | work-item-inbox, work-item-detail, work-item-workbench, worker-task-pane, sla-indicator, approval-gate | Full work lifecycle UI with SLA countdown, delegation, M-of-N quorum, approval evidence |
| **Trust & audit** | trust-score-panel, trust-feedback-display, routing-rationale, audit-trail-viewer, trust-workbench, contributor-workbench | End-to-end trust visualisation: score → routing → decision → feedback → Merkle-verified audit |
| **Communication** | channel-activity, conversation-viewer, commitment-viz, notification-inbox | Structured deliberation with speech-act types, epistemic common ground, convergence indicators |
| **Document review** | document-workbench (9 panels: debate-feed, document-diff, review-tracker, context-gauge, brainstorm-options, and more) | Multi-agent document review with streaming debate, side-by-side diff, review point tracking |
| **Agent identity** | agent-catalog, agent-manifest-editor, agent-personality-workbench, agent-profile-panel, avatar-step | Visual agent identity configuration from personality selection through LLM provider setup |
| **Evolution** | evolution-config, evolution-workbench | Gated agent improvement streams with deny/watch patterns, KPI metrics, health monitoring |
| **Operations** | cluster-panel, service-card, topology-viewer, reconciliation-status, dimension-dashboard | Infrastructure visibility — K8s clusters, service health, reconciliation state, topology graphs |
| **Layout** | split-workbench, list-pane, detail-pane, grouped-data-view, session-workbench | Composable panel system where every component works standalone AND embedded via hostPanel |

All components follow a three-tier consumption model: standalone (full
page), panel-hosted (within a workbench), or inline (embedded within
another component's data context). This consistency is enforced through
the `configure()` pattern and the pages hostPanel integration.

### Data Visualisation

15 chart types with a consistent API, typed data contracts, and
platform-aware colour palettes:

Bar, Line, Area, Pie, Scatter, Bubble, Timeseries, Timeline, Heatmap,
Density Heatmap, Treemap, Meter, Metric, Map, Graph.

Plus PagesEventTimeline for temporal event sequences and full statistic
components. All charts support cross-filtering, responsive sizing, and
OKLCH-based theming. The data pipeline connects charts to DataSources
— the same YAML declaration that wires a table to a REST endpoint can
wire a heatmap to an IoTDB time-series source.

### Playbook Framework

Full-stack automation orchestration: YAML playbooks drive both UI
interactions and domain operations in a single declaration.

A playbook can be a test scenario, a demo walkthrough, a tutorial, or
an operational automation. The framework bridges three layers:

- **ARIA walker and executor** (TypeScript) — interacts with the
  rendered UI using accessibility semantics
- **MCP/GraphQL domain resolver** (Java) — `@McpDomain("aria")`
  exposes UI automation as MCP tools, enabling agents to interact
  with dashboards
- **CDI action handlers** (Java) — `@ScenarioAction` pattern lets
  any backend service register as a playbook step handler

Playbooks support hierarchical composition (call graph validation
ensures no cycles), virtual clock for time-controlled execution,
narrative content for tutorial mode, and cross-parser consistency
(YAML is parsed identically by TypeScript and Java runtimes).

The yaml-core step system provides orchestration primitives within
playbooks: select/match, barrier, signal, quorum, deadline,
correlation. A 13-layer DecoratorChain pipeline handles step
execution with deadline tracking and quorum coordination.

### Agent Personality UI

Visual configuration of agent identity — a complete setup workflow
from personality selection through LLM provider configuration:

1. **Agent Catalog** — browse personality templates with featured
   cards, search, and category filtering
2. **Avatar Step** — faceted personality selector with 4 SVG avatar
   collections that map personality traits to visual appearance
3. **Agent Manifest Editor** — configure LLM provider, model,
   credentials, and behavioural parameters
4. **Agent Profile Panel** — display the configured personality
   with capability breakdown

No other UI component library provides this. Agent identity
configuration in competing frameworks means editing JSON or Python
dictionaries. CaseHub makes agent personality a first-class visual
experience.

### Evolution Conductor Dashboard

Operational dashboard for the evolution conductor — the system that
manages gated agent improvement streams:

- **Evolution Config** — deny-pattern-editor, watch-pattern-editor,
  gate-policy-editor for defining improvement guardrails
- **Evolution Workbench** — KPI metrics, active streams, approval
  inbox, audit trail, and health indicators

This is purpose-built for a capability that doesn't exist elsewhere:
structured, gated agent evolution with observability.

### Graph Editing

Domain-agnostic graph editing infrastructure with a stencil grammar
system for creating domain-specific editors:

- **graph-core** — stencil grammar (containment/connection rules with
  cardinality), DomainAdapter for model translation, EditPolicy with
  7 interaction hooks
- **graph-renderer** — ELK layout engine with stack-column and radial
  algorithms, React Flow 12 bridge via Lit web components
- **graph-stencils** — domain-specific stencil packages for case
  definitions, SWF workflows, HTN plans, and org charts

The Lit–React Flow bridge is distinctive: graph editing runs within
the web component ecosystem rather than requiring a separate React
application. Persistence SPI with optimistic concurrency. Runtime
overlays for badges, heatmaps, and status highlights. Multi-diagram
drill-down navigation through the diagram-workbench.

### Push Infrastructure

Durable real-time data delivery with typed wire protocol:

- **WebSocket + SSE push** with topic-based routing via segment-trie
  TopicRegistry (wildcard patterns: `*` single-segment, `#`
  multi-segment)
- **EventStore SPI** with three implementations: InMemory (testing),
  PostgreSQL via JDBC (production), Redis Streams (high-throughput)
- **Store-and-forward replay** — new subscriptions receive last N
  events, so late-joining clients see consistent state
- **ARIA command correlation** — server-side code can execute and
  observe UI operations, enabling the playbook framework to
  bridge frontend and backend

The push protocol is typed (PushMessage builders, PushRequest sealed
parser) and tenant-aware. CDI producers provide drop-in integration
for any Quarkus application — not just Pages apps. The engine and
other backend services use `casehub-pages-push` for real-time data
delivery.

### Design Token System

OKLCH 12-step colour scales with perceptually uniform wide-gamut
colours — the most modern approach to design tokens in any enterprise
platform.

Token categories: colour scales, spacing, typography, elevation,
motion, radius, density. Semantic role tokens map from scale steps,
so a theme only sets a few base values and the entire palette
derives consistently. Dark theme with blue-dominant neutrals. Token
generation CLI for build-time and runtime generation. 22 components
styled exclusively via tokens.

OKLCH ensures consistent contrast ratios across all hue families —
a property that HSL and hex colour systems cannot guarantee. This
matters for accessibility compliance and for rendering trust scores,
SLA states, and severity indicators with perceptually accurate
colour distinctions.

---

## What Makes It Different

**Most enterprise platforms stop at APIs.** Camunda ships a task
list. Temporal ships a web UI for workflow monitoring. Neither ships
a component library, a data visualisation engine, a graph editor, or
visual agent configuration. Consumers build their own frontend from
scratch.

**Generic UI frameworks don't understand the domain.** React
component libraries (MUI, Ant Design, Chakra) provide buttons,
tables, and layout primitives. They know nothing about trust scores,
speech acts, case lifecycles, SLA breach states, or agent
personality. Every consumer rebuilds domain semantics from scratch.

**CaseHub ships both.** 60 domain-specific components that render
platform state with full semantic understanding, on a web framework
designed for YAML-declarable dashboards with typed data pipelines.
The playbook framework bridges UI automation with domain operations
in a way no other tool achieves — a single YAML playbook can drive
both ARIA UI interactions and backend MCP/GraphQL calls.

Three capabilities have no competitor equivalent:
- **Agent Personality UI** — visual agent identity configuration
- **Evolution Conductor Dashboard** — gated agent improvement
  observability
- **Structured Deliberation UI** — conversation-viewer with
  epistemic common ground and convergence detection

---

## How Deep It Goes

**Pages:** 28 TypeScript packages and 17 Java backend modules.
661 TypeScript source files, 137 Java source files. 15 chart types.
14 DataSource implementations. 45+ Zod component schemas for LSP
intelligence. Full LSP server with IntelliJ plugin for IDE-assisted
YAML authoring.

**Blocks UI:** 60 Lit web components across 9 packages. 479
non-test TypeScript source files, 217 test files. Every component
has SSE push support for live updates. Three consumption tiers
(standalone, panel-hosted, inline) across all components.

**Combined:** the Application Surface spans approximately 1,350
source files across 45 packages — a standalone product by any
measure.

---

## What It Gains from the Platform

The Application Surface is not a separate frontend bolted onto
backend APIs. It shares the same data model, the same event system,
and the same push protocol as every backend service.

- **Trust scores** rendered by trust-score-panel are the same
  Bayesian Beta values that the engine uses for routing decisions —
  computed once, consumed everywhere
- **SLA states** shown in sla-indicator are the same breach
  calculations that trigger escalation in the work module — not
  a frontend approximation
- **Case lifecycle events** that update casehub-diagram arrive
  through the same CDI event system that drives backend handlers
- **Push protocol** is the same typed wire protocol used by the
  engine for internal real-time delivery — not a separate WebSocket
  layer for the frontend
- **DataSources** connect directly to platform data providers
  (SQL push-down, IoTDB, Prometheus) without an API translation
  layer — filter/sort/group operations push down to the backend

This eliminates the translation layer between "what the platform
knows" and "what the user sees." There is no API serialisation
gap, no eventual consistency between frontend and backend state,
no separate frontend data model that drifts from the platform
model. The surface renders the platform's actual state.

---

## Connections to Other Areas

- **[Declaration Surface](01-declaration-surface.md)** — the Visual
  Builder creates what the Declaration Surface defines: YAML
  dashboards authored visually, with the composition layer visible
  in the builder
- **[Enterprise Execution](04-enterprise-execution.md)** — work-item
  components render Work module state; case-explorer and diagram
  components render Engine case lifecycle
- **[Accountability & Governance](05-accountability-governance.md)**
  — trust panels, audit-trail-viewer, and routing-rationale render
  Ledger and Qhorus governance state
- **[Agent Identity & Cognition](07-agent-identity-cognition.md)**
  — agent personality UI renders Eidos structured identity; evolution
  conductor renders Engine improvement streams
- **[Convergence & Situational Awareness](06-convergence-situational-awareness.md)**
  — reconciliation-status and topology-viewer render Ops and
  DesiredState convergence state
- **[The Shared Foundation](08-shared-foundation.md)** — Pages push
  infrastructure is shared across the platform; DataSources connect
  to Platform data providers
