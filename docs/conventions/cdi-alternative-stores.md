# Convention: CDI Alternative Stores in Tests

**Applies to:** All modules using `@Alternative @Priority(1)` in-memory store implementations for testing
**Severity:** Important — Panache statics silently bypass alternatives, returning empty results with no error

## The Problem

Panache static query methods (`Entity.<Entity>find()`, `Entity.listAll()`, `Entity.count()`, etc.) resolve directly against JPA, bypassing CDI entirely. `@Alternative @Priority(1)` store implementations are CDI beans — they intercept calls made through injected interfaces, not through static Panache entry points.

When InMemory stores are active via `quarkus.arc.selected-alternatives`, the JPA entity tables are empty. Any Panache static query on those entities returns zero results, silently.

## The Rule

In test code that activates InMemory stores: **never use Panache statics to query domain entities.** Always go through the store or service layer.

```java
// Wrong — bypasses CDI alternative, queries empty JPA table
List<Channel> channels = Channel.<Channel>listAll();

// Correct — routes through the injected alternative store
List<Channel> channels = channelStore.findAll();
// or via tool layer
var result = tools.listChannels();
```

## Where This Applies

Any module that declares `quarkus.arc.selected-alternatives` with InMemory store implementations in `src/test/resources/application.properties`. The pattern is common across casehub-qhorus, casehub-ledger, and casehub-work test suites.
