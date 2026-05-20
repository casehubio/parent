---
id: PP-20260520-650742
title: "Dedicated @ApplicationScoped writer bean for shared LedgerEntry sequenceNumber ownership"
type: rule
scope: application
applies_to: "Any harness where more than one service writes entries of the same LedgerEntry subtype for the same subject"
severity: important
refs:
  - docs/protocols/casehub/ledger-subclass-extension.md
violation_hint: "Multiple services independently calling findLatestBySubjectId with no shared owner — concurrent writes can produce duplicate sequence numbers for the same subject"
created: 2026-05-20
---

# Protocol: Dedicated Ledger Writer Bean

**Applies to:** Any harness where more than one service writes entries of the same `LedgerEntry`
subtype for the same subject  
**Severity:** Important — violations leave the sequence number invariant untestable and create
a concurrent-write race

---

## Rule

When two or more services in a harness application write entries of the same `LedgerEntry`
subtype for the same subject, extract a single `@ApplicationScoped` writer bean that:

1. **Owns `sequenceNumber` computation** via `LedgerEntryRepository.findLatestBySubjectId()`
2. **Provides named construction methods** per entry type (e.g. `writeCommandEntry`, `writeResolutionEntry`)
3. **Is the only code that calls `ledgerEntryRepository.save()`** for that entry type

Do not let each service independently read the latest sequence number. There is no single place
to test the invariant, and two callers reading before either has flushed will compute the same
sequence number.

---

## Why

`sequenceNumber` forms the position in a per-subject audit chain. `findLatestBySubjectId`
reads the latest committed row to compute `latest + 1`. If two services call this independently
— whether concurrently or in rapid succession before a flush — both may read the same latest
entry and assign the same position. The ledger has no unique constraint on
`(subject_id, sequence_number)` because the sequence is computed at write time, not enforced
at the database level.

Centralising all writes in one bean means:

- The sequence number invariant has exactly one owner, testable in isolation with a mocked repository
- Call sites are named and typed (`writeCommandEntry`, `writeResolutionEntry`), not raw entity construction
- GCP/ICH/regulatory audit requirements that mandate both ends of a lifecycle chain (e.g. COMMAND + resolution) are expressed as a cohesive API rather than scattered save calls

---

## Reference Implementation

`io.casehub.clinical.service.DeviationLedgerWriter` in `casehub-clinical` (clinical#14):

```java
@ApplicationScoped
public class DeviationLedgerWriter {

    @Inject LedgerEntryRepository ledgerEntryRepository;
    @Inject Clock clock;

    public void writeCommandEntry(ProtocolDeviation dev, String piId) {
        ProtocolDeviationLedgerEntry entry = baseEntry(dev);
        entry.entryType = LedgerEntryType.COMMAND;
        // ... field population
        ledgerEntryRepository.save(entry);
    }

    public void writeResolutionEntry(ProtocolDeviation dev, PiApprovalStatus status,
                                     String actorId, ActorType actorType, String actorRole) {
        ProtocolDeviationLedgerEntry entry = baseEntry(dev);
        entry.entryType = LedgerEntryType.EVENT;
        // ... field population
        ledgerEntryRepository.save(entry);
    }

    private ProtocolDeviationLedgerEntry baseEntry(ProtocolDeviation dev) {
        ProtocolDeviationLedgerEntry entry = new ProtocolDeviationLedgerEntry();
        entry.id = UUID.randomUUID();
        entry.subjectId = dev.id;
        entry.sequenceNumber = nextSequenceNumber(dev.id);
        // ... shared fields
        return entry;
    }

    private int nextSequenceNumber(UUID subjectId) {
        return ledgerEntryRepository.findLatestBySubjectId(subjectId)
            .map(e -> e.sequenceNumber + 1)
            .orElse(1);
    }
}
```

---

## When This Rule Applies

**Applies** when the same `LedgerEntry` subtype can be written by two or more services:

- `ServiceA` writes a `COMMAND` entry, `ServiceB` writes a resolution entry, both for the same subject
- A scheduled job and a REST-triggered service both write the same entry type
- Three services each contribute a phase of an audit trail for the same entity

**Does not apply** when only one service ever writes a given subtype:

- A single service writes all entries for its subtype and no other code path calls `save()` on it
- In this case, sequenceNumber computation can live directly in the service with no shared owner problem

---

## Testing

A writer bean is testable in isolation with a mocked `LedgerEntryRepository`. The
sequence number logic — `findLatestBySubjectId().map(e -> e.sequenceNumber + 1).orElse(1)` —
is verifiable without a database. Each named write method can be tested for correct
field population independently of the services that call it.

```java
@QuarkusTest
class DeviationLedgerWriterTest {

    @InjectMock LedgerEntryRepository repo;
    @Inject DeviationLedgerWriter writer;

    @Test
    void sequenceNumberStartsAt1WhenNoExistingEntries() {
        when(repo.findLatestBySubjectId(any())).thenReturn(Optional.empty());
        writer.writeCommandEntry(deviation(), PI_ID);
        ArgumentCaptor<ProtocolDeviationLedgerEntry> cap = ArgumentCaptor.forClass(...);
        verify(repo).save(cap.capture());
        assertThat(cap.getValue().sequenceNumber).isEqualTo(1);
    }
}
```

---

## Scope Note

The race condition this rule prevents exists wherever multiple independent callers write the
same entry type for the same subject — not only in harness applications. It surfaces most
frequently in harness apps because domain orchestration naturally multiplies the number of
services participating in a lifecycle. Foundation-tier and engine-tier code rarely has more
than one write path for a given subtype. If you encounter the pattern outside a harness app,
apply the same fix.
