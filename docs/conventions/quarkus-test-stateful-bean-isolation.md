# Convention: Stateful @ApplicationScoped Beans Don't Reset Between @QuarkusTest Classes

**Applies to:** All modules with stateful @ApplicationScoped beans and multiple @QuarkusTest classes  
**Severity:** Important — shared bean state causes flaky tests that pass in isolation but fail in suite runs

## Problem

All `@QuarkusTest` classes in a module share one Quarkus application instance. State accumulated in `@ApplicationScoped` beans (rate limiters, registries, caches) persists across test classes.

## Rule

1. Use unique identifiers per test to avoid cross-test interference
2. Expose `package-private resetForTest()` or `setClockForTest()` hooks on stateful beans
3. Call reset hooks in `@AfterEach` in every test class that uses the stateful bean

## Example

```java
// In the bean
@ApplicationScoped
public class AuthRateLimiter {
    void resetForTest() { this.state.clear(); }  // package-private
}

// In the test
@AfterEach
void cleanup() { rateLimiter.resetForTest(); }
```
