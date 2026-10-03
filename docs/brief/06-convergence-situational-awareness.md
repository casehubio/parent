# Convergence & Situational Awareness

*The loop no competitor closes.*

Automation that can't detect drift, trigger corrective action, and
reconcile toward a desired state is just a script with extra steps.
CaseHub closes the loop: declare what should be true, detect when
reality diverges, learn from every correction.

This is the Convergence → Operations arc — the feedback loop that makes
the lifecycle spine a cycle, not a line.

---

## The Problem

Kubernetes reconciliation works — for infrastructure. Terraform
plan/apply works — for provisioning. Neither handles arbitrary business
domains. Neither involves humans. Neither learns from failures.

When a clinical trial protocol drifts from its declared parameters, you
don't need a Kubernetes controller — you need domain-agnostic
reconciliation with human approval gates, fault policies that escalate
intelligently, and a learning loop that makes recovery better each time.

When a fleet of IoT devices reports anomalous readings, you don't need
a static threshold alert — you need composable signal detection that
can watch for patterns across situations, measure its own recall, and
adjust when it's missing events.

CaseHub provides both — and proves the model works by running the
platform against itself.

---

## Desired-State Reconciliation

Declare a graph of desired state. The engine observes actual state,
computes the delta, and drives reality toward the declaration —
continuously, not once.

Unlike Kubernetes controllers (infrastructure-only, fully automated),
CaseHub reconciliation is:

- **Domain-agnostic.** The same engine reconciles deployment topologies,
  compliance controls, container environments, organisational
  structures, and IoT device fleets. Each domain implements the same
  SPI quad (GoalCompiler, NodeProvisioner, ActualStateAdapter,
  FaultPolicy) — consistent operations across any problem space.

- **Human-in-the-loop.** Per-action gating controls which transitions
  require human approval: provision-only, deprovision-only, all, or
  none. Approval gates create work items through the same human task
  system used elsewhere on the platform.

- **Lifecycle-aware.** Multi-phase deployments carry a sequence of
  graphs with completion conditions. The LifecycleManager orchestrates
  phase transitions with dual CAS for concurrent safety.
  SituationRecompilers can replace the entire lifecycle mid-execution
  when conditions change.

**Extent:** 37 modules, 566 Java source files. ReconciliationLoop with
per-tenant event-driven + periodic resync, per-NodeType scheduling,
debounced event processing, OTel tracing. TransitionPlanner with Kahn's
topological sort (prune-before-grow), orphan spec resolution.
Parallel execution on virtual threads with per-NodeType semaphore rate
limiting. Dual-framework deployment (Quarkus + Spring Boot from one
codebase, 24 framework-neutral core classes).

---

## YAML Plugins

Complete resource types declared entirely in YAML — no Java required.

A plugin YAML file declares: spec schema, actual-state detection
(REST calls, JSON extraction, state comparison), provisioning steps,
fault policies, CBR feature schemas, and RAS situation definitions.
Built-in step primitives (`rest-call`, `json-extract`, `compare-state`,
`assert`) compose into complete lifecycles.

Kubernetes operators require Go. Terraform providers require Go.
CaseHub resource types require a YAML file.

The plugin system includes a declarative test framework
(`*.test.yaml`) with embedded WireMock and shell sandbox
infrastructure — plugin authors can test their resource types without
writing test code.

**Extent:** PluginModel, PluginParser, PluginValidator (Levenshtein
suggestions for typos), YamlPluginProvisioner,
YamlPluginActualStateAdapter. Build-time validation cross-references
the @NodeTypeId registry. JUnit5 PluginTestExtension discovers test
YAML and exercises real provisioners.

---

## CBR Fault Learning Loop

Fault recovery that improves with experience.

When reconciliation fails, the CBR pipeline:
1. **Retrieves** similar past fault configurations
2. **Adapts** the recovery strategy to the current context
3. **Applies** the adapted strategy
4. **Revises** based on the outcome (SUCCEEDED, FAILED, SKIPPED,
   REJECTED, SUPERSEDED, ALREADY_PRESENT)

Outcomes flow back as CloudEvents. Future fault responses incorporate
what worked before.

Multi-tier escalation compounds the learning: ThresholdFaultPolicy
with graph-presence guards drives retry → AI review → human review
cascades. Each tier's outcomes feed the CBR store. The system learns
not just *what* to do, but *when to escalate*.

No IaC tool has learning-based fault recovery. Terraform retries are
static. Kubernetes restart policies are fixed. CaseHub fault response
adapts.

**Extent:** FaultPolicyEngine with multi-policy merge and conflict
detection. CbrFaultPolicy for fault-triggered CBR.
CbrSituationRecompiler for situation-triggered CBR.
CbrProposalTracker matching affected nodes to outcomes. Namespace-scoped
FaultCountStore (3-tier CDI priority: custom > JPA > in-memory).

---

## Situation Detection Engine

Five ganglion types, one SPI — covering the full detection spectrum.

| Ganglion Type | What It Detects |
|--------------|-----------------|
| **JavaSwitch** | Stateless pattern matching — fast, simple, no setup |
| **ExpressionRules** | JQ/MVEL expressions over event payloads |
| **NaiveBayes** | Incremental Bayesian classification with prior recalibration |
| **Drools CEP** | Full complex event processing — temporal windows, stream-mode |
| **SituationWatcher** | Meta-situations — situations watching situations |

Events arrive as CloudEvents from any platform source (Kafka, AMQP,
webhook, Camel). The engine routes events to matching situation
definitions, evaluates detection strategies, accumulates evidence, and
triggers case creation or notification when thresholds cross.

**Extent:** 9 modules, 122 Java source files. YAML-based situation
definitions with expression support, evidence templates, dynamic
confidence expressions, and situation templates with parameter
substitution. Flyway V1–V10.

---

## RAS Pheromone CloudEvent Bridge

Cases can influence each other's situation detection through shared
pheromone signals. When a case emits a pheromone CloudEvent —
signalling a condition discovered during its own execution — other
cases' ganglia can incorporate that signal into their detection
logic.

This is cross-case signal visibility: a fraud investigation case
that identifies a suspicious pattern can emit a pheromone that
triggers heightened sensitivity in related compliance cases — without
any direct coupling between the case definitions.

The metaphor is biological: just as ant pheromone trails guide colony
behaviour without centralised coordination, CaseHub pheromones enable
emergent cross-case awareness. No equivalent exists in event
processing systems, where cases are isolated processing contexts.

---

## Composable Signal Architecture

Seven sealed ChainMode variants compose simple signals into complex
detection patterns:

**And** · **Or** · **Threshold** · **Sequence** · **Count** ·
**Streak** · **Rate**

Each is algebraically composable — a Sequence of Thresholds, a Rate
of Streaks, an And of Sequences. The sealed hierarchy is type-safe
and exhaustive — pattern matching is checked at compile time.

This is signal processing as algebra. No CEP system offers this
level of compositional precision with compile-time guarantees.

---

## Meta-Situations

Situations can watch other situations.

A SituationWatcher ganglion observes the lifecycle events of child
situations — creation, expiry, resolution — and fires when patterns
emerge across situations. A temperature anomaly situation and a motion
detection situation, individually benign, become a compound security
situation when they co-occur.

Cycle detection via DFS at registration time prevents circular
observation chains. Deadline-based triggering fires when expected
situations *don't* occur within a time window — non-detection is
itself a signal.

No competitor in the CEP space offers hierarchical
situation-watching-situations with cycle detection and
deadline-triggered absence detection.

---

## Missed Detection API

The system measures its own recall.

External feedback (POST /api/ras/feedback/missed) reports situations
the system should have detected but didn't. The API cross-references
against trigger history to determine whether the miss was genuine
(no event received), a detection failure (event received but not
matched), or a threshold failure (matched but below threshold).

Per-ganglion quality metrics track precision, noise rate, and recall.
A drift classification model (OVER_SENSITIVE, UNDER_SENSITIVE,
BOTH_DRIFTING, STABLE, INSUFFICIENT_DATA) guards against
counter-productive auto-tuning.

The feedback loop operates in two modes:
- **Advisory** — suppression + metrics only, human reviews drift
- **Tuning** — automatic parameter adjustment within safety bounds

This is the operational equivalent of model monitoring in ML — but
for event detection, and built into the platform.

---

## Self-Managing Platform

The ops module runs the engine's own case model against the platform's
own infrastructure. This is not a metaphor — the same case definitions,
worker pipelines, and situation ganglia that manage customer workloads
manage CaseHub itself.

Seven fully-implemented case descriptors:

| Case Descriptor | What It Does |
|----------------|-------------|
| DriftRemediation | Detects and corrects configuration drift |
| ScalingEvent | Responds to load-driven capacity changes |
| CveResponse | Manages vulnerability remediation lifecycle |
| ServiceUpgrade | Orchestrates rolling upgrades |
| IncidentResponse | Coordinates multi-system incident response |
| ComplianceRemediation | Remediates compliance control failures |
| ContainerLifecycle | Manages container provisioning and health |

37 RAS ganglia + 15 situation definitions monitor platform health.
An SSE ring buffer (ApplicationEventBroadcaster) provides real-time
operational visibility. The @McpDomain SPI exposes 29 operations
across REST, GraphQL, and MCP.

The platform is its own best proof point.

---

## Container Lifecycle Management

Podman container provisioning via REST socket API, implementing the
full desiredstate SPI quad:

- **GoalCompiler** — compiles deployment descriptors to
  container/network/volume graphs
- **NodeProvisioner** — provisions and deprovisions via PodmanClient
- **ActualStateAdapter** — queries running state from Podman
- **FaultPolicy** — ThresholdFaultPolicy for container failures

Real-time event stream subscription with exponential backoff reconnect
provides active drift detection — the system knows when a container
stops, not just when it fails a health check.

The same SPI quad pattern governs K8s clusters (fabric8),
containers (Podman), compliance controls, and agent topology —
consistent operations across infrastructure scales.

---

## Adaptive Topology

RAS situation-driven recompilation of deployment topology. When
situations change (load spike, node failure, capacity threshold),
the system recompiles the desired-state graph with updated node
counts, reconfigured routing, or modified fault policies.

Hysteresis prevents oscillation — a scale-up situation must sustain
beyond a configurable window before the topology recompiles, and a
scale-down requires a longer sustain period than scale-up. This
prevents the reactive feedback loop from becoming unstable.

**Extent:** 5-minute safety-net poll alongside event-driven CDI event
bridge. 30 source files, 5 drift checkers with field-by-field
comparison, 5 provision handlers.

---

## IoT Device Lifecycle

The full Declaration → Intelligence → Control → Convergence →
Operations loop applied to physical devices.

11 typed device classes (Matter-aligned: switch, light, thermostat,
sensor, presence, power, lock, cover, media player, fan, camera)
with dual-provider architecture (Home Assistant + OpenHAB), edge-to-cloud
bridge (sealed 7-variant wire protocol, durable store-and-forward),
and a complete incident resolution pipeline:

1. Situation ganglia detect anomaly (7 ganglia: 5 standard + 2
   Drools CEP)
2. Case created with CBR-powered similarity matching (4 feature
   schemas)
3. AI resolution agent opens multi-turn conversation with MCP tools
4. Safe actions execute autonomously; high-risk actions escalate to
   human work items
5. Outcome recorded to CBR — future incidents resolve faster

12 modules, 50+ Java files in the webapp alone, Docker multi-arch
deployment (ARM64 + x86_64). Three bundled playbooks.
Full REST API surface with MCP tool exposure (4 tools).

This is the strongest E2E lifecycle proof point — every stage of the
lifecycle spine exercised against the physical world.

---

## Regulatory Compliance Posture

Compliance as a reconciliation problem — not a checklist.

Each compliance control becomes a desired-state node. Evidence
collection is pluggable via strategy key routing (file-existence,
certificate-expiry, config-hash, log-directory). Human-gated controls
require explicit review. All evidence records are tamper-evident via
ledger integration.

Six frameworks supported: SOC2-TypeII, GDPR, EU-AI-Act Art.12, DORA,
NIS2, ISO27001. Framework registry with bidirectional lookup. Posture
service aggregates cross-control status per framework.

The compliance module uses the same reconciliation loop, same fault
policies, and same approval workflow as every other domain — compliance
isn't a special system, it's the same infrastructure applied to
regulatory requirements.

---

## Cross-Domain Composition

Multiple reconciliation domains compose without coupling.

Push-model composition: each domain compiles its own goals, declares
provides/requires for cross-domain edges, and registers with the
engine. Three composition modes:

- **Flattened** — single merged graph for simple deployments
- **Hierarchical** — meta-loop with one domain-level node per domain,
  preserving domain isolation
- **Passthrough** — 0-1 domains, no composition overhead

Domains compile independently (preserving GoalCompiler&lt;G&gt; type
safety), and domain-specific SituationRecompilers receive only their
own domain graph. Isolation is preserved through composition.

No equivalent exists in IaC — Crossplane is the closest but lacks
human gating, CBR learning, and domain isolation.

---

## What It Gains from the Platform

Convergence and operations are not separate systems bolted onto the
platform — they ARE the platform, applied to itself.

- **Case engine** powers reconciliation control loops — transition
  plans become case instances with prune/grow phases
- **CBR** from neocortex provides fault learning and IoT resolution
  matching
- **RAS** uses platform CloudEvents and expression engines — clean
  event-only boundary, no transport library imports
- **Work items** from the human task system handle approval gates
- **Ledger** provides tamper-evident compliance evidence
- **Tenancy** scopes every reconciliation loop and every ganglion to
  the correct tenant
- **Simulation** enables deterministic replay of both reconciliation
  sequences and detection scenarios

The self-managing platform is the ultimate consistency proof: the ops
module doesn't import a different management system — it uses the same
case definitions, the same CBR, the same ganglia, the same work items.
The platform's own operations are indistinguishable from customer
workloads.

---

## Extent Summary

| Component | Modules | Sources | Key Metric |
|-----------|---------|---------|------------|
| Desired State | 37 | 566 | 27 production + 10 examples |
| RAS | 9 | 122 | 5 ganglion types, 7 ChainModes |
| Ops | 10 | 316 | 7 case descriptors, 37 ganglia |
| IoT | 12 | 170+ | 11 device types, 7 wire variants |
| **Total** | **68** | **1,174+** | |

---

## Connections to Other Areas

- **← Declaration Surface:** Desired state is declared in YAML,
  annotations, or TypeScript (POC). Situation definitions are
  YAML-based. IoT device configurations are declarative.
- **← Enterprise Execution:** Transition plans execute as case
  instances. Reconciliation failures trigger case-driven resolution
  pipelines.
- **← AI Knowledge & Learning:** CBR provides fault learning for
  reconciliation and resolution matching for IoT. RAG supports
  agent-driven diagnosis.
- **← Accountability & Governance:** All reconciliation actions
  produce ledger entries. Compliance evidence is tamper-evident.
  Protocol enforcement governs agent communication during resolution.
- **→ Declaration Surface:** Operations detects drift and triggers
  new declarations — closing the lifecycle loop.

---

*The feedback loop is the differentiator. Detect, reconcile, learn,
repeat. No competitor covers Convergence through Operations as one
platform — and no competitor has the platform operate on itself to
prove it works.*
