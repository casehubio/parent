# Privacy (GDPR)

> **Scope:** Art.17 erasure, Art.22 decision records, PII sanitisation
> **Audience:** All (critical for regulated-domain app builders)
> **Key repos:** casehub-ledger
> **Protocols:** None specific

## Overview

All GDPR concerns are centralised in `casehub-ledger`:

- **Art.17 erasure** — `LedgerErasureService` + `ActorIdentityProvider` SPI
- **Art.22 decision records** — `ComplianceSupplement`
- **PII sanitisation** — `DecisionContextSanitiser` SPI

This centralisation ensures consistent GDPR compliance across all harnesses without duplicating erasure logic.

## Art.17 Erasure (Right to be Forgotten)

`LedgerErasureService` in `casehub-ledger` provides GDPR Art.17 erasure with audit trail.

**API:**
- `eraseActor(actorId, reason)` — erase all ledger entries for an actor
- `eraseEntity(entityId, tenancyId)` — erase all entries for a business entity (e.g. case, WorkItem)
- `eraseEntityAcrossTenants(entityId, Set<String> tenantIds)` — cross-tenant entity wipe

**Erasure reasons** (`ErasureReason` enum):
- `GDPR_ART_17_REQUEST` — data subject exercised right to be forgotten
- `RETENTION_EXPIRED` — retention period elapsed
- `ACCOUNT_DELETION` — user account deleted

**Erasure receipt ledger entry** (opt-in):

Activate with:
```properties
casehub.ledger.erasure-receipt.enabled=true
quarkus.arc.selected-alternatives=io.casehub.ledger.jpa.JpaErasureReceiptRepository
```

When enabled, every erasure operation creates an `ErasureReceiptLedgerEntry` — a tamper-evident record of the erasure itself.

`ErasureResult` carries `Optional<UUID> receiptEntryId` for GDPR Art.5(2) audit (accountability principle — prove that erasure occurred).

**Cross-tenant erasure:**

`eraseEntityAcrossTenants(entityId, Set<String> tenantIds)` requires:
- `CurrentPrincipal.isCrossTenantAdmin()` — only cross-tenant admins may erase across tenants
- `CROSS_TENANT_ERASE` `MemoryCapability` — adapter declares support
- `MemoryPermissions.assertCrossTenantAdmin(principal)` — 1-arg assertion (no async bypass)

**Implementation notes:**
- `NoOpCaseMemoryStore` returns 0 and does not declare `CROSS_TENANT_ERASE`
- JDBC adapters (JPA, SQLite) use single optimized `DELETE IN` query (SQLite chunked at 500 for `SQLITE_LIMIT_VARIABLE_NUMBER`)
- REST adapters (Mem0, Graphiti) use sequential loop — idempotent/retry-safe

**Async-aware permission checks:**

`MemoryPermissions.assertTenant(tenancyId, principal, requestContextActive)` — 3-arg async-aware form.

Skip principal check when CDI request scope inactive (background jobs, scheduled tasks).

## Art.22 Decision Records (Automated Decision-Making)

`ComplianceSupplement` in `casehub-ledger` attaches decision rationale to ledger entries.

GDPR Art.22 requires meaningful information about the logic involved in automated decision-making. The compliance supplement captures:
- **Decision context** — what inputs influenced the decision
- **Decision rationale** — why this outcome was chosen
- **Human review flag** — whether a human reviewed the decision

**Use case:** An agent recommends rejecting a loan application. The ledger entry carries:
- The agent's attestation (trust score, DID)
- The decision context (income, credit score, debt ratio)
- The rationale ("debt-to-income ratio exceeds 43% threshold")
- Human review status

## PII Sanitisation

`DecisionContextSanitiser` SPI in `casehub-ledger` sanitises decision context before it's written to the compliance supplement.

**Purpose:** Remove or redact PII from decision rationale while preserving auditability.

**Example:** Sanitise a free-text rationale like "John Smith's credit score is 580" → "Applicant's credit score is 580".

**Implementation:**
- `NoOpDecisionContextSanitiser @DefaultBean` — no sanitisation
- Application repos provide domain-specific sanitisers (e.g. regex-based name removal, entity masking)

## Memory SPI and Erasure

`CaseMemoryStore` SPI (migrated to `casehub-neocortex-memory-api`) provides entity-scoped erasure:

- `eraseById(memoryId, entityId, tenantId)` — erase a single memory; entity mismatch is a silent no-op
- `eraseEntity(entityId, tenantId)` — erase all memories for an entity; returns `int` count for GDPR Art.5(2) audit
- `eraseEntityAcrossTenants(entityId, Set<String> tenantIds)` — cross-tenant entity wipe

**Permission-aware:** All erase methods check `CurrentPrincipal.tenancyId()` unless `requestContextActive=false` (async jobs).

**Backends:**
- `NoOpCaseMemoryStore @DefaultBean` — no-op, returns 0
- `InMemoryCaseMemoryStore @Alternative @Priority(1)` — volatile `ConcurrentHashMap`
- `JpaCaseMemoryStore @ApplicationScoped` — PostgreSQL + Flyway + FTS
- `SqliteCaseMemoryStore @Alternative @Priority(1)` — SQLite + HikariCP WAL + FTS5
- `Mem0CaseMemoryStore @Alternative @Priority(1)` — Mem0 REST adapter
- `GraphitiCaseMemoryStore @Alternative @Priority(2)` — Graphiti REST `GraphCaseMemoryStore`

All backends implement entity-scoped erasure with the same permission semantics.

## Ledger Entry Enrichment

`LedgerEnricherPipeline` runs CDI-discovered `LedgerEntryEnricher` implementations at persist time.

Enrichers can attach metadata for GDPR compliance:
- Data processing purpose (Art.13)
- Legal basis (Art.6)
- Retention period (Art.13)
- Processor identity (Art.28)

Enrichers run synchronously in the same transaction as the ledger write.

## W3C PROV-DM Export

`LedgerProvExportService` exports tamper-evident audit trails as W3C PROV-DM graphs.

**GDPR use case:** Provide data subjects with a machine-readable export of all processing activities involving their data (Art.15 — right of access).

PROV-DM is a W3C standard for provenance interchange. The export enables external compliance tools to ingest CaseHub audit trails without understanding the ledger schema.
