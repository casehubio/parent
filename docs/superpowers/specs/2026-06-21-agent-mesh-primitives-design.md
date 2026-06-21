# Design: Agent Mesh Primitives — Extract to casehub-engine-api

**Issue:** casehubio/parent#93  
**Child issues:** engine#550, claudony#159, openclaw#38  
**Date:** 2026-06-21  
**Status:** Approved for implementation

---

## Problem

The normative agent mesh participation model — channel topology and participation level — lives in `claudony-casehub`. This is wrong: both concepts are platform primitives that any mesh agent needs, not claudony implementation details.

Drift has already started: `openclaw-casehub` has `OpenClawNormativeLayout`, an exact duplicate of claudony's `NormativeChannelLayout`. Its Javadoc already references parent#93 as the intended fix.

---

## Types Being Extracted

### Group 1: Channel Layout

**`CaseChannelLayout`** — SPI interface. Answers: "what channels should be created for this agent case?"

```java
// package io.casehub.api.spi.mesh
public interface CaseChannelLayout {

    List<ChannelSpec> channelsFor(UUID caseId, CaseDefinition definition);

    static CaseChannelLayout named(String configValue) {
        return switch (configValue) {
            case "normative" -> new NormativeChannelLayout();
            case "simple"    -> new SimpleLayout();
            default -> throw new IllegalArgumentException("Unknown channel layout: " + configValue);
        };
    }

    record ChannelSpec(
        String purpose,
        ChannelSemantic semantic,
        Set<MessageType> allowedTypes,
        Set<MessageType> deniedTypes,
        String description
    ) {}
}
```

**`NormativeChannelLayout`** — canonical 3-channel mesh implementation.

Per protocols `qhorus-human-governance-channel-types.md` and `channel-type-policy-invariant.md`:
- `work` — APPEND, no allowedTypes (all obligation-carrying types permitted)
- `observe` — APPEND, `allowedTypes = {EVENT}` (telemetry only, hard-blocked from obligation types)
- `oversight` — APPEND, `deniedTypes = {EVENT}` (advisory enforcement; obligation types permitted)

Note: oversight uses `deniedTypes=EVENT` per PP-20260604-a7ad99, not `allowedTypes=QUERY,COMMAND`. The older protocol (PP-20260508) is superseded.

**`SimpleLayout`** — 2-channel light implementation for cases not requiring human oversight.
- `work` — APPEND, no constraints
- `observe` — APPEND, `allowedTypes = {EVENT}`

Both are platform concepts — any mesh agent may want either variant.

---

### Group 2: Mesh Participation

**`MeshParticipationStrategy`** — SPI interface. Answers: "how actively does this agent participate in the mesh?"

```java
// package io.casehub.api.spi.mesh
public interface MeshParticipationStrategy {

    /**
     * Signature fix: was strategyFor(String workerId, WorkerContext context).
     * The old signature was a design lie — context was always null at the call site
     * (DESIGN.md line 540: "Outstanding: currently receives null for context").
     * caseId is directly available in buildContext() and is all per-case dispatch needs.
     * This fix is compliant with spi-case-id-parameter.md: direct UUID, not buried in a nullable wrapper.
     */
    MeshParticipation strategyFor(String workerId, UUID caseId);

    /**
     * NEW factory method — does not exist prior to this extraction.
     * Mirrors CaseChannelLayout.named() as a config-string API.
     * Replaces claudony's private selectStrategy() method.
     */
    static MeshParticipationStrategy named(String configValue) {
        return switch (configValue) {
            case "active"   -> new ActiveParticipationStrategy();
            case "reactive" -> new ReactiveParticipationStrategy();
            case "silent"   -> new SilentParticipationStrategy();
            default -> throw new IllegalArgumentException("Unknown mesh participation: " + configValue);
        };
    }

    enum MeshParticipation {
        /** Register on startup, post STATUS, check messages periodically. */
        ACTIVE,
        /** Do not register; only engage when directly addressed. */
        REACTIVE,
        /** No mesh participation. */
        SILENT
    }
}
```

**`ActiveParticipationStrategy`** — always returns `ACTIVE`. Pure logic, zero deps beyond interface. No longer imports `WorkerContext`.  
**`ReactiveParticipationStrategy`** — always returns `REACTIVE`. Pure logic. No longer imports `WorkerContext`.  
**`SilentParticipationStrategy`** — always returns `SILENT`. Pure logic. No longer imports `WorkerContext`.

All three verified: zero claudony-specific dependencies.

Note on per-case dispatch: `strategyFor(String workerId, UUID caseId)` passes caseId directly per `spi-case-id-parameter.md`. A future `PerCaseDynamicStrategy` dispatches per-case without any interface change.

---

## Package

New package: **`io.casehub.api.spi.mesh`** in `casehub-engine-api`.

Rationale: engine-api already uses sub-packages (`io.casehub.api.spi.routing`). The mesh types form a coherent group — channel layout + participation strategy together define the agent mesh participation model.

---

## Dependencies

`casehub-engine-api` already depends on `casehub-qhorus-api`.  
`MessageType` and `ChannelSemantic` are already available — **zero new dependencies**.

`CaseDefinition` is in `io.casehub.api.model` — already in engine-api.  
`WorkerContext` is no longer referenced by `MeshParticipationStrategy` — the signature fix removes that import from the interface and all three implementations.

Both claudony and openclaw already depend on `casehub-engine-api` — **zero new dependencies** in either consumer.

---

## Full Change Surface

### `casehub-engine` — api module (engine#550)

**Add** `io.casehub.api.spi.mesh`:
- `CaseChannelLayout` (interface + `ChannelSpec` record + `named()` factory)
- `NormativeChannelLayout`
- `SimpleLayout`
- `MeshParticipationStrategy` (interface + `MeshParticipation` enum + `named()` factory — **new code**, not a move)
- `ActiveParticipationStrategy`
- `ReactiveParticipationStrategy`
- `SilentParticipationStrategy`

**Add tests** in api test sources:
- `CaseChannelLayoutContractTest` — SPI contract: non-null return, no duplicate purposes, APPEND semantic invariant, no purpose/caseId/definition assumption; **plus** factory tests:
  - `named("normative")` returns instance producing 3 channels (work, observe, oversight)
  - `named("simple")` returns instance producing 2 channels (work, observe, no oversight)
  - `named("unknown")` throws `IllegalArgumentException`
- `NormativeChannelLayoutTest` — moved from claudony; verifies 3 channels, exact allowedTypes/deniedTypes per protocol. No extension — the `named()` factory tests above cover `NormativeChannelLayout` indirectly.
- `SimpleLayoutTest` — moved from claudony; verifies 2 channels, no oversight
- `MeshParticipationStrategyTest` — moved **and extended** from claudony; existing tests updated with the following distinction:
  - **Behavioral tests** (verify return value): `active_returnsActive`, `reactive_returnsReactive`, `silent_returnsSilent`, `threeDistinctValues`, `allStrategiesIgnoreWorkerId`, `resultsAreConsistentAcrossRepeatedCalls` — change second arg from `null` → `UUID.randomUUID()`. These test what the strategy returns; they should use a real caseId.
  - **Null-safety test** `allStrategiesAcceptNullContext` → rename to `allStrategiesAcceptNullCaseId`; keep `null` as the caseId arg. A null caseId is semantically valid — the strategy is called before a case exists. All three implementations ignore caseId, null must remain accepted.
  - `allStrategiesAcceptNullWorkerId`, `allStrategiesAcceptEmptyWorkerId`, enum tests — no arg changes needed.
  - **Must add** (behavioral, not structural):
  - `named("active").strategyFor("w", someUUID)` returns `MeshParticipation.ACTIVE`
  - `named("reactive").strategyFor("w", someUUID)` returns `MeshParticipation.REACTIVE`
  - `named("silent").strategyFor("w", someUUID)` returns `MeshParticipation.SILENT`
  - `named("unknown")` throws `IllegalArgumentException`

**No changes** to engine-api pom.xml — no new dependencies.

---

### `casehub-claudony` — casehub module (claudony#159)

**Delete** (types move to engine-api):
- `io.casehub.claudony.casehub.CaseChannelLayout`
- `io.casehub.claudony.casehub.NormativeChannelLayout`
- `io.casehub.claudony.casehub.SimpleLayout`
- `io.casehub.claudony.casehub.MeshParticipationStrategy`
- `io.casehub.claudony.casehub.ActiveParticipationStrategy`
- `io.casehub.claudony.casehub.ReactiveParticipationStrategy`
- `io.casehub.claudony.casehub.SilentParticipationStrategy`

**Delete tests** (move to engine-api):
- `NormativeChannelLayoutTest`
- `SimpleLayoutTest`
- `MeshParticipationStrategyTest`

**Update — `ClaudonyReactiveCaseChannelProvider`:**
- Import change: `CaseChannelLayout` and `ChannelSpec` now from `io.casehub.api.spi.mesh`
- `CaseChannelLayout.named(config.channelLayout())` still works — logic unchanged

**Update — `ClaudonyReactiveWorkerContextProvider`:**
- **Delete** `selectStrategy(String name)` private static method (lines 170–180)
- **Replace** its call at line 56 and 84 with `MeshParticipationStrategy.named(config.meshParticipation())`
- **Fix call site at line 109**: `strategy.strategyFor(workerId, null)` → `strategy.strategyFor(workerId, caseId)`. `caseId` is the parameter of `buildContext(String workerId, UUID caseId, WorkRequest task)` at line 108 — directly available, no structural change needed.
- **New explicit imports** (all previously same-package, no import needed; after migration to `io.casehub.api.spi.mesh` all require explicit import):
  - `io.casehub.api.spi.mesh.CaseChannelLayout`
  - `io.casehub.api.spi.mesh.MeshParticipationStrategy`
  - `io.casehub.api.spi.mesh.NormativeChannelLayout`
  - `io.casehub.api.spi.mesh.ActiveParticipationStrategy`

**Update — `docs/DESIGN.md`** (both changes to the same file, consolidated here):
- **Line 540 Outstanding note**: remove only the first clause: *"MeshParticipationStrategy.strategyFor() currently receives null for context (context not yet built at call time);"*. Preserve the second clause: *"shared-data keys from prior workers not yet included in the prompt (requires additional Qhorus integration, tracked as future work under epic #86)."*
- **Architecture section**: note that `CaseChannelLayout`, `NormativeChannelLayout`, `SimpleLayout`, `MeshParticipationStrategy` and its three standard implementations have moved to `io.casehub.api.spi.mesh` in engine-api; claudony retains `SimpleLayout` usage but the type definition is no longer local.

**Update tests** (import change only):
- `MeshSystemPromptTemplateTest` — `MeshParticipation` import update
- `ClaudonyReactiveCaseChannelProvider` tests — `CaseChannelLayout`, `ChannelSpec` import update
- `ClaudonyReactiveWorkerContextProviderTest` — `ActiveParticipationStrategy`, `NormativeChannelLayout` import updates (used at lines 111, 186, 218, 234); `strategyFor` call-site updates in strategy tests if any are inlined here

**No changes** to pom.xml — already depends on engine-api.

---

### `casehub-openclaw` — casehub module (openclaw#38)

**Background: shape mismatch.** `OpenClawNormativeLayout.ChannelSpec` has 3 fields: `{description, allowedTypes, deniedTypes}`. `CaseChannelLayout.ChannelSpec` has 5 fields: `{purpose, semantic, allowedTypes, deniedTypes, description}`. Migrating gains `purpose` and `semantic` fields not previously used by openclaw. The access pattern also changes from keyed-map to spec-list iteration. This is not a rename — it is a structural migration.

**Delete**:
- `io.casehub.openclaw.casehub.OpenClawNormativeLayout`
- `OpenClawNormativeLayoutTest`
- `docs/protocols/casehub/normative-layout-single-source.md` (PP-20260615-11b9d2) — **update, do not delete**. The rule survives; only the implementation pointer changes. Update:
  - **Title**: "All changes to the normative channel layout must go through `NormativeChannelLayout` in `casehub-engine-api`"
  - **Body**: "`NormativeChannelLayout` in `io.casehub.api.spi.mesh` (engine-api) is the single source of truth. Use `CaseChannelLayout.named("normative")` or construct `new NormativeChannelLayout()` directly. Do not define private `ChannelSpec` records or `LAYOUT` maps inside provider classes — this bypasses `NormativeChannelLayoutTest` value assertions in engine-api and re-introduces the duplication this extraction was designed to eliminate."
  - **violation_hint**: update from `OpenClawNormativeLayout`/`OpenClawNormativeLayoutTest` references to `NormativeChannelLayout`/`NormativeChannelLayoutTest` in `io.casehub.api.spi.mesh`

**Update — `OpenClawCaseChannelProvider` (sync):**

Current pattern:
```java
// openChannel(caseId, purpose):
OpenClawNormativeLayout.ChannelSpec spec = OpenClawNormativeLayout.LAYOUT.get(purpose); // O(1) map lookup
```

After migration:
```java
// Store layout instance as a field:
private final CaseChannelLayout layout = new NormativeChannelLayout();

// openChannel(caseId, purpose):
CaseChannelLayout.ChannelSpec spec = layout.channelsFor(caseId, null)
    .stream().filter(s -> s.purpose().equals(purpose)).findFirst()
    .orElseThrow(() -> new IllegalArgumentException(
            "Unknown channel purpose '" + purpose + "' for case " + caseId));
```

This is O(3) for a 3-element list — effectively constant and not a performance concern. The caseId is passed correctly, respecting the SPI contract that layouts may vary by case. A constructor-time Map cache built from `channelsFor(null, null)` was considered and rejected: it bakes in the assumption that the layout is caseId-independent, violating the parameterization contract of `channelsFor(UUID caseId, ...)`.

`orElseThrow` replaces the previous `spec != null ? spec.x() : null` fallback (which silently created an unconstrained channel for unknown purposes). The reactive provider already throws for unknown purposes via the existing `if (ch == null) throw new IllegalArgumentException(...)` in its `openChannel()` — the sync provider was the gap.

**Update — `ReactiveOpenClawCaseChannelProvider` (reactive):**

This is a refactor, not an import update. The sync provider and reactive provider have fundamentally different structures and must be migrated separately.

Current `initializeLayout(caseId)`:
```java
List<String> purposes = OpenClawNormativeLayout.LAYOUT.keySet().stream().sorted().toList();
// ... reduces over purposes, calling openOrCreate(caseId, purpose) for each
```

Current `openOrCreate(caseId, purpose)`:
```java
OpenClawNormativeLayout.ChannelSpec spec = OpenClawNormativeLayout.LAYOUT.get(purpose); // SECOND lookup
String description = spec != null ? spec.description() : purpose;
Set<MessageType> allowedSet = spec != null ? spec.allowedTypes() : null;
Set<MessageType> deniedSet  = spec != null ? spec.deniedTypes() : null;
```

After migration:
1. Refactor `openOrCreate(UUID caseId, String purpose)` → `openOrCreate(UUID caseId, CaseChannelLayout.ChannelSpec spec)`. The method receives the spec directly — no second lookup.
2. Refactor `initializeLayout(caseId)` to call `layout.channelsFor(caseId, null)` once and iterate the `List<ChannelSpec>` directly, passing each spec to the refactored `openOrCreate(caseId, spec)`. The `keySet().stream().sorted()` pattern disappears entirely.

After migration:
```java
// initializeLayout(caseId):
List<CaseChannelLayout.ChannelSpec> specs = layout.channelsFor(caseId, null);
// reduce over specs, calling openOrCreate(caseId, spec) for each

// openOrCreate(UUID caseId, CaseChannelLayout.ChannelSpec spec):
String channelName = CaseChannel.channelName(caseId, spec.purpose());
// use spec.description(), spec.allowedTypes(), spec.deniedTypes() directly
```

This eliminates the second map lookup and is architecturally cleaner than the current pattern.

**Update tests:**
- `OpenClawCaseChannelProviderTest` — no structural change needed; `OpenClawNormativeLayout` was never imported by the test; existing assertions on `allowedTypes`/`deniedTypes` values continue to hold since `NormativeChannelLayout` produces identical constraints. Add one test: `openChannel_unknownPurpose_throws` verifying `IllegalArgumentException` is thrown (bonus fix made this testable where previously it silently succeeded).
- `ReactiveOpenClawCaseChannelProviderTest` — verify tests pass without structural change. `openOrCreate` is private and never called directly by the test; assertions on channel count and type constraints hold unchanged since `NormativeChannelLayout` produces identical constraints.

**No changes** to pom.xml — already depends on engine-api.

---

### `casehub-parent` — docs

**Update `docs/PLATFORM.md`** — Capability Ownership table, add rows:
- `CaseChannelLayout SPI + normative/simple layouts` → `casehub-engine-api` (`io.casehub.api.spi.mesh`)
- `MeshParticipationStrategy SPI + standard implementations` → `casehub-engine-api` (`io.casehub.api.spi.mesh`)

**Update `docs/CHANNELS.md`** — coordination channels section: add class references (`CaseChannelLayout`, `NormativeChannelLayout`, `io.casehub.api.spi.mesh`); note `MeshParticipationStrategy` as a companion concept in the same package

**Update `docs/repos/claudony.md`** — note `CaseChannelLayout` and `MeshParticipationStrategy` now in engine-api; claudony implements `SimpleLayout` and the three standard participation strategies

---

### `casehub/garden` — protocols

**Update `casehub/garden/docs/protocols/casehub/spi-case-id-parameter.md`** — protocol table at lines 81–82:

Before:
```
| claudony | `CaseChannelLayout`         | ✅ `channelsFor(UUID caseId, ...)` |
| claudony | `MeshParticipationStrategy` | ✅ `WorkerContext` carries `UUID caseId` |
```

After:
```
| engine-api | `CaseChannelLayout`         | ✅ `channelsFor(UUID caseId, ...)` |
| engine-api | `MeshParticipationStrategy` | ✅ `strategyFor(String workerId, UUID caseId)` — direct parameter |
```

This is a 2-line change. It is in scope, not a follow-up.

---

## Cross-Repo Documentation (per repo)

**engine** — update deep-dive doc: note `io.casehub.api.spi.mesh` package; add `CaseChannelLayout` and `MeshParticipationStrategy` to API surface; update ARC42STORIES.MD for integration SPIs section

**claudony** — update ARC42STORIES.MD (DESIGN.md changes are detailed in the claudony source section above)

**openclaw** — update docs: note `OpenClawNormativeLayout` removed; update ARC42STORIES.MD

---

## Implementation Order

1. **engine-api first** — add all types and tests; publish (or install locally)
2. **claudony and openclaw in parallel** — both remove local copies; both already depend on engine-api

Within engine-api: TDD order — write contract test, add `CaseChannelLayout` + `ChannelSpec`; write `NormativeChannelLayoutTest`, add `NormativeChannelLayout`; write `SimpleLayoutTest`, add `SimpleLayout`; write `MeshParticipationStrategyTest` (including `named()` factory tests), add `MeshParticipationStrategy` + three impls.

---

## Protocol Compliance

| Protocol | Compliance |
|----------|-----------|
| `module-tier-structure.md` | ✅ engine-api is Tier 1; all new types are pure Java, zero JPA/Quarkus |
| `library-jars-require-jandex.md` | ✅ engine-api already has jandex-maven-plugin configured |
| `qhorus-human-governance-channel-types.md` | ✅ oversight uses `deniedTypes={EVENT}` per PP-20260604-a7ad99 (PP-20260508 is superseded) |
| `channel-type-policy-invariant.md` | ✅ COMMAND/QUERY hard-enforced via allowedTypes on observe; oversight uses advisory deniedTypes per PP-20260604-a7ad99 |
| `spi-case-id-parameter.md` | ✅ `channelsFor(UUID caseId, ...)` passes caseId directly; `strategyFor(String workerId, UUID caseId)` passes caseId directly (signature fix from WorkerContext); protocol table rows updated from claudony → engine-api |
| `spi-default-method-contract-test.md` | ✅ `CaseChannelLayoutContractTest` covers SPI invariants |
| `ci-dispatch-covers-direct-consumers.md` | ✅ engine already dispatches to claudony and openclaw; no new dispatch paths needed |

---

## What Is NOT in Scope

- `MeshSystemPromptTemplate` — stays in claudony (builds Claude-specific system prompts; import update only)
- `AgentCase` / `CaseChannelProvider` implementations — stays in claudony
- Any claudony Quarkus/CDI beans — stays in claudony
- `CaseChannelLayout` as engine `@DefaultBean` — engine does not inject `CaseChannelLayout`; no `@DefaultBean` needed
- `MeshParticipationStrategy` injection by engine — provider implementations inject it themselves
- Injection refactor of openclaw providers (currently hardcode NormativeChannelLayout; making it config-driven like claudony is a future improvement, not in this issue)

---

## Follow-up Issues to File

- **parent#NNN** — formalise `MeshParticipationStrategy` in CHANNELS.md taxonomy (currently undocumented as a channel primitive)
- **engine#NNN** — consider whether engine should expose `CaseChannelLayout` as a discoverable SPI (currently invisible to engine; `CaseChannelProvider` is the boundary)
- **engine#NNN** — per-case dynamic participation: `PerCaseDynamicStrategy` implementing `MeshParticipationStrategy` receives `caseId` directly via `strategyFor(workerId, caseId)`; no interface change needed (belongs on engine repo now that the SPI lives there)
- **openclaw#NNN** — make channel layout config-driven: align openclaw providers with claudony's `channelLayout` config property and `CaseChannelLayout.named()` pattern; currently hardcodes `NormativeChannelLayout`
