---
id: PP-20260508-d4e6c3
title: "@ObservesAsync methods with transactional logic must delegate to a separate bean"
type: rule
scope: platform
applies_to: "All modules with CDI async event observers"
severity: important
refs: []
violation_hint: "Combining @ObservesAsync and @Transactional on the same method causes transaction context issues"
created: 2026-05-08
---

# Convention: @ObservesAsync Methods With @Transactional Logic Must Delegate to a Separate Bean

**Applies to:** All modules with CDI async event observers  
**Severity:** Important — combining @ObservesAsync and @Transactional on the same method causes transaction context issues

## Problem

Annotating an `@ObservesAsync` method with `@Transactional` does not reliably start a transaction in the async thread. The CDI spec does not guarantee transaction propagation across the event dispatch boundary.

## Rule

Delegate all transactional work to a separate `@ApplicationScoped @Transactional` bean injected into the observer. The observer method itself carries no `@Transactional`.

## Example

```java
// Wrong
@ApplicationScoped
public class LedgerCapture {
    @ObservesAsync
    @Transactional  // unreliable
    void onEvent(WorkItemLifecycleEvent e) { ... }
}

// Right
@ApplicationScoped
public class LedgerCapture {
    @Inject LedgerCaptureService service;  // @Transactional lives here

    @ObservesAsync
    void onEvent(WorkItemLifecycleEvent e) {
        service.record(e);
    }
}
```
