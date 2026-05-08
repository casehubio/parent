---
id: PP-20260508-904291
title: "Test SPI wiring with @Alternative static inner classes, not Mockito mocks"
type: rule
scope: platform
applies_to: "All modules with CDI SPI implementations"
severity: important
refs: []
violation_hint: "Injecting mock SPI implementations via Mockito fails with Quarkus CDI; wrong bean injected silently"
created: 2026-05-08
---

# Convention: Test SPI Wiring With @Alternative Static Inner Classes

**Applies to:** All modules with CDI SPI implementations  
**Severity:** Important — injecting mock SPI implementations via Mockito fails with Quarkus CDI

## Problem

Quarkus CDI resolves beans at augmentation time. You cannot inject Mockito mocks or anonymous classes as CDI alternatives at test time.

## Rule

Define SPI test doubles as `@Alternative @Priority(1) @ApplicationScoped` static inner classes within the test class. Use static fields to record invocations. Reset in `@BeforeEach`.

## Example

```java
@QuarkusTest
class WorkerProvisionerTest {
    @Alternative @Priority(1) @ApplicationScoped
    static class RecordingProvisioner implements WorkerProvisioner {
        static List<ProvisionContext> calls = new ArrayList<>();
        @Override public Worker provision(ProvisionContext ctx) {
            calls.add(ctx); return Worker.noop();
        }
    }

    @BeforeEach void reset() { RecordingProvisioner.calls.clear(); }
}
```
