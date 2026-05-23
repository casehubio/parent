# Platform Coherence Analysis — 2026-05-23

**Issue:** casehubio/parent#4
**Branch:** issue-4-platform-coherence-audit

## Status

| Batch | Theme | Findings | Done |
|-------|-------|----------|------|
| M1 | Worker selection intelligence | 2, 14, 15 | 3/3 ✅ |
| M2 | Audit trail documentation | 4, 6 | 0/2 |
| M3 | Notification + signal silo | 8, 9, 24, 25 | 0/4 |
| M4 | Integration boundary semantics | 16, 17 | 0/2 |
| M5 | SpawnGroup / Stage gap | 20 | 0/1 |
| M6 | Provenance + observability | 23, 29 | 0/2 |
| M7 | Architecture placement | 26 | 0/1 |
| M8 | Normative enforcement | 30, 32 | 0/2 |
| L1 | Verification required | 5 | 0/1 |
| L2 | Documentation + patterns | 11, 12 | 0/2 |
| L3 | Structural debt | 13, 19, 27 | 0/3 |

**Total:** 3 / 23 findings complete

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
