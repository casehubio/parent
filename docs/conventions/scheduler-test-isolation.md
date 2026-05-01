# Convention: Scheduler Isolation in Tests

**Applies to:** All modules with `@Scheduled` beans that interact with database state
**Severity:** Important — scheduler can pick up committed test data and fire spurious side effects

## The Problem

`@Scheduled` methods run on a **separate Quarkus thread** with their own transaction. They cannot see data inside a `@TestTransaction` (uncommitted), but they **can** see any committed data — including entities created in `@BeforeEach` via `@Transactional` service calls.

A test that creates persistent state in `@BeforeEach` and then calls a service directly may race against the scheduler, which sees the committed setup data and triggers side effects (alerts, expiry, event emission) that interfere with the test's assertions.

## Rules

**Use `@TestTransaction` on test methods** that invoke service logic the scheduler also drives — uncommitted test data is invisible to the scheduler's separate transaction.

**Use unique entity names per test** (e.g. UUID suffix) when tests create persistent entities the scheduler queries. This prevents committed entities from prior tests triggering spurious scheduler runs in subsequent tests.

**Do not call the evaluation service directly in tests** that also have the `@Scheduled` driver active — both code paths will run and double-fire side effects.

## Standard Pattern

```java
@Test
@TestTransaction  // uncommitted — scheduler cannot see this
void myTest() {
    String name = "test-" + UUID.randomUUID();
    // set up, assert — scheduler sees nothing
}
```
