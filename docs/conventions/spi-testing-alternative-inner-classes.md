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
