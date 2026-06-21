# CaseHub Lifecycle Coherence Protocol

Normative reference for all lifecycle state machines across the CaseHub platform.
Every enum that represents lifecycle states must be registered here and follow the rules below.

---

## Registered State Machines

| State machine | Repo | States | Terminal check method |
|---------------|------|--------|----------------------|
| `PlanItemStatus` | `casehub-engine` | `PENDING`, `ENABLED`, `ACTIVE`, `RUNNING`, `COMPLETED`, `TERMINATED`, `FAILED`, `OBSOLETE` (8) | `isTerminal()`, `isActive()` |
| `WorkItemStatus` | `casehub-work` | `CREATED`, `CLAIMED`, `IN_PROGRESS`, `COMPLETED`, `REJECTED`, `CANCELLED`, `EXPIRED`, `DELEGATED`, `DELEGATION_DECLINED`, `ESCALATED` (10) | `isTerminal()` |
| `CommitmentState` | `casehub-qhorus` | `OPEN`, `FULFILLED`, `FAILED`, `EXPIRED`, `DECLINED`, `HANDOFF`, `CANCELLED` (7) | `isTerminal()` |
| `SessionStatus` | `claudony` | `ACTIVE`, `WAITING`, `IDLE` | — |

---

## Rules

### 1. Always use `isTerminal()` / `isActive()`

Consumer code must never enumerate lifecycle statuses explicitly to determine whether a state is terminal or active — except in a `switch` where each case has semantically distinct behaviour.

**Wrong:**
```java
if (status == COMPLETED || status == FAILED || status == TERMINATED || status == OBSOLETE) {
    // terminal logic
}
```

**Right:**
```java
if (status.isTerminal()) {
    // terminal logic
}
```

The set of terminal states is an implementation detail of the state machine. Adding a new terminal state (e.g. `OBSOLETE`) must not require changes in consumers.

### 2. Adding a new state

When adding a new state to any registered state machine:

1. **Update `isTerminal()` and `isActive()`** — if the new state is terminal, add it to `isTerminal()`. If it is active (in-flight), add it to `isActive()`. Both methods must remain exhaustive.
2. **Audit all consumers** — search all repos for any code that enumerates the status values explicitly (switch statements, if-chains, collections). Each must be reviewed and updated if necessary.
3. **Update this file** — update the state count in the table above.
4. **File cross-repo issues** — if consumer repos need updating, file issues on those repos. Do not commit to peer repos from the adding repo's session.
5. **Update PLATFORM.md** — update the capability ownership row for the affected state machine.

### 3. Cross-module state machine boundaries

`CommitmentState.DELEGATED` (Qhorus) and `WorkItemStatus.DELEGATED` (work) use the same word with opposite terminal semantics:
- Qhorus `DELEGATED` is **terminal** — obligation transferred, original commitment closed.
- Work `DELEGATED` is **non-terminal** — work reassigned, item remains active.

Integration code bridging a Qhorus HANDOFF to WorkItem delegation must not assume terminal semantics from the word alone. See PLATFORM.md — Gotchas section.

### 4. New state machines

When introducing a new lifecycle enum in any CaseHub repo:

1. Define `isTerminal()` and `isActive()` from the start.
2. Register the enum in this file before the first commit that uses it.
3. Add a capability ownership row in PLATFORM.md.

---

## References

- `engine#539` — added `OBSOLETE` to `PlanItemStatus`; `isTerminal()` / `isActive()` introduced as the single source of truth
- PLATFORM.md — Capability Ownership table (Durable PlanItem status row)
- PLATFORM.md — Gotchas (CommitmentState.DELEGATED vs WorkItemStatus.DELEGATED)
