# Platform Coherence Analysis — 2026-05-23

**Issue:** casehubio/parent#4
**Branch:** issue-4-platform-coherence-audit

## Status

| Batch | Theme | Findings | Done |
|-------|-------|----------|------|
| M1 | Worker selection intelligence | 2, 14, 15 | 3/3 ✅ |
| M2 | Audit trail documentation | 4, 6 | 2/2 ✅ |
| M3 | Notification + signal silo | 8, 9, 24, 25 | 4/4 ✅ |
| M4 | Integration boundary semantics | 16, 17 | 2/2 ✅ |
| M5 | SpawnGroup / Stage gap | 20 | 1/1 ✅ |
| M6 | Provenance + observability | 23, 29 | 2/2 ✅ |
| M7 | Architecture placement | 26 | 0/1 |
| M8 | Normative enforcement | 30, 32 | 0/2 |
| L1 | Verification required | 5 | 0/1 |
| L2 | Documentation + patterns | 11, 12 | 0/2 |
| L3 | Structural debt | 13, 19, 27 | 0/3 |

**Total:** 14 / 23 findings complete

## Findings

---

## Batch M1 — Worker selection intelligence (findings 2, 14, 15)

Cross-finding note: findings 2 and 14 are two facets of the same architectural gap — the engine's
worker selection is isolated from both trust data (2) and semantic intelligence (14). Both stem
from `WorkOrchestrator` owning strategy selection explicitly rather than delegating to CDI.
Finding 15 is a distinct governance gap in the shared capability vocabulary.

---

## Finding 2 — Trust scores published but no WorkerSelectionStrategy consumes them

**Status:** Confirmed — more fundamental than described
**Batch:** M1
**Repos:** casehub-engine, casehub-ledger, quarkus-work

### Verification

- **Code read:** `WorkOrchestrator.doSubmit()`, `SelectionContext` record, `TrustScoreRoutingPublisher`
- **Evidence:**
  - `TrustScoreRoutingPublisher` fires `TrustScoreFullPayload`, `TrustScoreDeltaPayload`,
    `TrustScoreComputedAt` CDI events. Engine imports `casehub-ledger`; these events are in scope.
  - `WorkOrchestrator` builds `SelectionContext(null, null, capability.getName(), null, null, null, null, null)` — seven of eight fields are null. `SelectionContext` has no trust field at all.
  - `WorkOrchestrator` never queries `ActorTrustScoreRepository` before building `SelectionContext`.
  - Strategy is passed explicitly: `workBroker.apply(context, CREATED, candidates, selectionStrategy)`.
    Even if a trust-aware strategy existed, it would receive a context with no trust data.

### Root Cause

`SelectionContext` was designed as a minimal WorkItem projection — category, priority, capability
tags, candidate groups. Trust scoring was added to ledger later as a separate concern. Nobody
extended `SelectionContext` to carry trust context, and `WorkOrchestrator` never wired the two.
The gap is structural: the API boundary (`SelectionContext`) has no slot for trust data, so no
strategy can consume it regardless of what is implemented.

### Blast Radius

Trust scoring in ledger is fully operational — scores are computed, stored, and published. But
they cannot influence who receives work. Any trust-weighted routing requirement (prefer high-trust
workers, exclude low-trust workers, boost by capability dimension) is impossible to implement
without first changing `SelectionContext`. The trust scoring investment is effectively stranded.

### Implementation Guidance

1. Add `Map<String, Double> trustScoresByActorId` to `SelectionContext` — keyed by worker name,
   value is the actor's global trust score. Nullable; strategies that ignore trust receive null.
2. In `WorkOrchestrator.doSubmit()`, after building candidates, query
   `ActorTrustScoreRepository.findByActorIds(candidateNames)` (repository already in CDI context
   via casehub-ledger import) and inject the scores into `SelectionContext`.
3. Implement `TrustWeightedStrategy` in `casehub-engine-ledger` module: weight `LeastLoadedStrategy`
   scores by trust score, with configurable blend factor. Activate via `@Alternative @Priority`.
4. This unblocks finding 14 — once `SelectionContext` carries trust data, `SemanticWorkerSelectionStrategy`
   can also incorporate trust weighting in its scoring.

**Scale:** M — `SelectionContext` API change (quarkus-work-api), `WorkOrchestrator` change (engine),
new `TrustWeightedStrategy` (casehub-engine-ledger)
**Complexity:** Med — clear path; the trust repository is already in scope; API change is additive

### Issue

casehubio/engine#336 — resolve after engine#337 (CDI strategy resolution) is in place

---

## Finding 14 — SemanticWorkerSelectionStrategy unused in casehub-engine

**Status:** Confirmed — harder to fix than described
**Batch:** M1
**Repos:** casehub-engine, quarkus-work

### Verification

- **Code read:** `WorkOrchestrator` (field `LeastLoadedStrategy selectionStrategy`, line 74),
  `WorkCdi.java` (documents the concrete-injection rule), engine root `pom.xml`
- **Evidence:**
  - `WorkOrchestrator` injects `LeastLoadedStrategy` by concrete type and passes it explicitly to
    `workBroker.apply(context, CREATED, candidates, selectionStrategy)`.
  - Engine has no dependency on `quarkus-work-ai`.
  - `WorkCdi.java` documents why: injecting `WorkerSelectionStrategy` by interface causes
    `AmbiguousResolutionException` because both `LeastLoadedStrategy` and `ClaimFirstStrategy`
    are active `@ApplicationScoped` CDI beans.
  - The `@Alternative @Priority(1)` mechanism on `SemanticWorkerSelectionStrategy` works via
    CDI injection. But `WorkOrchestrator` bypasses CDI entirely — it injects a concrete type
    and passes it as a parameter. Even adding `quarkus-work-ai` to engine would not activate
    semantic routing.

### Root Cause

`WorkBroker.apply()` accepts the strategy as a caller-supplied parameter rather than resolving
it via CDI internally. This was the right design for quarkus-work (where the strategy is
configured per application), but it means the `@Alternative @Priority` extension point that
makes `SemanticWorkerSelectionStrategy` drop-in is bypassed in engine. The engine caller must
explicitly choose the strategy, and it hard-codes the least-loaded one.

### Blast Radius

Semantic skill matching — matching workers to work by narrative embedding similarity — is fully
implemented in `quarkus-work-ai` and auto-activates in quarkus-work applications. In
casehub-engine, it is completely unavailable. AI-driven orchestration (matching case tasks to
the most semantically appropriate worker) is blocked entirely.

### Implementation Guidance

Two options; option A is preferred:

**A — CDI priority resolution in WorkOrchestrator (recommended)**
1. Change `WorkOrchestrator` to inject `@Any Instance<WorkerSelectionStrategy> strategies`.
2. Resolve the highest-priority available strategy at call time:
   `strategies.stream().max(comparingInt(s -> getPriority(s.getClass()))).orElseThrow()`
   where `getPriority` reads the `@Priority` annotation value (0 if absent).
3. Add `quarkus-work-ai` as an optional dependency in `casehub-engine/runtime/pom.xml`.
4. When `quarkus-work-ai` is on the classpath, `SemanticWorkerSelectionStrategy` (`@Priority(1)`)
   wins over `LeastLoadedStrategy` (no priority → 0) automatically.

**B — WorkBroker resolves strategy internally**
Redesign `WorkBroker.apply()` to resolve the strategy via CDI when no strategy is passed.
More invasive (API change) but removes the burden from every caller.

Option A is lower blast radius and doesn't require a quarkus-work-api change.

**Scale:** S — one injection point change in WorkOrchestrator, one optional pom dependency
**Complexity:** Low — the `@Priority` resolution pattern is standard CDI

### Issue

casehubio/engine#337 — resolve this first; engine#336 depends on it

---

## Finding 15 — Capability vocabulary between engine and work is unmanaged

**Status:** Confirmed — format is consistent; governance is the gap
**Batch:** M1
**Repos:** casehub-engine, quarkus-work

### Verification

- **Code read:** `WorkOrchestrator.buildCandidates()`, `SelectionContext`, `WorkerCandidate`,
  engine `CaseDefinition.Capability`, `Worker.getCapabilities()`
- **Evidence:**
  - Engine: `CaseDefinition.Worker` holds `List<Capability>`, each with `getName()`. Engine
    creates `WorkerCandidate(name, Set.of(capabilityName), workload)` — capability as a single
    String in a Set.
  - `SelectionContext.requiredCapabilities` is documented as "comma-separated capability tags".
    Engine passes `capability.getName()` — a single name, valid as a single-element list.
  - Both sides use `String` — the format is wire-compatible.
  - The gap: engine capability names live in `CaseDefinition` objects (code/JSON, managed by
    case authors). Work capability tags live in worker registration (DB, managed at runtime).
    No shared registry; no enforcement that the same string means the same thing in both systems.

### Root Cause

Capabilities were conceived independently in each layer. Engine `Capability` is a structural
element of case definition (what the case needs done). Work capability tag is a worker attribute
(what the worker can do). They meet at `WorkBroker` via string matching, but the matching
contract — that the strings are drawn from the same vocabulary — is implicit and undocumented.

### Blast Radius

Capability mismatches (e.g. engine uses `"legal-review"`, worker registers `"legal_review"`)
produce silent failures: `WorkBroker` finds no capable candidates, `WorkOrchestrator` throws
`IllegalStateException("No worker available for capability: legal-review")`. No diagnostic
points at the vocabulary gap. As the number of case definitions and worker types grows, drift
becomes likely and debugging is difficult.

### Implementation Guidance

1. Define capability names as constants in a shared module (e.g. `casehub-engine-api` or a new
   `casehub-capability-registry` module): `CapabilityNames.LEGAL_REVIEW = "legal-review"`.
2. Engine case definitions reference these constants; worker registrations import and use the same.
3. Longer term: a `CapabilityRegistry` SPI in `quarkus-work-api` that lists known capabilities;
   startup validation checks that all worker-registered tags exist in the registry.
4. Immediate: document the matching contract (exact case-sensitive string) in `SelectionContext`
   javadoc and `WorkBroker` javadoc.

**Scale:** S — shared constants module or documented convention; optional startup validator
**Complexity:** Low — no runtime behavior changes; purely additive

### Issue

casehubio/work#220

---

## Batch M2 — Audit trail documentation (findings 4, 6)

Cross-finding note: findings 4 and 6 are the same undocumented pattern in two different repos.
Both repos have an operational trail (EventLog / AuditEntry) and a compliance ledger
(CaseLedgerEntry / WorkItemLedgerEntry). The split makes architectural sense but is invisible
to anyone reading the code. Both are addressed by the same protocol and the same javadoc fix.

---

## Finding 4 — casehub-engine has two audit trails, split undocumented

**Status:** Confirmed
**Batch:** M2
**Repos:** casehub-engine, casehub-ledger

### Verification

- **Code read:** `EventLog.java`, `CaseLedgerEntry.java`, `CaseLedgerEventCapture.java`,
  `EventLogRepository`, `WorkerContextProvider` javadoc
- **Evidence:**
  - `EventLog`: plain domain object with `caseId`, `eventType` (`CaseHubEventType` enum),
    `workerId`, `timestamp`, `metadata (JsonNode)`. No hash chain. Written synchronously by
    `WorkOrchestrator` and `CaseStatusChangedHandler` via `EventLogRepository`. Javadoc says
    "Plain domain object for an **immutable** audit event" — no hash-chain, so "immutable"
    means only append-only, not tamper-evident.
  - `CaseLedgerEntry`: extends `LedgerEntry` (Merkle-chained, `sequenceNumber`, `digest`,
    `supplements`). Written by `CaseLedgerEventCapture` via `@ObservesAsync CaseLifecycleEvent`
    in its **own transaction** — eventual consistency with respect to case state is explicit.
    Optional module: `LedgerConfig.enabled()` gates every write.
  - `WorkerContextProvider` javadoc contains the only hint of the split: "query
    `CaseLedgerEntryRepository` (not EventLog) for prior worker" — scattered and easy to miss.
  - No class, protocol, or design doc states the governing rule.

### Root Cause

`EventLog` predates the ledger module. When `casehub-ledger` was introduced for tamper-evident
compliance records, no protocol was written documenting the split. The javadoc on `EventLog`
uses the word "immutable" in the wrong sense (append-only, not hash-chained), making it appear
to satisfy compliance requirements it cannot actually meet.

### Blast Radius

A developer building a compliance feature queries `EventLogRepository` — obvious choice from the
name. They get append-only records with no tamper-evidence. The compliance requirement fails
silently: data looks correct, but a determined actor could alter `EventLog` rows without breaking
any integrity check. Separately, a developer adding a new lifecycle event doesn't know whether to
write to `EventLog`, fire a `CaseLifecycleEvent`, or both.

### Implementation Guidance

1. **Correct `EventLog` javadoc** — replace "immutable audit event" with "operational event log
   entry — for observability and runtime queries. Not tamper-evident; do not use for compliance
   or regulatory audit."
2. **Add a parallel note to `EventLogRepository`** javadoc.
3. **Publish a garden protocol: `dual-trail-audit-pattern.md`** — governing rule:
   - All case lifecycle transitions MUST fire a `CaseLifecycleEvent` → ledger captures automatically
   - `EventLog` MUST be used only for operational events (WORK_SUBMITTED, monitoring, replay)
   - Compliance/regulatory queries MUST read from `CaseLedgerEntryRepository`
   - Note the eventual-consistency gap: ledger write is in a separate transaction; compliance
     queries requiring strong consistency with case state must account for the lag
4. Cross-reference finding 6 — same protocol governs quarkus-work.

**Scale:** S — javadoc fixes + one garden protocol
**Complexity:** Low — no runtime behaviour changes

### Issue

casehubio/parent#52

---

## Finding 6 — quarkus-work has two audit trails, split undocumented

**Status:** Confirmed — identical pattern to finding 4
**Batch:** M2
**Repos:** quarkus-work, casehub-ledger

### Verification

- **Code read:** `AuditEntry.java`, `WorkItemLedgerEntry.java`, `LedgerEventCapture.java`,
  `WorkItemService.audit()` helper
- **Evidence:**
  - `AuditEntry`: JPA entity, `workItemId / event (String) / actor / detail (TEXT) / occurredAt`.
    Written by `WorkItemService.audit()` private helper. No hash chain. Javadoc says "Immutable
    audit log entry recording a lifecycle event" — append-only, not tamper-evident.
  - `WorkItemLedgerEntry`: extends `LedgerEntry` (Merkle-chained, JOINED inheritance,
    `commandType + eventType` CQRS encoding). Written by `LedgerEventCapture` CDI observer.
    Has REST endpoint via `LedgerResource`. Feeds trust score computation in `TrustScoreJob`.
  - No documentation states which to use for compliance.

### Root Cause

Same as finding 4: `AuditEntry` predates the ledger module. The javadoc framing is identical
in its misleading implication. Additionally: `AuditEntry` is written by explicit `audit()` calls;
`WorkItemLedgerEntry` is written by a CDI observer. If a new state transition calls `audit()` but
forgets to fire the CDI event, the operational log gets an entry but the compliance ledger does
not. No test currently enforces that both trails receive every lifecycle event.

### Blast Radius

Same as finding 4, plus the symmetry gap: divergence between the two trails is possible and
undetected. A lifecycle transition missing from `WorkItemLedgerEntry` silently breaks trust score
computation (which reads only from the ledger) — wrong scores, wrong routing decisions downstream.

### Implementation Guidance

1. **Correct `AuditEntry` javadoc** — clarify it is operational, not tamper-evident.
2. **Add a note to `AuditEntryStore` javadoc.**
3. **Add an integration test** asserting that for every WorkItem lifecycle transition, both an
   `AuditEntry` and a `WorkItemLedgerEntry` are written. Divergence becomes a test failure.
4. The garden protocol from finding 4 covers the cross-repo rule.

**Scale:** S — javadoc fixes + one integration test assertion
**Complexity:** Low

### Issue

casehubio/parent#52

---

## Batch M3 — Notification + signal silo (findings 8, 9, 24, 25)

Cross-finding note: all four findings are facets of the same broken pipeline. The platform has
the pieces — WatchdogScheduler, Connector SPI, CaseHubReactor.signal(), WorkEventType — but they
are not connected. Findings 8 and 9 are the output/input gaps at the boundaries of quarkus-qhorus
and quarkus-work respectively; finding 24 is the architectural consequence of both gaps; finding
25 is the vocabulary gap that results from signals having no lifecycle representation in work.

Findings 8, 9, 24 are filed as a single cross-repo issue. Finding 25 is filed separately in work.

---

## Finding 8 — Watchdog alerts reach Qhorus channels only, not human-facing delivery

**Status:** Confirmed
**Batch:** M3
**Repos:** quarkus-qhorus, casehub-connectors

### Verification

- **Code read:** `WatchdogEvaluationService.fireAlert()`, `WatchdogScheduler.evaluate()`
- **Evidence:**
  - `fireAlert()` calls `channelService.findByName(w.notificationChannel)` then
    `messageService.dispatch(MessageDispatch.builder().channelId(...).type(STATUS)...)`.
  - `MessageDispatch` goes to a Qhorus internal `Channel` — an in-process message bus for agents.
    No bridge to `casehub-connectors` exists anywhere in `WatchdogEvaluationService`.
  - If `w.notificationChannel` doesn't exist, `fireAlert()` returns silently — no fallback.

### Root Cause

`WatchdogEvaluationService` was written targeting Qhorus channels as its notification primitive.
`casehub-connectors` (the human-facing delivery SPI) was never wired to the watchdog output path.

### Blast Radius

Stalled-obligation alerts, stuck barrier alerts, approval-pending warnings, agent staleness, and
queue depth alerts all fire into internal channels that only connected agents can observe. Human
operators are never notified. The watchdog is functionally invisible to humans.

### Implementation Guidance

1. Add an optional `Connector` delivery path to `WatchdogEvaluationService`: inject
   `@Any Instance<Connector>` and call `send(ConnectorMessage)` for each active connector.
2. Alternatively, emit a `WatchdogAlertEvent` CDI event from `fireAlert()`; a `ConnectorAlertBridge`
   bean in a separate integration module observes it and dispatches via `Connector`. Keeps
   qhorus core free of the connectors dependency.
3. **Depends on parent#5** — the right Connector API should be in place before wiring.

**Scale:** M — new integration bridge between qhorus and connectors
**Complexity:** Med — clean path once parent#5 lands

### Issue

casehubio/parent#53

---

## Finding 9 — WorkItem escalation has no path back to CaseHubReactor

**Status:** Confirmed
**Batch:** M3
**Repos:** quarkus-work, casehub-engine

### Verification

- **Code read:** `ExpiryLifecycleService.executeEscalateTo()`, `CaseHubReactor.signal()`,
  `PendingWorkRegistry`
- **Evidence:**
  - `executeEscalateTo()` calls `fireLifecycleEvent("ESCALATED", item)` and
    `slaBreachEventBus.fire(new SlaBreachEvent(...))` — both stay within quarkus-work CDI context.
  - `CaseHubReactor.signal()` exists in engine, exposed via `CaseHubRuntimeImpl.signal()`, but
    nothing in quarkus-work calls it.
  - `PendingWorkRegistry` future is only completed on success or failure — not on escalation.
    A case waiting on an escalated WorkItem remains in `WAITING` state indefinitely.

### Root Cause

`ExpiryLifecycleService` handles escalation within the quarkus-work domain. No adapter bridges
the escalation event to the engine's signal path. `PendingWorkRegistry` has no escalation slot.

### Blast Radius

Cases in `WAITING` freeze when their WorkItem escalates. The engine cannot react (reroute, extend
deadline, fault the case). Any case definition expecting to handle escalation is broken.

### Implementation Guidance

1. Define `CaseSignalSink` SPI in `casehub-engine-api` (or `quarkus-work-api`):
   `void onWorkItemEscalated(UUID workItemId, String correlationKey, List<String> groups)`.
2. Implement in `casehub-engine`: look up the case awaiting `correlationKey` in
   `PendingWorkRegistry`, call `CaseHubReactor.signal(caseId, "escalation", payload)`.
3. In `ExpiryLifecycleService.executeEscalateTo()`, inject `@Any Instance<CaseSignalSink>`
   and call if present. quarkus-work acquires no hard dependency on engine.

**Scale:** M — new SPI + engine implementation + one call site in work
**Complexity:** High — cross-repo SPI design; must not create hard dependency work→engine

### Issue

casehubio/parent#53

---

## Finding 24 — Three disconnected human input paths

**Status:** Confirmed
**Batch:** M3
**Repos:** casehub-engine, quarkus-qhorus, quarkus-work

### Verification

- **Code read:** `CaseHubReactor.signal()`, `CaseHubRuntimeImpl.signal()`,
  `MessageService.dispatch()`, `PendingWorkRegistry`
- **Evidence:**
  1. **WorkItem completion** → `PendingWorkRegistry.complete(correlationKey)` → engine future.
     Works only for work the engine explicitly submitted and is awaiting.
  2. **Qhorus human message** → `MessageService.dispatch()` → Qhorus `Channel` only.
     No bridge to `CaseHubReactor.signal()`.
  3. **Direct signal** → `CaseHubRuntimeImpl.signal()` → Vert.x `SIGNAL_RECEIVED`. Works if
     the caller knows `caseId` and `path`, but nothing in Qhorus or escalation path calls it.
  - Paths 1 and 3 reach the engine; path 2 does not. Paths 2 and 3 do not interact with the
    WorkItem lifecycle. Nothing unifies them.

### Root Cause

Each path was built independently to solve a specific problem. No unifying design was ever
produced; each is a vertical slice with no lateral bridges.

### Blast Radius

Human operators cannot inject decisions into running cases via Qhorus messages. WorkItem
escalation doesn't return control to the engine. Any use case requiring cross-path coordination
(e.g. "human responds in Qhorus to unblock a waiting case") cannot be built without new wiring.

### Implementation Guidance

**Short term:**
1. Bridge Qhorus message → engine: when a `Message` arrives on a channel carrying a `caseId`
   header, call `CaseHubRuntimeImpl.signal(caseId, ...)`. A `QhorusCaseBridge` bean in a
   `casehub-engine-qhorus` integration module observes `MessageDispatchedEvent`.
2. Bridge WorkItem escalation → engine via `CaseSignalSink` SPI (finding 9).

**Long term:**
A `CaseSignalBus` SPI — single point of entry for all external inputs to a running case. Paths
1, 2, and 3 become adapters over the bus. Case definitions handle `onSignal(Signal)` regardless
of origin.

**Scale:** L — three-path unification; short-term bridges are M each
**Complexity:** High — cross-repo coordination; signal semantics must be defined first

### Issue

casehubio/parent#53

---

## Finding 25 — WorkEventType has no SIGNAL_RECEIVED

**Status:** Confirmed
**Batch:** M3
**Repos:** quarkus-work

### Verification

- **Code read:** `WorkEventType.java`
- **Evidence:** Values: CREATED, ASSIGNED, STARTED, COMPLETED, REJECTED, DELEGATED, RELEASED,
  SUSPENDED, RESUMED, CANCELLED, EXPIRED, CLAIM_EXPIRED, SPAWNED, ESCALATED. No SIGNAL_RECEIVED.

### Root Cause

Signals as a WorkItem concept don't exist yet — the input paths are not wired (finding 24).
The vocabulary gap is a direct consequence of the architectural gap.

### Blast Radius

When findings 9 and 24 are resolved and signals can flow into WorkItems, the `WorkItemLedgerEntry`
and `AuditEntry` trails will have no event type to record signal receipt. A signal that changes
WorkItem routing or state will leave no record in the compliance trail.

### Implementation Guidance

1. Add `SIGNAL_RECEIVED` to `WorkEventType` — trivial enum addition, zero risk.
2. When the signal input path exists, call `audit()` and fire `WorkItemLifecycleEvent` with
   `SIGNAL_RECEIVED` on receipt.
3. **Implement after finding 24** — the enum can be added now; the wiring waits.

**Scale:** XS — one enum value; lifecycle wiring is XS–S on top
**Complexity:** Low — purely additive

### Issue

casehubio/work#221

---

## Batch M4 — Integration boundary semantics (findings 16, 17)

Cross-finding note: both findings are about the same class of problem — terminology used
differently at repo boundaries, creating implicit contracts that diverge silently. Finding 16 is
a collapse of semantically distinct work states into one engine state. Finding 17 is a terminal-
semantics mismatch hidden behind the same vocabulary in two repos.

---

## Finding 16 — WorkItem REJECTED, EXPIRED, ESCALATED all map to CaseHub FAULTED

**Status:** Confirmed — broader than described; three states collapse, not two
**Batch:** M4
**Repos:** casehub-engine (work-adapter), quarkus-work

### Verification

- **Code read:** `WorkItemLifecycleAdapter.applyStatus()`, `WorkItemStatus.isTerminal()`,
  `PlanItem.markFaulted()`
- **Evidence:**
  - `WorkItemLifecycleAdapter.applyStatus()` line 172:
    `case REJECTED, EXPIRED, ESCALATED -> item.markFaulted()`
  - `WorkItemStatus.REJECTED` javadoc: "WorkItem was rejected by the assignee or a reviewer."
    This is an **intentional refusal**, not a technical failure.
  - `WorkItemStatus.EXPIRED` javadoc: "WorkItem's deadline passed without resolution." Time-based.
  - `WorkItemStatus.ESCALATED` javadoc: "WorkItem was escalated due to expiry or policy breach."
    Routing event — the work may still be completable by a different group.
  - All three become `CaseStatus.FAULTED` via `markFaulted()` → `markCancelled()` does not.
  - Case definitions have no way to distinguish REJECTED (refused) from EXPIRED (timed out) from
    ESCALATED (rerouted). The outcome of a WorkItem collapses to: COMPLETED, CANCELLED, or FAULTED.

### Root Cause

`WorkItemLifecycleAdapter` was written when the only semantically meaningful distinction was
COMPLETED vs everything-else-bad. REJECTED, EXPIRED, and ESCALATED were all treated as
"something went wrong." As the platform matured, these three states acquired distinct meanings
that the adapter never revisited.

### Blast Radius

A case definition cannot implement:
- "If the worker refused (REJECTED), offer the task to a different group"
- "If the task timed out (EXPIRED), fault the case; if escalated, continue waiting"
- "On ESCALATED, record the escalation group and resume case with adjusted deadline"
All such requirements silently fault the case regardless of the actual work outcome. Case authors
have no recourse within the engine's reaction model.

### Implementation Guidance

1. In `WorkItemLifecycleAdapter.applyOutputMapping()` (or in a new pre-step before firing
   `CONTEXT_CHANGED`), write the actual `WorkItemStatus` string to the case context under a
   reserved key: `context.set("_workItemOutcome", status.name())`.
2. Case definitions can then gate conditions on `_workItemOutcome`:
   `{ "REJECTED": [...], "EXPIRED": [...], "ESCALATED": [...] }`.
3. Longer term: add `PlanItemStatus.REJECTED` alongside `COMPLETED`, `FAULTED`, `CANCELLED`
   so the plan model reflects the distinction structurally. This requires a `markRejected()` on
   `PlanItem` and handling in `SubCaseCompletionStrategy`.
4. `ESCALATED` specifically should not immediately fault — it should leave the PlanItem in a
   non-terminal state and fire `CONTEXT_CHANGED` so the case can re-evaluate routing.

**Scale:** S (context variable approach) or M (PlanItemStatus extension)
**Complexity:** Med — the context approach is safe and additive; the PlanItemStatus approach
requires changes to SubCaseCompletionStrategy and all callers

### Issue

casehubio/engine#338

---

## Finding 17 — CommitmentState.DELEGATED (Qhorus, terminal) ≠ WorkItemStatus.DELEGATED (work, non-terminal)

**Status:** Confirmed — original finding's "back-to-pool" framing inaccurate; real mismatch is
terminal semantics
**Batch:** M4
**Repos:** quarkus-qhorus, quarkus-work

### Verification

- **Code read:** `MessageType.HANDOFF`, `CommitmentState.DELEGATED`, `CommitmentService.delegate()`,
  `WorkItemService.delegate()`, `WorkItemStatus.isTerminal()`
- **Evidence:**
  - **Qhorus HANDOFF:** `MessageDispatch` requires a named `target`. On dispatch,
    `commitmentService.delegate(correlationId, target)` transitions the original Commitment to
    `CommitmentState.DELEGATED` (terminal for the original obligor) and creates a child
    Commitment for the target. HANDOFF is final for the sender.
  - **WorkItem DELEGATED:** `WorkItemService.delegate(id, toAssigneeId, actorId)` names a specific
    recipient, builds a `delegationChain`, sets `status = WorkItemStatus.PENDING` for the
    recipient to claim, and fires `lifecycleEvent("DELEGATED")`. `WorkItemStatus.isTerminal()`
    returns **false** for DELEGATED — the work is ongoing.
  - The original finding's "back-to-pool" characterisation is wrong — work DELEGATED names a
    specific recipient (not anonymous). The real mismatch: Qhorus DELEGATED = terminal; work
    DELEGATED = non-terminal continuation.

### Root Cause

Both systems model obligation transfer independently. In Qhorus, HANDOFF/DELEGATED follows the
normative commitment model where delegation ends the original obligation. In quarkus-work,
DELEGATED is a workflow transition that continues the item's lifecycle. Neither system was
designed with the other's vocabulary in mind.

### Blast Radius

Any integration code or documentation that bridges Qhorus HANDOFF to WorkItem delegation will
misapply terminal semantics. A developer reasoning about a case where an agent HANDOFFs a task
to a WorkItem DELEGATED path will expect the original obligation to end when work is delegated —
it does not. This creates invisible tracking gaps: the original obligor in Qhorus thinks they're
done; the WorkItem still shows them in the delegation chain as `owner`.

### Implementation Guidance

1. **Document the distinction clearly** in both codebases' javadoc:
   - `CommitmentState.DELEGATED`: "Terminal for the original obligor. Obligation fully
     transferred. Original Commitment is closed."
   - `WorkItemStatus.DELEGATED`: "Non-terminal. Work reassigned to a named actor; item remains
     active until completed, rejected, or cancelled."
2. **Consider renaming for clarity:**
   - Qhorus: `CommitmentState.TRANSFERRED` (makes the finality explicit)
   - Work: `WorkItemStatus.REASSIGNED` (distinguishes from the normative concept)
3. **Any future bridge between Qhorus HANDOFF and WorkItem delegation** must account for the
   terminal-semantics gap: the Qhorus side closes the obligation; the work side does not.

**Scale:** S — javadoc (immediate); renaming is M (cross-repo rename refactor)
**Complexity:** Low (docs only) to Med (rename requires protocol update and cross-repo sweep)

### Issue

casehubio/parent#54

---

## Batch M5 — SpawnGroup / Stage gap (finding 20)

Note: the original audit's "Stage concept" framing is misleading. No new CaseHub abstraction
is needed. This is a missing CDI observer in an existing adapter. The event infrastructure was
explicitly designed for engine routing (the javadoc says so) but never wired.

---

## Finding 20 — WorkItemGroupLifecycleEvent has no observer in casehub-engine

**Status:** Confirmed — scope correction: no new Stage concept needed; missing observer only
**Batch:** M5
**Repos:** casehub-engine (work-adapter), quarkus-work

### Verification

- **Code read:** `WorkItemGroupLifecycleEvent.java`, `WorkItemSpawnGroup.java`,
  `MultiInstanceGroupPolicy.java`, `WorkItemLifecycleAdapter.java`, engine `work-adapter` module
- **Evidence:**
  - `WorkItemGroupLifecycleEvent` javadoc: "Consumers subscribe to this for group-level
    outcomes: dashboards, notifications, **CaseHub routing**. The `callerRef` is echoed from
    the parent WorkItem so CaseHub can route outcomes without a query."
  - `callerRef` carries the `case:{caseId}/pi:{planItemId}` format that `WorkItemLifecycleAdapter`
    already parses for individual WorkItem events.
  - Engine search for `WorkItemGroupLifecycleEvent` observer: **zero results**.
  - Engine search for `SpawnGroup` or `multiInstance`: **zero results** — engine has no
    awareness of multi-instance WorkItem groups at all.
  - `WorkItemLifecycleAdapter` handles individual `WorkItemLifecycleEvent` only (line 65:
    `onWorkItemLifecycle(@ObservesAsync WorkItemLifecycleEvent event)`).
  - `WorkItemSpawnGroup` M-of-N completion: when `completedCount >= requiredCount`, fires
    `WorkItemGroupLifecycleEvent` with `groupStatus = COMPLETED` and the parent `callerRef`.
    The engine never sees this.

### Root Cause

`WorkItemGroupLifecycleEvent` was designed with CaseHub as an explicit consumer — the event
carries `callerRef` specifically for engine routing. The implementation was never wired. The
adapter that bridges work events to engine reactions (`WorkItemLifecycleAdapter`) was not
extended to handle the group-level event alongside the individual one.

### Blast Radius

A case definition cannot use multi-instance WorkItems (spawn N, wait for M to complete) as an
orchestration primitive. If a case spawns a SpawnGroup, the engine only sees individual child
WorkItem completions, not the group outcome. The case has no way to detect that M-of-N was
reached and continue. Any parallel-task pattern (fan-out to multiple reviewers, quorum decisions,
parallel document processing) is impossible to implement at the case level via quarkus-work.

### Implementation Guidance

This requires only a new observer method in `WorkItemLifecycleAdapter` — no new concept:

1. Add `@ObservesAsync WorkItemGroupLifecycleEvent groupEvent` handler in
   `WorkItemLifecycleAdapter`.
2. Parse `groupEvent.callerRef()` using the same `CallerRef.parse()` already used for
   individual events — the format is identical (`case:{caseId}/pi:{planItemId}`).
3. Look up the `PlanItem` from `BlackboardRegistry`. Based on `groupEvent.groupStatus()`:
   - `COMPLETED` → `item.markCompleted()`
   - `REJECTED` → `item.markFaulted()` (or `item.markRejected()` pending finding 16)
4. Apply output mapping from the parent WorkItem's `resolution` field (same as individual path).
5. Fire `CONTEXT_CHANGED` to trigger engine re-evaluation.
6. If `groupEvent.groupStatus() == COMPLETED` and `onThresholdReached` is `CANCEL`,
   remaining children are handled by quarkus-work internally — no engine action needed.

**Scale:** S — one new observer method + existing CallerRef parsing reused
**Complexity:** Low — the event carries all needed data; the adapter pattern is established

### Issue

casehubio/engine#339

---

## Batch M6 — Provenance + observability (findings 23, 29)

Cross-finding note: finding 23 is a small, focused gap in ledger capture — `callerRef` is
available but unused. Finding 29 is a larger structural gap — Qhorus has no OTel integration
at all. They share the theme of missing cross-repo observability. Different scope, different fix.

---

## Finding 23 — ProvenanceSupplement.hadPrimarySource not attached for case-spawned WorkItems

**Status:** Confirmed — one-line fix; the data is already in scope
**Batch:** M6
**Repos:** quarkus-work (casehub-work-ledger)

### Verification

- **Code read:** `LedgerEventCapture.onWorkItemEvent()`, `WorkItemSpawnGroup.javadoc`,
  `LedgerProvSerializer.hadPrimarySource`, `WorkItem.callerRef`
- **Evidence:**
  - `LedgerEventCapture` loads the full `WorkItem` via `workItemStore.get(event.workItemId())`
    on every lifecycle event. The `WorkItem.callerRef` field contains
    `case:{caseId}/pi:{planItemId}` for WorkItems spawned from a CaseHub case.
  - `LedgerEventCapture` attaches a `ComplianceSupplement` (rationale, planRef, detail,
    decisionContext) but never reads `callerRef` or attaches a `ProvenanceSupplement`.
  - `LedgerProvSerializer.hadPrimarySource` serialises `ProvenanceSupplement.hadPrimarySource`
    into PROV-DM export. For CaseHub-spawned WorkItems, this field is always absent.
  - The SPAWNED event handler sets `causedByEntryId` on child ledger entries (entry-to-entry
    causal chain) but this is an internal ledger link, not a PROV-DM `hadPrimarySource`.
  - Examples (`CreditDecisionScenario`, `ContentModerationScenario`) manually attach
    `ProvenanceSupplement` — demonstrating the API works but is never called automatically.

### Root Cause

`LedgerEventCapture` was written to capture operational compliance data (rationale, planRef,
decisionContext). PROV-DM provenance linking to an external source (the originating case) was
not included when the observer was written. The `callerRef` is parsed by `WorkItemLifecycleAdapter`
in the engine module but never by `LedgerEventCapture` in the ledger module.

### Blast Radius

PROV-DM provenance export for CaseHub-orchestrated WorkItems is structurally incomplete.
A `GET /ledger/prov/{workItemId}` response never contains `hadPrimarySource` for these items,
even though the relationship to the originating case exists and is known at write time. Any
downstream system consuming PROV-DM for audit or lineage (compliance, data governance) receives
an incomplete provenance graph — the link from WorkItem to the case that generated it is absent.

### Implementation Guidance

In `LedgerEventCapture.onWorkItemEvent()`, after the compliance supplement is attached, check
`callerRef` on the loaded `WorkItem` and attach a `ProvenanceSupplement` when present:

```java
workItemOpt.ifPresent(wi -> {
    if (wi.callerRef != null && !wi.callerRef.isBlank()) {
        final var prov = new ProvenanceSupplement();
        prov.hadPrimarySource = wi.callerRef; // e.g. "case:{uuid}/pi:{uuid}"
        entry.attach(prov);
    }
});
```

This is the complete fix. The `callerRef` is already available; `ProvenanceSupplement` is
already imported and used elsewhere in the module. Zero new infrastructure needed.

**Scale:** XS — three lines inside an existing method
**Complexity:** Low — data is in scope; pattern established in examples

### Issue

casehubio/work#223

---

## Finding 29 — Qhorus EVENT telemetry stored in DB columns, not OTel spans

**Status:** Confirmed
**Batch:** M6
**Repos:** quarkus-qhorus

### Verification

- **Code read:** `MessageType.java`, qhorus-wide search for `OpenTelemetry`, `traceId`
- **Evidence:**
  - `MessageType.EVENT` javadoc: "telemetry only, not delivered to agents." `isAgentVisible()`
    returns false for EVENT. EVENT messages go into the same `Message` / `MessageLedgerEntry`
    table as all other message types.
  - Full-project search for `OpenTelemetry` in qhorus: **zero results**.
  - Full-project search for `traceId` in qhorus: **zero results**.
  - No W3C trace context propagation in any Qhorus REST resource or message handler.
  - EVENT messages are stored as DB rows keyed to a `channelId` — they cannot be queried
    from Jaeger, Grafana Tempo, or any OTel-compatible backend.

### Root Cause

Qhorus was built as a standalone agent communication layer with its own persistence model.
OTel instrumentation was never added. The EVENT message type was intended to capture telemetry
but was implemented as a DB-backed record rather than an OTel span. There is no bridge between
Qhorus agent activity and the distributed trace context established by casehub-engine
(which does propagate W3C trace IDs via `PropagationContext.traceId`).

### Blast Radius

Agent decisions, COMMAND dispatches, HANDOFF chains, and DONE/FAILURE outcomes are invisible in
distributed traces. Correlating Qhorus agent activity with engine case execution (which has
proper OTel integration) requires manual DB joins — not possible in Jaeger/Grafana. Post-incident
analysis of cases that involved agents cannot trace agent decisions through the execution graph.
Any observability dashboard that relies on OTel traces for end-to-end case visibility is blind to
the Qhorus layer.

### Implementation Guidance

**Minimum viable (propagate context only):**
1. Extract W3C trace parent from HTTP headers on incoming Qhorus REST requests (MicroProfile
   or Quarkus OTel extension does this automatically if OTel is added to the classpath).
2. Add `traceId` and `spanId` fields to `MessageLedgerEntry` — populate from OTel context at
   write time. This makes EVENT records correlatable to the active trace without rewriting the
   storage model.

**Full OTel instrumentation:**
1. Emit OTel spans for COMMAND dispatch (`COMMAND sent → DONE/FAILURE received` = one span).
2. Emit OTel span events for HANDOFF chains (child spans per delegation hop).
3. Emit EVENT messages as OTel span events on the active span rather than (or in addition to)
   DB rows. This makes Qhorus telemetry natively visible in Jaeger.
4. Propagate trace context when Qhorus sends outbound HTTP calls (to agents, to casehub-engine).

**Scale:** M (context propagation only) or L (full instrumentation)
**Complexity:** Med (context propagation) to High (full span model for the message protocol)

### Issue

casehubio/qhorus#197
