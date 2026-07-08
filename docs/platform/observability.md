# Observability

> **Scope:** OTel tracing, audit trails, agent interaction recording, case decision logs
> **Audience:** All
> **Key repos:** casehub-ledger, casehub-work, casehub-engine, casehub-qhorus
> **Protocols:** [dual-trail-audit-pattern](https://github.com/casehubio/garden/blob/main/docs/protocols/casehub/dual-trail-audit-pattern.md)

## OpenTelemetry Trace Linkage

`LedgerTraceListener` in `casehub-ledger` auto-populates `traceId` from the active OTel span at `@PrePersist`.

Every ledger entry carries the trace ID of the request that created it. This links the tamper-evident audit record to distributed tracing tools (Jaeger, Tempo, Honeycomb).

**Runtime:** OTel tracing instrumentation (`opentelemetry-api`) on key orchestration components:
- `ReconciliationLoop` and `SimpleTransitionExecutor` (casehub-desiredstate)
- Worker execution paths (casehub-worker)
- Case lifecycle events (casehub-engine)

## Audit Trails

The platform maintains **dual audit trails** for lifecycle state machines:

1. **Operational trail** — always-on, queryable, non-tamper-evident
2. **Compliance trail** — opt-in, tamper-evident, Merkle-linked

### WorkItem Audit (casehub-work)

- **Operational:** `AuditEntry` — always-on, SQL-queryable, timestamp, actor, status transition
- **Compliance:** `WorkItemLedgerEntry extends LedgerEntry` — opt-in tamper-evident, Merkle-linked, used by trust score computation

**Write rule:** Every state transition must call `audit()` **and** fire `WorkItemLifecycleEvent`. The async observer (`WorkItemLedgerEventCapture`) writes the compliance record.

**Failure mode:** A transition that calls `audit()` but omits the CDI event produces an operational record but no compliance record, silently corrupting trust scores.

See protocol: [dual-trail-audit-pattern](https://github.com/casehubio/garden/blob/main/docs/protocols/casehub/dual-trail-audit-pattern.md)

### Case Decision Logs (casehub-engine)

- **Operational:** `EventLog` — engine-internal, restart recovery, observability
- **Compliance:** `CaseLedgerEntry extends LedgerEntry` — external, tamper-evident, decision accountability

**Write rule:** Every lifecycle transition must fire `CaseLifecycleEvent`. The async observer writes the compliance record.

**Failure mode:** If a lifecycle transition doesn't fire `CaseLifecycleEvent`, it won't be ledgered — and the async observer can fail silently.

Detection query:
```sql
SELECT * FROM case_instance ci
WHERE NOT EXISTS (
  SELECT 1 FROM case_ledger_entry cle
  WHERE cle.case_id = ci.id AND cle.event_type = 'COMPLETED'
)
AND ci.status = 'COMPLETED';
```

See protocol: [dual-trail-audit-pattern](https://github.com/casehubio/garden/blob/main/docs/protocols/casehub/dual-trail-audit-pattern.md)

## Agent Interaction Recording

`MessageLedgerEntry extends LedgerEntry` in `casehub-qhorus` records all 9 speech-act types:

- COMMAND
- QUERY
- RESPONSE
- DONE
- DECLINE
- FAILURE
- STATUS
- HANDOFF
- EVENT

Every agent-to-agent and agent-to-human interaction is recorded in the tamper-evident ledger with:
- `actorId` — sender
- `channelId` — conversation context
- `messageType` — speech act
- `correlationId` — conversation thread
- `inReplyTo` — message being responded to
- `traceId` — distributed trace linkage

The ledger provides normative accountability: who said what, to whom, when, and in what context.

## WorkItem Lifecycle Events

`casehub-work` fires CDI events for all WorkItem state transitions:

- **Outbound:** `WorkCloudEventAdapter` observes `@ObservesAsync WorkItemLifecycleEvent` and produces `CloudEvent` via `Event<CloudEvent>.fireAsync()`.
- **Inbound:** `WorkCloudEventInboundAdapter` observes `@ObservesAsync CloudEvent` type `io.casehub.work.workitem.requested` and creates WorkItems via template-based instantiation.

Event types: `io.casehub.work.workitem.*` (24 types), `io.casehub.work.group.*` (3 types).

Type constants in `casehub-work-api` (`WorkCloudEventTypes`).

This enables external observability systems to react to WorkItem lifecycle without polling the REST API.

## IoT State Change Events

`IoTCloudEventAdapter` in `casehub-iot-api` observes `@ObservesAsync StateChangeEvent` and produces `CloudEvent`.

Event type: `io.casehub.iot.state_change.<deviceClass>` (reverse-DNS).

Carries:
- `deviceId` — which device changed
- `changedCapabilities` — which capabilities changed (e.g. `temperature`, `motion`)
- `before` / `after` — full `DeviceEntity` snapshots

This enables external systems (RAS ganglia, dashboards) to react to IoT state changes without polling the device provider.

## Ledger Entry Enrichment Pipeline

`LedgerEnricherPipeline` in `casehub-ledger` runs CDI-discovered `LedgerEntryEnricher` implementations at persist time.

Enrichers add domain-specific metadata to entries without coupling ledger to domain types.

**Example use cases:**
- Attach case context to worker decision entries
- Add geographic location to audit entries
- Populate risk scores from external classifiers

Enrichers run synchronously in the same transaction as the ledger write.

## W3C PROV-DM Lineage Export

`LedgerProvExportService` in `casehub-ledger` exports tamper-evident audit trails as W3C PROV-DM graphs.

PROV-DM is a W3C standard for provenance interchange. The export enables external compliance tools to ingest CaseHub audit trails without understanding the ledger schema.

**Use cases:**
- Regulatory audits (EU AI Act Art.12 record-keeping)
- Cross-system lineage analysis
- Third-party compliance validation
