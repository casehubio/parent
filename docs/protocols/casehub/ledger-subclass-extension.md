---
id: PP-20260513-ledger-subclass
title: "Ledger subclass extension rules — JOINED inheritance, consumer-owned migrations, domain-agnostic leaf hash"
type: rule
scope: platform
applies_to: "Any casehubio repo adding a new JPA subclass of LedgerEntry"
severity: required
refs:
  - docs/protocols/casehub/flyway-version-range-allocation.md
  - docs/protocols/casehub/ledger-spi-propagation.md
violation_hint: "Wrong inheritance strategy, version conflict, or domain-specific data in leaf hash breaks multi-tenant query and auditability guarantees"
created: 2026-05-13
---

# Protocol: Ledger Subclass Extension Rules

**Applies to:** Any casehubio repo adding a JPA subclass of `LedgerEntry` in `casehub-ledger`  
**Severity:** Required — violations break multi-tenant query, audit trail integrity, or Flyway startup

---

## Inheritance Strategy: JOINED

**Use `InheritanceType.JOINED`.** Never `SINGLE_TABLE` or `TABLE_PER_CLASS`.

- `SINGLE_TABLE` — all columns in one table, nullable by subtype. Breaks `NOT NULL` constraints and pollutes the base table with domain-specific columns.
- `TABLE_PER_CLASS` — no shared base table. Breaks cross-type queries (`SELECT * FROM ledger_entry ORDER BY occurred_at`) and disables the leaf hash integrity check.
- `JOINED` — base table holds shared fields; each subtype has its own join table with its own columns. Cross-type queries work against the base table; subtype-specific queries join as needed.

```java
@Entity
@Inheritance(strategy = InheritanceType.JOINED)
@Table(name = "ledger_entry")
public class LedgerEntry { ... }

@Entity
@Table(name = "work_item_ledger_entry")
public class WorkItemLedgerEntry extends LedgerEntry { ... }
```

---

## Flyway Version Numbering: V1004+

`casehub-ledger` owns the Flyway version range V1000–V1003 for its own base schema. **Consumer repos that add ledger subclass join tables must use V1004 or higher**, using their own allocated range from the flyway-version-range-allocation protocol.

```
casehub-ledger base schema:    V1000–V1003
casehub-work subclass joins:   V4000+ (within casehub-work's allocated block)
casehub-qhorus subclass joins: V3000+ (within casehub-qhorus's allocated block)
```

Each consumer owns its own join table migration — it must not be in casehub-ledger.

---

## Domain-Agnostic Leaf Hash

Every `LedgerEntry` subclass participates in the Merkle Mountain Range (MMR) append-only audit chain via a leaf hash. **The leaf hash must not encode domain-specific data.**

The leaf hash is computed from the base `LedgerEntry` fields only:
- `id`, `subjectId`, `actorId`, `occurredAt`, `eventType`, `sequenceNumber`

It must NOT include fields from the subclass join table (e.g. `workItemId`, `channelId`, `policyId`). Subclass-specific fields would make the hash meaningless across different subtype contexts and break cross-repo audit verification.

---

## Consumer-Owned Migration Pattern

The subclass join table belongs to the consumer repo, not to `casehub-ledger`:

```
casehub-ledger/
└── src/main/resources/db/migration/
    ├── V1000__ledger_base.sql        ← base table only
    └── V1001__ledger_sequence.sql    ← base schema extensions

casehub-work/
└── src/main/resources/db/migration/
    └── V4001__work_item_ledger_entry.sql   ← join table
```

The join table migration depends on the base table existing. If `casehub-ledger` is used without `casehub-work`, no join table is created — correct.

---

## Checklist When Adding a New Ledger Subclass

- [ ] Inheritance strategy is `JOINED` — not `SINGLE_TABLE` or `TABLE_PER_CLASS`
- [ ] Join table migration is in the consumer repo, not `casehub-ledger`
- [ ] Migration version is ≥ V1004 and within the consumer repo's allocated range
- [ ] Leaf hash computation excludes subclass-specific columns
- [ ] New SPI method added to `LedgerEntryRepository`? → follow `ledger-spi-propagation.md` checklist
- [ ] `LedgerEntryType` enum updated if a new entry type was introduced
