# CaseHub API Reference

> Machine-generated API documentation for LLM and RAG consumption.
> Each repo's API reference is generated from source by jmarkdoc
> (Java) or TypeDoc (TypeScript). This index links to all available
> API references.

## Per-Repo API References

### Foundation

| Repo | Types | API Surface | Reference |
|------|-------|------------|-----------|
| **engine** | 247 | CaseDefinition, AgentRoutingStrategy, bindings, goals, planning SPIs, routing, mesh, oversight | [API](../repos/casehub-engine/api/) |
| **work** | 63 | WorkItem lifecycle, WorkerSelectionStrategy, SLA, delegation, queues, progress | [API](../repos/casehub-work/api/) |
| **eidos** | 92 | AgentDescriptor, CapabilityHealth, SystemPromptRenderer, vocabulary, graph | [API](../repos/casehub-eidos/api/) |
| **qhorus** | 142 | ChannelManager, MessageDispatcher, Commitment, projections, OTel tracing | [API](../repos/casehub-qhorus/api/) |
| **ledger** | 20 | LedgerEntry, attestation, EigenTrust, GDPR erasure, KMS signing | [API](../repos/casehub-ledger/api/) |
| **worker** | 20 | Worker, Capability, WorkerFunction, WorkerResult, WorkerScope | [API](../repos/casehub-worker/api/) |
| **neocortex** | 225 | InferenceModel, CaseRetriever, RAG pipelines, CBR, agent memory | [API](../repos/casehub-neocortex/api/) |
| **platform** | 39 | CurrentPrincipal, PreferenceProvider, notifications, expressions, ACL | [API](../repos/casehub-platform/api/) |
| **blocks** | 253 | Agentic orchestration, conversation protocol, routing strategies, summarisation | [API](../repos/casehub-blocks/api/) |

### Infrastructure

| Repo | Types | API Surface | Reference |
|------|-------|------------|-----------|
| **ras** | 57 | Ganglion, SituationDefinition, event correlation, case triggers | [API](../repos/casehub-ras/api/) |
| **desiredstate** | 84 | DesiredStateGraph, GoalCompiler, NodeProvisioner, FaultPolicy | [API](../repos/casehub-desiredstate/api/) |
| **ops** | 136 | InfraNodeSpec, EvidenceCollector, compliance, deployment goals | [API](../repos/casehub-ops/api/) |
| **iot** | 53 | DeviceRegistry, DeviceProvider, Matter-aligned, SSE streaming | [API](../repos/casehub-iot/api/) |

### Applications

| Repo | Types | API Surface | Reference |
|------|-------|------------|-----------|
| **aml** | 64 | Investigation, compliance, risk classification | [API](../repos/casehub-aml/api/) |
| **clinical** | 65 | Clinical decision support, adverse events, CBR | [API](../repos/casehub-clinical/api/) |
| **life** | 54 | Personal automation, household management | [API](../repos/casehub-life/api/) |
| **soc** | 17 | Security operations, alert triage | [API](../repos/casehub-soc/api/) |
| **fsitrading** | 11 | Financial services trading | [API](../repos/casehub-fsitrading/api/) |

**Total: 1,636 types across 18 repos**

## Cross-Repo SPI Implementations

[cross-repo-implementations.md](cross-repo-implementations.md) — 94 SPIs with
implementations across multiple repos. Updated when repos are synced.

## Relationship to Other Docs

- **Consumer guides** (`docs/repos/*/consumer-guide.md`) — explain *when* and *why* to use each API
- **This reference** (`docs/repos/*/api/`) — documents *what* the exact signatures and types are
- **Cross-repo implementations** — shows *who else* implements each SPI
