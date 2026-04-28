# Atomic Threshold Counters

## Rule

When tracking M-of-N completion across concurrent transactions, use **explicit counter columns + `@Version` OCC + a `policyTriggered` flag** on the group entity. Do not use pessimistic locking (`PESSIMISTIC_WRITE`) and do not recount from the DB inside the child's transaction.

## Problem

A naive recount approach (`SELECT COUNT(*) WHERE status = COMPLETED`) inside the child completion transaction is unsafe at READ COMMITTED isolation (PostgreSQL default). Two concurrent child completions each read the other's write as uncommitted — both see count = M-1, neither triggers, and the group is permanently stuck at a satisfied threshold with no parent completion.

Pessimistic locking (`SELECT FOR UPDATE` on the parent) fixes correctness but serialises all child completions through a single row lock — a bottleneck that is unnecessary for human-task workloads.

## Solution

Add to the group entity:

```java
@Column(nullable = false)
public int completedCount = 0;

@Column(nullable = false)
public int rejectedCount = 0;

@Column(nullable = false)
public boolean policyTriggered = false;

@Version
public Long version = 0L;
```

When a child reaches a terminal status, in a single transaction:

1. Load the group entity (the `@Version` is captured).
2. Increment `completedCount` or `rejectedCount`.
3. If threshold is met AND `policyTriggered == false`: set `policyTriggered = true`, then complete or reject the parent.
4. Commit. If another transaction concurrently modified the group, `OptimisticLockException` fires.
5. On `OptimisticLockException`: retry once. On retry, `policyTriggered` will either be `true` already (do nothing — another transaction won the race correctly) or the count will be genuinely different (re-evaluate the threshold).

## Why the policyTriggered flag matters

`@Version` OCC prevents concurrent writes from both committing an inconsistent state. But in the rare case where two transactions both reach `count == M` before either commits, one wins and one retries. On retry the winner's commit is visible — `policyTriggered = true` — so the loser takes no action. Without the flag, the retrying transaction would fire parent completion a second time.

## When to use

Any feature that counts aggregate completions across concurrent operations and must trigger a one-time action when a threshold is reached. Examples: M-of-N WorkItem group completion, quorum voting, staged approval gates.

## When NOT to use

- In-process concurrency (single JVM, no DB persistence needed) → use `AtomicInteger.incrementAndGet() == M` instead.
- Extremely high throughput counters (millions/second) → consider the slotted counter pattern to reduce row contention.
- Human-task workloads are inherently low concurrency (completions happen minutes apart) — OCC conflicts will be vanishingly rare.

## Applies to

All casehubio modules implementing group completion semantics against a relational DB.
