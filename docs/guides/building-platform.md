# Building Platform

> **Audience:** Platform contributors extending foundation repos
> **Scope:** Navigation, boundary rules, SPI design, capability addition checklist
> **See also:** [Building Apps](building-apps.md) for app-tier development

This is the lighter companion to building-apps.md. If you're extending casehub-platform, ledger, work, qhorus, engine, eidos, neocortex, connectors, workers, iot, ras, desiredstate, blocks, blocks-ui, pages, or openclaw — this is your entry point.

---

## Architecture

Start here to understand the tier structure and patterns in use across the platform.

- **[ARCHITECTURE.md](../ARCHITECTURE.md)** — architectural patterns (Hexagonal, DDD, Event-Driven, CQRS-lite), dependency rule, selective event sourcing
- **[platform/overview.md](../platform/overview.md)** — tier structure, repository map, build order, Serverless Workflow 1.0 alignment

The dependency rule shapes everything: **source code dependencies may only point inward. Domain logic never depends on infrastructure.** This is enforced by the three-tier module structure (SPI / core / extension).

---

## Boundary Rules

Before adding a capability, check what must NOT be placed where.

- **[platform/boundary-rules.md](../platform/boundary-rules.md)** — all cross-repo "do not" rules (orchestration in engine not work, trust in ledger not engine, notification infrastructure in connectors, etc.)
- **[platform/overlap-risks.md](../platform/overlap-risks.md)** — known semantic collisions (EventLog vs CaseLedgerEntry, CommitmentState.DELEGATED vs WorkItemStatus.DELEGATED) and known placement violations

Read boundary-rules.md before designing any new feature. The rules prevent semantic drift and duplication across repos.

---

## SPI Design Conventions

When adding a new SPI or extending an existing one, follow these patterns:

### API Interface Taxonomy

[`api-interface-taxonomy`](https://github.com/casehubio/garden/blob/main/docs/protocols/casehub/api-interface-taxonomy.md) protocol — four categories of `api/` interfaces:
1. **Store** — data access SPIs (`CaseInstanceRepository`, `EventLogRepository`)
2. **SPI** — pluggable extension points (`WorkerProvisioner`, `RoutingStrategy`)
3. **Gateway** — outbound integration ports (`Connector`, `NotificationDeliveryProvider`)
4. **Service Facade** — cross-aggregate read views (`QhorusDashboardService`)

Each has different placement rules and consumer expectations. The protocol includes a decision flowchart.

### Module Tier Structure

[`module-tier-structure`](https://github.com/casehubio/garden/blob/main/docs/protocols/universal/module-tier-structure.md) protocol — the three-tier rule:
1. **Pure-Java SPI tier** (`api/`) — no Quarkus, no JPA, no reactive types in SPI signatures
2. **Core library tier** — domain logic, no JPA annotations, may use reactive types internally
3. **Full extension tier** — Panache entities, CDI beans, REST resources

REST adapters must live in a separate module ([`rest-adapter-module`](https://github.com/casehubio/garden/blob/main/docs/protocols/universal/rest-adapter-module.md) protocol) — never in the core library runtime.

### DSL Design

- **[DSL-STYLE-GUIDE.md](../DSL-STYLE-GUIDE.md)** — fluent API conventions (pattern-named builders, three-way expression overloads, static factory imports for vocabulary)

New builder APIs should follow the LangChain4j + Quarkus Flow + CaseHub blended style documented here.

---

## Adding a New Capability

When adding a platform capability (not an app feature), follow this checklist:

1. **Check INDEX.md** — does this capability already exist under a different name? Check [INDEX.md](../INDEX.md) and [platform/capability-ownership.md](../platform/capability-ownership.md) before creating a new module or SPI.

2. **Decide repo ownership** — does this belong in an existing repo, or does it need a new one? Guidance:
   - **Existing repo** if it extends an existing concern (new routing strategy → engine, new connector type → connectors, new memory backend → neocortex)
   - **New repo** if it's a new foundation concern with no natural home (iot was a new repo; pages was a new repo)
   - **Application repo** if it requires domain knowledge (software dev, clinical trials, financial crime)

3. **Follow module-tier-structure** — create `api/`, `core/`, `runtime/` (or `deployment/`) modules per the protocol. The SPI must be pure Java with zero infrastructure dependencies.

4. **Update INDEX.md** — add an entry under the correct concern section. Include: capability name, one-line description, link to deep-dive, relevant protocols.

5. **Update building-apps.md if app-facing** — if app builders will interact with this capability, add it to the capability matrix and pattern catalogue in [guides/building-apps.md](building-apps.md).

6. **Document in a deep-dive** — create or update `docs/repos/<repo-name>.md` with the new capability's SPI contracts, module structure, and usage patterns.

---

## Cross-Cutting Concerns

All platform builders must know the cross-cutting rules. These apply regardless of which repo you're working in.

| Concern | Where |
|---------|-------|
| Persistence | [platform/persistence.md](../platform/persistence.md) — Flyway conventions, datasource naming, migration path scoping |
| Auth | [platform/auth.md](../platform/auth.md) — gateway topology, roles, outbound credentials |
| Notifications | [platform/notifications.md](../platform/notifications.md) — subscription engine, delivery pipeline, digest batching |
| Observability | [platform/observability.md](../platform/observability.md) — OTel tracing, audit trail, ledger correlation |
| Privacy | [platform/privacy.md](../platform/privacy.md) — GDPR erasure, PII sanitization |
| Agent Identity | [platform/agent-identity.md](../platform/agent-identity.md) — DID format, SCIM2, versioning |
| Agent Mesh | [platform/agent-mesh.md](../platform/agent-mesh.md) — 3-channel normative layout, mesh participation |
| Routing | [platform/routing.md](../platform/routing.md) — trust-weighted, semantic, CBR-evidence agent selection |
| CBR | [platform/cbr.md](../platform/cbr.md) — case-based reasoning capability map |
| UI Architecture | [platform/ui-architecture.md](../platform/ui-architecture.md) — pages → blocks-ui → app UI layering |

---

## Pre-Implementation Protocol

Before implementing any change to foundation or orchestration repos, run the coherence protocol:

- **[platform/coherence-protocol.md](../platform/coherence-protocol.md)** — 6-step pre-implementation protocol (Step 1: check boundary rules, Step 2: check ownership, Step 3: check for existing SPI, Step 4: choose placement, Step 5: doc impact, Step 6: verify)

This is not optional. It prevents duplication, placement violations, and semantic drift.

---

## Operational Artifacts

| Artifact | What it does |
|----------|-------------|
| [platform/capability-ownership.md](../platform/capability-ownership.md) | "Where does X live?" lookup table |
| [platform/dependency-map.md](../platform/dependency-map.md) | Cross-repo impact analysis for renames, removals, SPI breaks |
| [platform/protocols.md](../platform/protocols.md) | Protocol summary, audience mapping |

---

## All Protocols

Platform builders must know all protocols (not just the app-builder subset). Full catalogue:

### CaseHub Foundation Protocols

- [`api-interface-taxonomy`](https://github.com/casehubio/garden/blob/main/docs/protocols/casehub/api-interface-taxonomy.md) — Four categories of `api/` interfaces with placement rules
- [`routing-strategy-convention`](https://github.com/casehubio/garden/blob/main/docs/protocols/casehub/routing-strategy-convention.md) — Per-case selectable strategies extend `NamedStrategy`, declare `id()`, ship `@DefaultBean` default

### Universal Protocols

- [`module-tier-structure`](https://github.com/casehubio/garden/blob/main/docs/protocols/universal/module-tier-structure.md) — Three-tier rule: pure-Java SPI / core library (no JPA) / full extension
- [`rest-adapter-module`](https://github.com/casehubio/garden/blob/main/docs/protocols/universal/rest-adapter-module.md) — REST layer in a separate opt-in module — never in core library runtime

### Web Protocols

- [`lit-immutable-collections`](https://github.com/casehubio/garden/blob/main/docs/protocols/web/lit-immutable-collections.md) — Replace reactive collections on every mutation — never mutate in place
- [`custom-event-shadow-dom`](https://github.com/casehubio/garden/blob/main/docs/protocols/web/custom-event-shadow-dom.md) — CustomEvents crossing shadow DOM need both `bubbles: true` and `composed: true`

Full protocol index: [garden protocols INDEX.md](https://github.com/casehubio/garden/blob/main/docs/protocols/INDEX.md)

---

## Application Impact

When your platform change affects app builders:

1. **Update building-apps.md** — add the capability to the capability matrix and pattern catalogue
2. **Update INDEX.md** — add the capability to the discovery index under the correct concern
3. **Update the relevant topic chunk** — if your change touches persistence, auth, notifications, etc., update the corresponding `platform/*.md` file

**The rule:** if an app builder needs to know about your change to use the platform correctly, it must be documented in building-apps.md before the PR merges.

---

## Tools and Conventions

- **Config Architecture** — [config-architecture.md](../config-architecture.md) — topic ownership map showing what's authoritative where
- **New Repo Checklist** — [new-repo-checklist.md](../new-repo-checklist.md) — setup steps for adding a new repository
- **Prompt Snippets** — [prompt-snippets.md](../prompt-snippets.md) — work-item opening sequences, doc-sync reminders
- **arc42stories** — [arc42stories-spec.md](../arc42stories-spec.md) | [profile](../arc42stories-casehub-profile.md) | [README](../arc42stories-readme.md) — standard architecture documentation format

---

## Lifecycle Management

- **Channels** — [CHANNELS.md](../CHANNELS.md) — purpose categories, discriminator dimensions
- **Lifecycle** — [LIFECYCLE.md](../LIFECYCLE.md) — state machines, terminal semantics

---

## Next Steps

- **Starting an app?** Read [guides/building-apps.md](building-apps.md) instead
- **Extending the platform?** Load INDEX.md, find your concern, follow the links
- **Pre-implementation?** Run [platform/coherence-protocol.md](../platform/coherence-protocol.md)
