---
id: PP-20260520-98b57d
title: "Strategy SPIs must pass caseId through all method signatures — not just at construction time"
type: rule
scope: platform
applies_to: "All casehub repos that define or implement strategy SPIs (engine, claudony, qhorus, and future modules)"
severity: important
refs:
  - docs/protocols/casehub/platform-spi-contract.md
violation_hint: "SPI method takes no caseId — a future PerCaseDynamicStrategy cannot delegate per-case without changing all call sites"
created: 2026-05-20
---

# Protocol: Strategy SPIs Must Pass caseId Through All Methods

**Applies to:** All casehub repos that define strategy SPIs — engine, claudony, qhorus, and any future module  
**Severity:** Important — violations require call-site changes to retrofit per-case dispatch later

---

## Rule

Every strategy SPI method that operates on a case instance must accept `caseId` (or an
equivalent case-scoped identifier) as an explicit parameter. The caseId must be passed
at every call site, not stored at construction time.

```java
// ✅ Correct — caseId flows through every method
interface CaseWorkerUpdateStrategy {
    void onLifecycleEvent(String caseId, LifecycleEvent event);
    Multi<String> subscribe(String caseId, Supplier<String> snapshotFn);
}

// ❌ Wrong — caseId captured at construction; strategy locked to one case
interface CaseWorkerUpdateStrategy {
    void onLifecycleEvent(LifecycleEvent event);   // caseId stored in impl field
    Multi<String> subscribe(Supplier<String> snapshotFn);
}
```

---

## Why

Current strategy SPIs are startup-time selections — `application.properties` chooses one
implementation for the lifetime of the JVM. This is intentional and appropriate for most
deployments. However, the door must be left open for a future `PerCaseDynamicStrategy`
that dispatches to different sub-strategies per case instance:

```java
class PerCaseDynamicStrategy implements CaseWorkerUpdateStrategy {
    void onLifecycleEvent(String caseId, LifecycleEvent event) {
        resolveFor(caseId).onLifecycleEvent(caseId, event);  // caseId still flows
    }

    private CaseWorkerUpdateStrategy resolveFor(String caseId) {
        // look up per-case priority, channel layout, custom config, etc.
    }
}
```

If existing SPIs do not pass `caseId`, every call site must be updated when this
implementation is added. If they do pass `caseId`, the implementation is a new class
with no call-site changes.

The cost of compliance is a single extra parameter at definition time. The cost of
violation is a cross-repo refactor touching every call site.

---

## Scope

**Applies to strategy SPIs** — those where the implementation may vary or be swapped.
Does not apply to repository interfaces, event publishers, or utility SPIs where
dispatching per case makes no sense.

Known SPIs to comply:

| Repo | SPI | Status |
|------|-----|--------|
| claudony | `CaseChannelLayout` | ✅ `channelsFor(UUID caseId, ...)` |
| claudony | `MeshParticipationStrategy` | ✅ `WorkerContext` carries `UUID caseId` |
| claudony | `CaseWorkerUpdateStrategy` | ✅ `onLifecycleEvent(String caseId)`, `subscribe(String caseId, ...)` |
| engine | `WorkerProvisioner` | ✅ `ProvisionContext` carries `UUID caseId` |
| engine | `WorkerContextProvider` | ✅ `buildContext(String workerId, UUID caseId, ...)` |
| engine | `CaseChannelProvider` | ✅ `openChannel(UUID caseId, ...)`, `listChannels(UUID caseId)` |
| qhorus | `MessageTypePolicy` | ✅ validates per channel semantic, not per case — caseId not needed |
| qhorus | `InstanceActorIdProvider` | ✅ session→persona mapping, not case-scoped — caseId not needed |

All existing SPIs comply as of 2026-05-20. This rule governs **new** strategy SPIs going forward.

---

## Not Doing Now

Full per-case strategy dispatch (`CaseStrategyRegistry`, per-case config storage,
fleet-wide replication) is deferred. This protocol only ensures the interface design
leaves the door open. No `PerCaseDynamicStrategy` implementation is required.
