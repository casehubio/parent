# Protocol: Dual-Trail Audit Pattern

**Applies to:** `casehub-engine`, `casehub-work`, and any future CaseHub module that writes both
an operational trail and a compliance ledger.

---

## The Pattern

Both `casehub-engine` and `casehub-work` maintain two parallel audit mechanisms that serve
different purposes. The split is architecturally sound and intentional:

| | casehub-engine | casehub-work |
|---|---|---|
| **Operational trail** | `EventLog` | `AuditEntry` |
| **Compliance ledger** | `CaseLedgerEntry` | `WorkItemLedgerEntry` |

**Operational trail** — append-only, plain JPA, synchronous, queryable at runtime. No hash
chain. The word "immutable" in javadoc means append-only, NOT tamper-evident. Use for
observability and runtime queries only.

**Compliance ledger** — extends `LedgerEntry`, Merkle-chained, `sequenceNumber + digest`,
written by CDI observer in a separate transaction. Eventual consistency. Optional module
(`LedgerConfig.enabled()`). This is the authoritative record for regulatory audit.

---

## Governing Rules

1. **All lifecycle transitions MUST fire a CDI lifecycle event.** The ledger observer captures
   automatically. A state transition that writes only to the operational trail and omits the
   CDI event produces an operational log entry but no compliance record.

2. **Operational trails are for observability only.** `EventLog` and `AuditEntry` serve
   runtime queries, restart recovery, and debugging. They are not tamper-evident and must
   never be cited as compliance evidence.

3. **Compliance queries MUST read from `LedgerEntryRepository` subclasses.** `CaseLedgerEntry`
   and `WorkItemLedgerEntry` are the authoritative records. The compliance ledger is optional
   (`LedgerConfig.enabled()`) — if it is disabled, the deployment has no compliance trail.

4. **Trust score computation reads from the ledger.** In `casehub-work`, trust scores read
   `WorkItemLedgerEntry`. A state transition that omits the CDI event silently corrupts trust
   score computation — no test will catch this unless the CDI path is explicitly covered.

---

## Failure Modes — `CaseLedgerEventCapture`

`CaseLedgerEventCapture.onCaseLifecycleEvent()` is `@ObservesAsync @Transactional`. The ledger
write runs in a separate transaction from the case state update. This is intentional: eventual
consistency is acceptable.

The failure path is not handled automatically:
- If the async ledger write fails, the error is logged at WARN level and swallowed.
- No retry, no dead-letter queue, no alert.
- The case state committed; the ledger record is missing.
- The compliance record is silently absent.

**quarkus-work is not affected** — `LedgerEventCapture` in work uses `@Observes` (same
transaction), so ledger write failure rolls back the state transition too.

### Detection

A divergence between operational trail and compliance ledger can be detected by:

```sql
-- Cases with EventLog entries but no corresponding CaseLedgerEntry
SELECT el.case_id, COUNT(el.id) AS event_count,
       COUNT(cle.id) AS ledger_count
FROM event_log el
LEFT JOIN case_ledger_entry cle ON el.case_id = cle.case_id
GROUP BY el.case_id
HAVING COUNT(el.id) > COUNT(cle.id);
```

### Remediation

Missing ledger entries can be replayed from `EventLog` — the event log is the source of
truth for what happened; the ledger entry records it tamper-evidently.

### Recommended improvement (not yet implemented)

Change the error handler in `CaseLedgerEventCapture` from LOG.warn to also fire a
`LedgerWriteFailedEvent`. A retry handler (`@ObservesAsync @Transactional`) retries with
exponential back-off. After N failures, raise an alert (metric increment or DLQ entry).

---

## Writing Rule for Developers

When adding a new lifecycle state transition to engine or work:

1. Write to the operational trail (EventLog / AuditEntry) ✅ already done if the lifecycle
   path calls the audit method
2. Fire the CDI lifecycle event (`CaseLifecycleEvent` / `WorkItemLifecycleEvent`) — **do not skip**
3. Assert in tests: for every transition, both an operational trail entry AND a ledger entry
   are written. A test that only checks the operational trail gives false confidence.

---

**Refs:** casehubio/parent#52, casehubio/parent#59
