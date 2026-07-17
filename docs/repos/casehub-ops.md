# casehub-ops — Platform Deep Dive

**GitHub:** [casehubio/casehub-ops](https://github.com/casehubio/casehub-ops)
**Tier:** Integration (Research project + reference architecture)
**Status:** Active — `infra` module PoC complete (casehub-ops#1); `deployment`, `compliance`, `iot`, `app`, `testing` modules on main

---

## Purpose

Domain implementations of `casehub-desiredstate` SPIs for CaseHub-specific deployment concerns. Bridges the generic desired-state runtime (`casehub-desiredstate`) to concrete CaseHub operational goals — agent deployment, stream topology, channel configuration, IoT desired state, compliance posture, and infrastructure provisioning.

`casehub-desiredstate` stays domain-agnostic; `casehub-ops` is the CaseHub domain layer above it. Research project and reference architecture.

---

## Module Structure

| Module | Purpose |
|--------|---------|
| `api` | SPIs for CaseHub-specific desired state: `GoalCompiler`, `NodeProvisioner`, `ActualStateAdapter`, `FaultPolicy`, `EventSource` implementations keyed to CaseHub domain concepts |
| `infra` | Terraform/Ansible augmentation PoC — `InfraNodeSpec` sealed hierarchy, `InfraBackend` SPI, `StandaloneBackend`, `InfraGoalCompiler`, `InMemoryResourceProvisioner`. Three operating modes: standalone, Terraform augmentation, Ansible augmentation |
| `deployment` | `DeploymentGoalCompiler` — processes `casehub-deployment.yaml` goal declaration into a `DesiredStateGraph`; sub-compilers for agents, streams, channels, detection, trust |
| `compliance` | SOC2/GDPR/EU-AI-Act/DORA posture compliance desired-state — includes `EvidenceCollector` SPI and 4 implementations (FileExistence, CertificateExpiry, ConfigHash, LogDirectory) |
| `iot` | IoT desired state: `IoTGoalCompiler`, `IoTActualStateAdapter`, `IoTNodeProvisioner`, `CapabilityNormalizer`, `CapabilityCommandMapper`, `IoTGoalLoader`, `IoTEventSource`, `IoTApprovalEvaluator`, `IoTFaultPolicy` (coordinates with `casehub-iot`) |
| `app` | Ops console — service lifecycle management for K8s microservices; embeds casehub-engine and casehub-desiredstate |
| `testing` | Shared test fixtures — dependency aggregator POM for `casehub-ops-api`, `casehub-desiredstate-testing`, `casehub-platform-testing`. No Java sources. |

---

## Compliance Module (casehub-ops#18)

**EvidenceCollector** SPI — strategy-based evidence collection for compliance posture verification. Four implementations:
- `FileExistenceEvidenceCollector` — verifies files exist at expected paths (e.g., `.env.example` present, `.env` absent)
- `CertificateExpiryEvidenceCollector` — checks TLS/SSL certificate expiry dates
- `ConfigHashEvidenceCollector` — verifies configuration file hashes match approved baselines
- `LogDirectoryEvidenceCollector` — validates log directory permissions and retention policies

---

## Ops Console App (casehub-ops#29)

Service lifecycle management for Kubernetes microservices through the desiredstate reconciliation engine. The app module embeds casehub-engine and casehub-desiredstate, implementing the SPI quad directly (not a domain module).

**Phase 1 — Foundation:**
- Application and cluster CRUD (JPA entities, Flyway migrations, REST API)
- `ApplicationGoalCompiler` — compiles `ServiceDefinition` → K8s `DesiredStateGraph`
- Stubbed lifecycle (@DefaultBean SPI stubs for ActualStateAdapter, NodeProvisioner, FaultPolicy, EventSource)

**Phase 2 — Kubernetes Integration:**
- K8sResourceHandler per resource type (Namespace, Deployment, Service, Ingress, ConfigMap)
- `KubernetesActualStateAdapter` + `KubernetesNodeProvisioner` replacing stubs via fabric8
- `KubernetesFaultPolicy` (empty — runtime handles retry) + passive `KubernetesEventSource`
- `K8sClientRegistry` for multi-cluster client management with @PreDestroy cleanup
- `ApplicationLifecycleService` wired to `ReconciliationLoop` with start-or-update semantics
- `DeploymentOutcomeTracker` — CDI CloudEvent observer for async deploy convergence
- `DecommissionCompletionHandler` — loop stop + index cleanup on decommission convergence
- `StartupRecoveryService` — @Observes StartupEvent restarts loops for non-terminal apps
- `ClusterService.delete()` rejects with 409 when active loops reference the cluster
- Topology manager: `DeploymentRecordEntity.topologyJson` stores service graph (JSON), updated on each deployment

### Kubernetes Integration

**`K8sClientRegistry`** (`io.casehub.ops.app.k8s`): Multi-cluster client management with `@PreDestroy` cleanup. Credential rotation via `checkExpiring()` (scheduled every 60s, refreshes when <5min to expiry). Reactive 401 refresh via `withRetryOn401()` — catches `KubernetesClientException` code 401, calls `refreshClient()`, retries. `CompletableFuture` coalescing deduplicates concurrent refreshes. Fires `CredentialRefreshedEvent` CDI event on refresh.

**`K8sWatchManager`** (`io.casehub.ops.app.k8s`): fabric8 `Watch` on 4 resource types (deployments, services, configmaps, ingresses) filtered by `managed-by=casehub-ops` label. `driftWatcher()` emits `StateEvent` with `NodeStatus.DRIFTED` or `ABSENT` on MODIFIED/DELETED actions. Watches auto-reconnect on `CredentialRefreshedEvent`.

**`InfraBackend`** SPI (`io.casehub.ops.api.infra.spi`): reactive `readState(NodeId, InfraNodeSpec) → Uni<ResourceState>` and `detectDrift(NodeId, InfraNodeSpec) → Uni<DriftReport>`.

### ScalingPolicy

`ScalingPolicy` record (`io.casehub.ops.app.case_`): `clamp(int targetReplicas)` for bounds clamping (`Math.max/min`), `isCoolingDown(Instant lastScalingEvent, Instant now)` for cooldown enforcement. Validates minReplicas >= 0, maxReplicas >= minReplicas, non-negative cooldown in constructor. Includes `UNBOUNDED` constant.

### Case Model

Two CaseDefinition descriptors in `io.casehub.ops.app.case_`:

- **`DriftRemediationCaseDescriptor`** — `drift-remediation` case with 3 workers (classify/remediate/escalate). Classifies drift severity (persistent, multi-node, security-sensitive fields), auto-remediates benign, escalates critical.
- **`ScalingEventCaseDescriptor`** — `scaling-event` case with 3 workers (evaluate/execute/verify-convergence). Applies `ScalingPolicy` clamping and cooldown, delegates to `ApplicationLifecycleService.updateServiceReplicas()`, tracks convergence via `NodeConvergenceTracker`.

### PendingApproval Provisioner Support

`OpsPendingApprovalHandler` (`io.casehub.ops.api.approval`): implements `PendingApprovalHandler` with plan/apply lifecycle. Methods: `check()` (returns None/Pending/Approved/Rejected), `recordPending()` (stores pending entry with plan reference), `approve()` (PENDING → APPROVED with `PlanApproval`), `reject()` (PENDING → REJECTED, cleanup via `PlanStore`). Risk-gated evaluators per domain: `InfraApprovalEvaluator`, `DeploymentApprovalEvaluator`, `IoTApprovalEvaluator`.

### AdaptiveTopologyManager

`AdaptiveTopologyManager` (`io.casehub.ops.deployment.adaptation`): RAS situation-driven topology recompilation. Observes `SituationChangeEvent` via `@ObservesAsync`, queries `SituationSource.activeSituations()`, applies `AdaptationRule`s to recompile the desired-state graph per tenant. Hysteresis via `TenantAdaptationState.shouldActivate()` and `clearAbsentSituations()`. Per-tenant serialization via `synchronized(state)`. Safety-net periodic poll every 5 minutes with graph content equality comparison. Uses `ReconciliationTarget` interface for `start/updateDesired/requestReconciliation`.

### Agent Drift Detection

`AgentDriftChecker` (`io.casehub.ops.deployment.drift`): implements `NodeDriftChecker`. Delegates to `AgentDescriptorComparator.compare(desired, actual)` for field-by-field comparison. Logs each `drift.field()`, `drift.desiredValue()`, `drift.actualValue()` at DEBUG. Returns ABSENT/DRIFTED/PRESENT. Resolves actual state via `AgentRegistry.findById()`.

---

## Infra Module PoC (casehub-ops#1)

`InfraNodeSpec` sealed hierarchy: `StandaloneNodeSpec`, `TerraformNodeSpec`, `AnsibleNodeSpec` — each representing one operating mode.

`InfraBackend` SPI — provision/deprovision infrastructure nodes. Implementations: `StandaloneBackend` (in-memory, test-friendly), `TerraformBackend` (planned), `AnsibleBackend` (planned).

`InfraGoalCompiler` — translates `casehub-desiredstate` `GoalSpec` into an `InfraNodeSpec` hierarchy.

`InMemoryResourceProvisioner` — test-scope in-memory `NodeProvisioner` implementation. 96 tests green.

---

## Depends On

| Artifact | Module | Nature |
|---|---|---|
| `casehub-desiredstate-api` | `api`, `infra` | `GoalCompiler`, `NodeProvisioner`, `ActualStateAdapter`, `FaultPolicy`, `EventSource` SPIs |
| `casehub-desiredstate` (runtime) | `infra` | `DefaultDesiredStateGraphFactory` (test scope) |
| `casehub-platform-api` | `api` | `Path`, `Preferences`, `CurrentPrincipal` |
| `casehub-work-api` | `infra` | `WorkItem` generation for human nodes |

---

## Design Documents

- Spec: `docs/superpowers/specs/2026-06-12-infra-terraform-ansible-adapter-design.md` (in casehub-ops repo)
