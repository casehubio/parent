# Convention: CDI fireAsync() Inside @Transactional Dispatches Immediately, Not at Commit

**Applies to:** All modules using CDI async events  
**Severity:** Important — observers can run before the triggering transaction commits, causing stale reads

## Problem

Calling `event.fireAsync()` inside a `@Transactional` method dispatches the event immediately on a separate thread, not after the transaction commits. If the observer reads the database, it may not see the uncommitted changes.

## Rule

Call `fireAsync()` after the transaction boundary, or use a `@Transactional(REQUIRES_NEW)` wrapper that commits before dispatching. Alternatively, structure the observer to tolerate eventual consistency.

## Example

```java
// Wrong — observer may run before transaction commits
@Transactional
void save(WorkItem item) {
    repo.persist(item);
    event.fireAsync(new WorkItemEvent(item)); // dispatches now, not after commit
}

// Right — fire after commit
void save(WorkItem item) {
    saveTransactional(item);            // commits
    event.fireAsync(new WorkItemEvent(item)); // fires after
}
```
