# Platform Evolution — Desired State, Situational Awareness, and Declarative Deployment

**Date:** 2026-06-12
**Status:** Research — active design questions, not yet decided
**Scope:** Cross-cutting — spans casehub-desiredstate, casehub-ras, casehub-platform, casehub-engine
**Next step:** Layering decisions before implementation begins on any of the three new layers

---

## 1. What We're Building — The Three New Layers

Three new capabilities emerged from a design session on 2026-06-12. Each is individually useful; together they form a self-governing platform.

### casehub-desiredstate (research project, repos exist)

Generic desired-state management runtime. Declares intent → compiles to dependency graph → executes transition workflows → reconciles continuously against actual state. Domain-agnostic SPIs: `GoalCompiler`, `ActualStateAdapter`, `NodeProvisioner`, `FaultPolicy`, `EventSource`.

Domains in `casehub-ops`: CasehHub agent topology, infrastructure provisioning (Terraform/Ansible augmentation), compliance posture, IoT desired state.

Primary use case: **declarative CasehHub deployment management**. You declare what you want; desiredstate provisions and heals it.

IBM/RHT angle: sits above Ansible/Terraform, adds tamper-evident audit trail + human governance gates + trust-weighted execution. Not a replacement — an accountability layer.

Spec: `casehubio/casehub-desiredstate/docs/superpowers/specs/2026-06-12-casehub-desiredstate-design.md`

### casehub-ras (repo exists, spec exists)

Reticular Activating System — situational awareness and reactive case creation. Monitors `SensoryEvent` streams, routes to pluggable `Ganglion` detection strategies, correlates composite events, triggers `startCase()` when a situation threshold is crossed.

Key design: **the RAS contains no stream infrastructure**. Quarkus/Camel stream modules in casehub-platform produce `SensoryEvent` CDI events; the RAS observes them. Ganglia are the pluggable detection units — Java switch, Drools CEP, Bayesian network, LLM.

Service lifecycle pattern: long-lived service management case → RAS monitors health streams → child cases (incident, upgrade, decommission). The parent case is sparse (WAITING); all activity in RAS detections and child cases.

Spec: `casehubio/casehub-ras/docs/superpowers/specs/2026-06-12-casehub-ras-design.md`

### The Deployment YAML (not yet designed — key open question)

The third layer is the deployment experience: a single YAML that declares the entire state of a CasehHub deployment — streams, RAS instances, situations, agents, channels, trust configuration, connectors.

```yaml
# casehub-deployment.yaml (sketch)

deployment:
  name: clinical-coordination

streams:
  - id: patient-vitals
    source: kafka
    topic: patient.vitals
    streamType: clinical.vitals
    mapping: classpath:streams/vitals-mapping.yaml   # optional Camel route

detection:
  situations:
    - id: patient-deterioration
      watch: [clinical.vitals, clinical.lab]
      window: PT30M
      ganglia:
        - type: drools-cep
          rules: classpath:ras/deterioration.drl
        - type: llm
          prompt: "Does this indicate patient deterioration?"
      chain: AND
      minConfidence: 0.8
      trigger:
        case: patient-escalation
        priority: HIGH

agents:
  - slot: safety-monitor
    count: 2
    provisioner: claudony
    minTrust: 0.70

channels:
  - name: clinical/safety/oversight
    type: oversight
    acl: [safety-monitor]

trust:
  routing: trust-weighted
  minObservations: 20
  fallback: availability-routing

connectors:
  - type: slack
    channel: "#clinical-alerts"
    on: [case.escalated, situation.detected]
```

This is a `casehub-desiredstate` goal declaration — the `DeploymentGoalCompiler` processes it and delegates to each subsystem. The reconciliation loop keeps running state aligned with declared intent.

---

## 2. The Self-Governance Property

CasehHub can govern its own deployment using its own primitives.

- **casehub-desiredstate** manages the CasehHub topology (agent counts, channels, stream sources, RAS instances)
- **casehub-ras** monitors the health of the running CasehHub deployment
- **casehub-engine** orchestrates remediation (upgrade cases, incident cases, decommission cases)

Every change to a CasehHub deployment goes through the same accountability primitives CasehHub provides to its users:
- Who declared this change? (deployment YAML commit)
- Who approved it? (human governance gate — WorkItem)
- Which agent executed it? (NodeProvisioner, trust-weighted)
- What happened? (tamper-evident ledger entry)

This is **recursive accountability** — the governance layer governs itself through itself. No Kubernetes operator, Terraform provider, or GitOps tool has this property. The external story: *"CasehHub is accountable enough to run itself. If you need accountability for agent-driven systems in regulated environments, it's the platform that proved the concept on its own infrastructure."*

The deployment YAML committed to git becomes the compliance record for infrastructure changes. The case history IS the audit trail.

---

## 3. Streams and Data as First-Class Citizens

### What Quarkus/Camel already handles (don't reinvent)

The transport layer is Quarkus. Kafka consumers, AMQP consumers, REST webhook endpoints, Camel routes for data transformation — these are Quarkus doing what Quarkus does best. CasehHub adding abstractions around `@Incoming("topic")` or Camel's 300+ connectors would be noise.

### Where CasehHub genuinely adds value

**`StreamContext` — tenancy in async processing (real gap, belongs in casehub-platform)**

`CurrentPrincipal` is `@RequestScoped`. Quarkus Kafka consumers run outside request context. Every stream consumer currently extracts `tenancyId` manually from message headers — a protocol violation (`PP-20260520-e6a5f0`) at scale. `StreamContext` is the async equivalent of `CurrentPrincipal`: resolved at the stream boundary from message metadata, propagated through the processing chain without call sites touching it directly.

Same placement logic as `CurrentPrincipal` → **casehub-platform-api**.

**Causal audit trail (real gap)**

`message received → ganglion detection → case created` should be tamper-evidently auditable. A `StreamEventLedgerEntry` (extends `LedgerEntry`) written when a `SensoryEvent` triggers a case gives you the full chain, linked via `causedByEntryId`. Quarkus has nothing here.

**Declarative stream topology**

Declaring which streams feed which RAS instances as desired state — managed by casehub-desiredstate. Adding a new data source becomes a configuration change, not a code change. The topology is maintained, not hardcoded.

**Flow control above the transport layer**

Quarkus reactive messaging handles backpressure at the Kafka/AMQP level. Above that — when ganglia are overwhelmed — the policy is a CasehHub concern. A `StreamFlowPolicy` SPI: buffer / drop / sample / rate-limit by `streamType`.

### Platform stream submodules (thin Quarkus wrappers)

These are a few hundred lines each — Quarkus `@Incoming` consumer that fires `Event<SensoryEvent> fireAsync()`. Nothing more.

| Module | Transport |
|---|---|
| `platform-streams-kafka` | Quarkus Kafka reactive messaging |
| `platform-streams-amqp` | Quarkus AMQP |
| `platform-streams-webhook` | Quarkus REST endpoint |
| `platform-streams-poll` | Quarkus `@Scheduled` + REST client |
| `platform-streams-camel` | Apache Camel route → `SensoryEvent` |

Each activates by classpath presence — same pattern as `memory-inmem/`, `memory-jpa/`. The question of where they live is unresolved (see §5).

---

## 4. Layering Analysis

This is the key concern flagged for the next design session. Current thinking on each boundary — none of these are decided.

### casehub-platform-api

**Should contain:**
- `StreamContext` SPI — tenancy in async processing (same rationale as `CurrentPrincipal`)
- Possibly `SensoryEvent` — see critical issue below

**Should NOT contain:**
- Ganglion, RAS types — integration tier concern
- Anything transport-specific

### casehub-platform (submodules)

**Should contain:**
- `platform-streams-*` submodules (Kafka, AMQP, webhook, Camel) — thin wrappers that fire `SensoryEvent`
- `NoOpStreamContext @DefaultBean`

**Open question:** Do platform stream modules live here or in a separate `casehub-streams` repo?
- Argument for here: follows `memory-inmem/`, `memory-jpa/` pattern — classpath-activated adapters for a platform SPI
- Argument for separate: stream infrastructure has different release cadence; more content than memory adapters; a `casehub-streams` repo is independently embeddable without the full platform stack

### casehub-ras-api

**Should contain:**
- `Ganglion` SPI
- `DetectionResult`, `SituationContext`, `SituationDefinition`, `RasTriggerPolicy`
- Possibly `SensoryEvent` — see critical issue below

**Critical layering issue — `SensoryEvent` placement:**

`SensoryEvent` is produced by platform stream modules (foundation tier) and consumed by casehub-ras (integration tier). If `SensoryEvent` lives in `casehub-ras-api` (integration), then platform foundation modules would depend on an integration tier artifact — wrong direction.

Options:
1. `SensoryEvent` moves to `casehub-platform-api` — justifiable if multiple peer repos need it; follows `ActorType`/`CurrentPrincipal` precedent
2. `SensoryEvent` lives in a new `casehub-streams-api` (foundation tier, zero casehubio deps beyond platform-api) — cleanest but adds a new tiny repo
3. `casehub-ras-api` stays integration but platform stream modules are also integration tier — acceptable if platform-streams are not truly foundational

**This must be resolved before any platform stream module is built.**

### casehub-desiredstate

**Should contain:**
- Generic runtime: `DesiredStateGraph`, `TransitionPlanner`, `ReconciliationLoop`, `FaultPolicyEngine`
- Core SPIs: `GoalCompiler`, `ActualStateAdapter`, `NodeProvisioner`, `FaultPolicy`, `EventSource`

**Open question: Does the deployment YAML compiler live here?**

The full deployment YAML (agents + streams + RAS + channels + trust + connectors) is processed by a `DeploymentGoalCompiler`. Options:
1. In `casehub-desiredstate` as the primary `GoalCompiler` implementation — clean, single entry point
2. In `casehub-ops/deployment` module — it's a domain implementation of the generic runtime
3. In a new `casehub-deploy` module — higher-level orchestrator above desiredstate

Argument for option 2: the deployment compiler delegates subsections to sub-compilers (streams → platform, RAS → casehub-ras, agents → claudony/openclaw). This is a domain, not the generic runtime.

### casehub-ras

**Should contain:**
- `RasEngine` — observes `SensoryEvent`, routes to ganglia
- `CompositeEventCorrelator`, `SituationAccumulator`, `CaseTriggerService`
- `DroolsGanglion` (optional module), `LlmGanglion` (optional module)

**Should NOT contain:**
- Any stream transport (Kafka, AMQP, Camel)
- `SensoryEvent` definition (see critical issue above)

### casehub-engine

**Should NOT know about:**
- casehub-ras directly
- casehub-desiredstate directly

**How cases get created from RAS:** `CaseTriggerService` in casehub-ras calls `casehub-engine-api` `startCase()`. Engine is not aware of the RAS — it just receives a case start request. Correct.

**How desiredstate executes workflows:** delegates to `casehub-engine-flow`. Engine is not aware of desiredstate. Correct.

---

## 5. Open Questions — Prioritised

These must be answered before implementation begins:

**P0 — Blocks everything:**

1. **`SensoryEvent` placement** — casehub-platform-api, casehub-ras-api (integration-only), or new casehub-streams-api? Dependency direction is the constraint. Decide before building any platform stream module.

2. **Platform stream module home** — submodules of casehub-platform, or separate `casehub-streams` repo? Affects build order, release cadence, and dependency graph.

**P1 — Blocks deployment UX:**

3. **Deployment YAML compiler placement** — in casehub-desiredstate runtime, casehub-ops/deployment, or new casehub-deploy? Affects how the deployment YAML is processed and which modules need to know about each other.

4. **Quarkus build-time constraint** — Quarkus extensions are configured at build time, not runtime. Can the deployment YAML wire stream sources at runtime, or do stream module configurations (Kafka topics, etc.) need to be in `application.properties`? If the latter, the deployment YAML declares intent but Quarkus configuration is separate — acceptable but degrades the UX.

**P2 — Blocks RAS implementation:**

5. **`SituationStore` persistence** — in-memory for prototype; JPA for durable correlation across restarts. Retention policy for expired situations?

6. **Drools CEP session model** — stateful KieSession per situation (safer, more expensive) or shared session with tenant isolation?

7. **Ganglion-as-case pattern** — optional or first-class? If first-class, the `Ganglion` SPI needs to accommodate both CDI bean and case-backed implementations from the start.

**P3 — Platform/architecture:**

8. **`StreamContext` SPI contract** — how does `tenancyId` flow from a Kafka message header through the async CDI event to the RAS and ledger entries? Who extracts it? When?

9. **`StreamEventLedgerEntry` home** — in casehub-ras (most natural), casehub-ledger (where all ledger subclasses live), or a bridge module?

10. **Self-governance bootstrap problem** — if casehub-desiredstate manages the CasehHub deployment, who manages casehub-desiredstate itself during first deployment? Classic chicken-and-egg. Likely: first deployment is imperative; subsequent changes are declarative.

---

## 6. Relationship to Existing Platform

```
What exists today                     What's being added
─────────────────────────────────     ──────────────────────────────────────────
casehub-platform (SPIs)          ←→   + StreamContext SPI
                                       + platform-streams-* submodules (Kafka, Camel...)

casehub-ledger (audit)           ←→   + StreamEventLedgerEntry

casehub-engine (orchestration)   ←←   casehub-desiredstate (delegates workflow to engine-flow)
                                       casehub-ras (calls startCase() via engine-api)

casehub-iot (IoT devices)        →    SensoryEvent adapter (iot StateChangeEvent → SensoryEvent)

casehub-qhorus (messaging)       →    SensoryEvent adapter (MessageReceivedEvent → SensoryEvent)

casehub-connectors (outbound)    →    SensoryEvent adapter (InboundMessage → SensoryEvent)

claudony (agent provisioner)     ←←   casehub-desiredstate ClaudonyNodeProvisioner
```

Nothing in the existing platform needs to change. The new layers consume existing SPIs via the existing dependency direction.

---

## 7. The Full Architecture (When Complete)

```
Developer declares:
  casehub-deployment.yaml
         │
         ▼
casehub-desiredstate
  DeploymentGoalCompiler
  ├── provision agents          → claudony/openclaw
  ├── provision channels        → casehub-qhorus
  ├── provision stream sources  → platform-streams-kafka/camel/webhook
  ├── provision RAS instances   → casehub-ras RasEngine
  └── provision case types      → casehub-engine

Runtime:
  External events
    → platform-streams-* (Quarkus/Camel)
      → SensoryEvent CDI fireAsync()
        → casehub-ras RasEngine
          → Ganglion implementations (CDI beans or cases)
            → DetectionResult accumulation
              → CompositeEventCorrelator
                → SituationThreshold crossed
                  → CaseTriggerService → startCase()
                    → casehub-engine case execution
                      → human gates, agent routing, ledger audit

Self-governance loop:
  casehub-ras monitors the casehub-desiredstate deployment itself
  → service down → IncidentCase
  → drift detected → ReconciliationCase
  → upgrade available → UpgradeCase
  → decommission intent → DecommissionCase (closes ServiceLifecycleCase with SUCCESS)
```

---

## 8. What Makes This Positioning Distinct

| Capability | Terraform | Kubernetes | ArgoCD | CasehHub |
|---|---|---|---|---|
| Declarative desired state | ✅ | ✅ | ✅ | ✅ |
| Continuous reconciliation | ❌ | ✅ | ✅ | ✅ |
| Human governance gates | ❌ | ❌ | ❌ | ✅ |
| Tamper-evident audit trail | ❌ | ❌ | ❌ | ✅ |
| Trust-weighted execution | ❌ | ❌ | ❌ | ✅ |
| Reactive case creation (RAS) | ❌ | Partial (operators) | ❌ | ✅ |
| Self-governed via own primitives | ❌ | ❌ | ❌ | ✅ |
| Agent-native | ❌ | ❌ | ❌ | ✅ |

The differentiator is not any single capability — it's the combination. Declarative + accountable + agent-native + self-governing is a position no existing tool occupies.
