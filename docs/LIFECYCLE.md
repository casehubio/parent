# CaseHub Lifecycle Coherence Protocol

Normative reference for all lifecycle state machines across the CaseHub platform.
Every enum that represents lifecycle states must be registered here and follow the rules below.

---

## Registered State Machines

| State machine | Repo | States | Terminal check method |
|---------------|------|--------|----------------------|
| `PlanItemStatus` | `casehub-engine` | `PENDING`, `RUNNING`, `DELEGATED`, `SUSPENDED`, `COMPLETED`, `FAULTED`, `REJECTED`, `OBSOLETE`, `CANCELLED` (9) | `isTerminal()`, `isActive()` |
| `WorkItemStatus` | `casehub-work` | `PENDING`, `ASSIGNED`, `IN_PROGRESS`, `DELEGATED`, `SUSPENDED`, `COMPLETED`, `REJECTED`, `FAULTED`, `CANCELLED`, `EXPIRED`, `ESCALATED`, `OBSOLETE` (12) | `isTerminal()`, `isActive()` |
| `CommitmentState` | `casehub-qhorus` | `OPEN`, `ACKNOWLEDGED`, `FULFILLED`, `DECLINED`, `FAILED`, `DELEGATED`, `EXPIRED` (7) | `isTerminal()`, `isActive()` |
| `SessionStatus` | `claudony` | `ACTIVE`, `WAITING`, `IDLE` (3) | — |

---

## Rules

### 1. Always use `isTerminal()` / `isActive()`

Consumer code must never enumerate lifecycle statuses explicitly to determine whether a state is terminal or active — except in a `switch` where each case has semantically distinct behaviour.

**Wrong:**
```java
if (status == COMPLETED || status == FAULTED || status == REJECTED || status == OBSOLETE) {
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

`CommitmentState.DELEGATED` (Qhorus) and `WorkItemStatus.DELEGATED` (work) use the same name with opposite terminal semantics:
- Qhorus `DELEGATED` is **terminal** — obligation transferred to a new debtor, original commitment closed.
- Work `DELEGATED` is **non-terminal** — work forwarded to a named actor for acceptance, item remains active.

Integration code bridging Qhorus commitment delegation to WorkItem delegation must not assume terminal semantics from the name alone. See PLATFORM.md — Gotchas section.

### 4. New state machines

When introducing a new lifecycle enum in any CaseHub repo:

1. Define `isTerminal()` and `isActive()` from the start.
2. Register the enum in this file before the first commit that uses it.
3. Add a capability ownership row in PLATFORM.md.

---

## References

- `engine#539` — added `OBSOLETE` to `PlanItemStatus`; `isTerminal()` / `isActive()` introduced as the single source of truth
- `engine#575` — PlanItemStatus class Javadoc omits `SUSPENDED` from active/terminal grouping
- `work#240` — lifecycle alignment: added `FAULTED`, `SUSPENDED`, `OBSOLETE` to `WorkItemStatus`; renamed `CREATED`→`PENDING`, `CLAIMED`→`ASSIGNED`; added `isActive()`
- `qhorus#309` — `CommitmentState` missing `isActive()` — lifecycle protocol compliance
- PLATFORM.md — Capability Ownership table (Durable PlanItem status row)
- PLATFORM.md — Gotchas (CommitmentState.DELEGATED vs WorkItemStatus.DELEGATED)
