# Convention: Enforce Blocking/Reactive SPI Parity With a Reflection Test

**Applies to:** All modules that define a blocking SPI interface and a reactive mirror of it  
**Severity:** Important — missing reactive methods silently break consumers building reactive services

## Problem

When a blocking SPI (`LedgerEntryRepository`) and its reactive mirror (`ReactiveLedgerEntryRepository`) evolve independently, method additions to the blocking interface are not added to the reactive one. The compiler doesn't catch this — no concrete implementation of the reactive SPI lives in the extension module, so nothing fails to compile. Consumers discover the gap when they try to use a method that doesn't exist.

## Rule

Write a plain JUnit test (no `@QuarkusTest`) that uses reflection to assert every method name on the blocking SPI is also present on the reactive SPI. Maintain an explicit exclusion set for methods that are intentionally blocking-only (e.g. batch operations that have no reactive equivalent).

## Example

From `casehub-ledger` (`ReactiveRepositoryIT`):

```java
@Test
void reactiveSpi_coversAllBlockingSpiMethods() {
    Set<String> blockingNames = Arrays.stream(LedgerEntryRepository.class.getDeclaredMethods())
            .map(Method::getName)
            .collect(Collectors.toSet());
    Set<String> reactiveNames = Arrays.stream(ReactiveLedgerEntryRepository.class.getDeclaredMethods())
            .map(Method::getName)
            .collect(Collectors.toSet());
    // findAllEvents is a batch concern with no reactive equivalent
    blockingNames.remove("findAllEvents");
    assertThat(reactiveNames)
            .as("ReactiveLedgerEntryRepository must cover all LedgerEntryRepository methods")
            .containsAll(blockingNames);
}
```

## Notes

- No `@QuarkusTest` needed — this is a pure reflection check, no CDI context required.
- The reactive SPI uses `Uni<T>` return types; the test only checks method names, not signatures.
- Add a companion test asserting every method on the reactive SPI returns `Uni<?>` to prevent accidental blocking return types creeping in.
- Document intentional exclusions with a comment stating why the method is blocking-only.
