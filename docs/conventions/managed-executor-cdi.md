# Convention: ManagedExecutor for CDI-Aware Concurrent Tests

**Applies to:** All Quarkus modules with tests requiring concurrent execution of CDI-managed code
**Severity:** Important — raw ExecutorService drops CDI context, silently breaking `@Transactional` on background threads

## The Problem

`@Transactional` and other CDI interceptors require an active CDI request context. When a raw `ExecutorService` (e.g. `Executors.newSingleThreadExecutor()`) spawns a thread, CDI context is not propagated. Any `@Transactional` call on that thread opens an unmanaged transaction or fails silently.

## The Rule

Inject `ManagedExecutor` from MicroProfile Concurrency instead of constructing a raw executor. `ManagedExecutor` propagates the Quarkus CDI context to spawned threads.

```java
// Wrong — CDI context not propagated
ExecutorService executor = Executors.newSingleThreadExecutor();
executor.submit(() -> service.doTransactionalWork()); // @Transactional silently broken

// Correct — CDI context propagated
@Inject ManagedExecutor executor;
executor.submit(() -> service.doTransactionalWork()); // @Transactional works
```

## Typical Use Case

Tests that run a blocking operation (e.g. a long-poll or `wait_for_reply`) concurrently with the main test thread, where both paths require transactional CDI beans.
