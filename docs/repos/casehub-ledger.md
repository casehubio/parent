# casehub-ledger — Platform Deep Dive

**GitHub:** [casehubio/casehub-ledger](https://github.com/casehubio/casehub-ledger)  
**Platform doc:** [PLATFORM.md](https://raw.githubusercontent.com/casehubio/parent/main/docs/PLATFORM.md)

---

## Purpose

Domain-agnostic, immutable, cryptographically tamper-evident audit ledger for any Quarkus application. Zero knowledge of business domain. Consumers extend it; it never extends them.

---

## Modules

| Module | Artifact ID | Purpose |
|--------|-------------|---------|
| `api/` | `casehub-ledger-api` | Pure-Java SPIs and model types — no JPA, no Quarkus framework deps. Two-tier `LedgerEntry` model (ledger#168): `@MappedSuperclass` base in `api/`, `JpaLedgerEntry` entity in `runtime/`. `LedgerAppender` SPI for domain-agnostic ledger writes with `AuditRecord` value type (ledger#168). |
| `runtime/` | `casehub-ledger` | Full extension: JPA entities, services, Flyway migrations, CDI |
| `deployment/` | `casehub-ledger-deployment` | Quarkus build-time augmentation |
| `persistence-memory/` | `casehub-ledger-memory` | Zero-datasource in-memory `@Alternative @Priority(1)` implementations of all persistence SPIs — for `@QuarkusTest` isolation and ephemeral installs. Add as `compile`-scope dependency in consumer modules to activate. |
| `rest/` | `casehub-ledger-rest` | JAX-RS REST API for ledger queries and admin operations — opt-in via explicit dependency (ledger#162). Provides `GET /ledger/entries`, `GET /ledger/entries/{id}`, `POST /ledger/entries/search` with pagination, filtering, and type discrimination. Exception mappers for ledger-specific errors. |
| `testing/` | `casehub-ledger-testing` | NoOp SPI implementations for test isolation — `NoOpLedgerAppender`, `NoOpActorIdentityProvider`, `NoOpTrustScoreSource`, etc. (ledger#173). |
| `consumer-compat-test/` | `casehub-ledger-consumer-compat-test` | Boot guard for CDI graph integrity. Standalone POM (not a child of ledger parent). Single `@QuarkusTest` with empty body — if CDI boots with no persistence infrastructure and no `quarkus.arc.exclude-types`, every injection point is satisfied by `@DefaultBean` no-ops. A failing build here means a new bean introduced an unsatisfied injection point that would break consumers. `maven.deploy.skip=true`. |
| `signing/` | `casehub-ledger-signing` | Reactor POM for cloud-managed Ed25519 signing adapters. Each provider has a pure Java module (framework-free) and a Quarkus CDI adapter module. See [Cloud KMS Signers](#cloud-kms-signers) below. |

---

## Key Abstractions

### Core Model

| Concept | Role |
|---|---|
| `LedgerEntry` | Abstract base entity for all tamper-evident audit records |
| `LedgerAttestation` | Peer verdict record (SOUND / FLAGGED / ENDORSED / CHALLENGED) with confidence and evidence |
| `ActorTrustScore` | Per-actor trust score keyed by actor, capability, and dimension; supports Bayesian and continuous score types |
| `LedgerMerkleFrontier` | Stored MMR frontier enabling incremental Merkle tree operations per subject |
| `ActorIdentity` | Token-to-identity mapping for pseudonymisation |

See `docs/DESIGN.md` for field model and entry type vocabulary.

### Services

The ledger provides services for: cryptographic verification and inclusion proofs, Merkle tree operations (RFC 9162 MMR), optional Ed25519 tlog-checkpoint publishing, W3C PROV-DM lineage export, GDPR Art.17 token-severing erasure, nightly trust score recomputation with CDI routing events, trust score read-model export, and trust bootstrapping for new actors.

**Incremental trust recomputation (ledger#115):** When `casehub.ledger.trust-score.incremental.enabled=true` (default false), `saveAttestation()` fires `AttestationRecordedEvent` → `IncrementalTrustUpdateObserver` (AFTER_SUCCESS + REQUIRES_NEW) → `PerActorTrustComputer` recomputes the affected actor's scores immediately using the same Bayesian Beta algorithm as the batch job. Fires `TrustScoreActorUpdatedEvent` on completion. The nightly `TrustScoreJob` remains as a consistency backstop.

**`TrustGateService` API (ledger#118):** now injects `TrustScoreSource` (not `ActorTrustScoreRepository`); returns `OptionalDouble` (was `Optional<Double>`); `findScore()` removed; `dimensionScores()` renamed to `allDimensionScores()`. `TrustGateService.allCapabilityScores(String actorId): Map<String, Double>` — returns all CAPABILITY-scoped trust scores as a capability-tag → score map (ledger#56 for actor state view).

**Trust score architecture (ledger#118):** On-read computation via `TrustScoreSource` SPI — three implementations:
- `MaterializedTrustScoreSource` (`@DefaultBean`) — reads pre-computed scores from `ActorTrustScoreRepository` (original path). Overrides batch methods (`scoresFor`, `decisionCountsFor`) with single `WHERE actorId IN (...)` queries.
- `CachedTrustScoreSource` — wraps `MaterializedTrustScoreSource` with in-memory TTL cache; replaces the engine-side `TrustScoreCache` (engine migration tracked in ledger#123)
- `ComputedTrustScoreSource` — computes on demand via `TrustScoreCalculator` (pure computation extracted from `PerActorTrustComputer`)

**Batch capability scoring API:** `TrustScoreSource` defines two batch default methods — `scoresFor(List<String> candidateIds, String capabilityTag) → Map<String, OptionalDouble>` and `decisionCountsFor(…) → Map<String, Integer>`. Defaults loop per-actor; `MaterializedTrustScoreSource` overrides with single `IN (…)` queries. Every candidate appears in the result map; `OptionalDouble.empty()` means the actor is in the BOOTSTRAP phase.

**Trust-score materialization config gate:** `casehub.ledger.trust-score.materialization.enabled` (default `true`). When `false`, `TrustScoreJob` and `IncrementalTrustUpdateObserver` skip computation and persistence — `ComputedTrustScoreSource` still works for on-read computation.

**Content-aware Merkle leaf hash:** `LedgerMerkleTree.leafHash()` computes `SHA-256(0x00 | entry.canonicalBytes())`. `canonicalBytes()` includes all core fields (subjectId, sequenceNumber, entryType, actorId, actorRole, occurredAt, tenancyId, actorType, causedByEntryId) plus `metadata`, `supplementJson`, and `domainContentBytes()`. Subclasses with persistent join-table fields MUST override `domainContentBytes()` — build-time enforcement via `LedgerProcessor` produces a deployment error if they do not.

**`@CrossTenant` qualifier** (`io.casehub.ledger.runtime.qualifier`): CDI qualifier disambiguating `CrossTenantLedgerEntryRepository` / `CrossTenantReactiveLedgerEntryRepository` from their tenant-scoped counterparts. Unqualified injection fails at startup. Not applied to inherently cross-tenant repos (`ActorTrustScoreRepository`, `KeyRotationRepository`, `ActorIdentityBindingRepository`). Build-time enforcement: `LedgerProcessor` rejects `@RequestScoped` beans injecting `@CrossTenant`. TenancyId propagates through the CDI event chain via `LedgerEntry.tenancyId`, set at persist time by the repository.

`LedgerEnricherPipeline` is an `@ApplicationScoped` CDI bean that owns enricher pipeline execution — shared by the JPA `@EntityListeners` path and the in-memory path. It is not an SPI (consumers do not implement it) but is the shared execution point for any consumer that adds enrichers.

`ReactiveAgentIdentityVerificationService` is a `@DefaultBean @Unremovable` Mutiny bridge wrapping `AgentIdentityVerificationService` on the blocking worker pool. Always active regardless of `reactive.enabled`.

**`ErasureReceiptLedgerEntry` (V1010, ledger PR #152):** GDPR Art.17 tamper-evident erasure receipt. Opt-in via `casehub.ledger.erasure-receipt.enabled=true` (default false). `subjectId=nameUUIDFromBytes(erasedActorId)`. `ErasureReason` enum: `GDPR_ART_17_REQUEST | RETENTION_EXPIRED | ACCOUNT_DELETION`. `ErasureResult` now carries `Optional<UUID> receiptEntryId`. Activate `JpaErasureReceiptRepository @Alternative` via `quarkus.arc.selected-alternatives`. Consumer migration tracked in casehub-devtown#82.

**`LedgerSequenceAllocator` dialect detection:** now queries `INFORMATION_SCHEMA.SETTINGS` to detect `H2 MODE=PostgreSQL` (previously used `getMetaData().getURL()` which Agroal strips). Plain H2 (no `MODE=PostgreSQL`) gets the SQL-standard `MERGE` path; PostgreSQL and `H2+MODE=PostgreSQL` get `ON CONFLICT DO NOTHING`. Fixes `casehub-engine-ledger` and any downstream module using plain H2 tests.

**`LedgerPrivacyProducer`:** now injects `Instance<EntityManager>` instead of `EntityManager` directly — datasource-free deployments (casehub-drafthouse, casehub-qhorus without ledger JPA) no longer fail CDI augmentation on `ActorIdentityProvider`.

See `docs/DESIGN.md` for service class structure.

### SPIs (Consumer-Implemented or Built-In Alternatives)

| SPI | Default | Built-in Alternative | Purpose |
|---|---|---|---|
| `LedgerEntryRepository` / `ReactiveLedgerEntryRepository` | — | JPA default; `InMemoryLedgerEntryRepository @Alternative @Priority(1)` in `casehub-ledger-memory` (wins over JPA by priority) | Persistence for ledger entries |
| `LedgerMerkleFrontierRepository` | — | JPA default (`JpaLedgerMerkleFrontierRepository @Alternative`) | Read/replace the per-subject Merkle MMR frontier — extracted from direct `EntityManager` injection in `LedgerVerificationService` |
| `ActorTrustScoreRepository` | — | JPA default | Persistence for trust scores |
| `TrustScoreSource` | `MaterializedTrustScoreSource` | `CachedTrustScoreSource`, `ComputedTrustScoreSource` | On-read trust score retrieval; injected into `TrustGateService` (ledger#118) |
| `ActorIdentityProvider` | — | JPA default | Tokenise / resolve / erase actor identities (GDPR) |
| `ErasureReceiptRepository` | — | JPA default (`JpaErasureReceiptRepository @Alternative`); `NoOpErasureReceiptRepository` | Query erasure receipt entries by actor/tenant; `countByTenant(tenancyId)` for compliance metrics |
| `DecisionContextSanitiser` | no-op | — | Sanitise PII from decision context JSON before storage |
| `LedgerTraceIdProvider` | OTel span | — | Override OTel trace ID extraction |
| `TrustImportService` | no-op default | JPA default (seed-if-absent) | Import trust scores from external payload |
| `TrustBootstrapSource` | no-op default | — | Fetch prior trust data for first-time actors |
| `ActorDIDProvider` | — | `ScimActorDIDProvider @Alternative @Priority(1)` (explicit activation via `quarkus.arc.selected-alternatives`) | Resolves actorId → DID via SCIM2 Agent endpoint; TTL cache; config prefix `casehub.ledger.agent-identity.scim.*` |

### Supplements (Optional Attachments)

| Supplement | Purpose |
|---|---|
| `ComplianceSupplement` | GDPR Art.22 / EU AI Act Art.12 decision fields |
| `ProvenanceSupplement` | Data lineage — source entity, workflow reference |

### Metadata Field

`LedgerEntry.metadata` — consumer-provided freeform JSON context (`TEXT` column). Included in `canonicalBytes()` for tamper evidence. Must be valid JSON, must NOT contain PII. Propagated through the write path via `AuditRecord.withMetadata(String)` and `OutcomeRecord.withMetadata(String)`. Config: `casehub.ledger.metadata.max-size` (default 65536).

### @NamedQuery Migration

All JPQL queries migrated from inline strings to `@NamedQuery` annotations on `JpaLedgerEntry`. 11 named queries: `LedgerEntry.listAll`, `findAllEvents`, `findEventsByActorId`, `findByTimeRange`, `findByIdAndTenancyId`, `findSequenceStats`, `findBySubjectId`, `findBySubjectIdAndTimeRange`, `findLatestBySubjectId`, `findByActorIdAndTimeRange`, `findByActorRoleAndTimeRange`, `findCausedBy`.

### Flyway Migrations

Path: `classpath:db/ledger/migration` (moved from `classpath:db/migration` in ledger#95).
Consumers must add this path to their `quarkus.flyway.locations` config.

| Version | Contents |
|---|---|
| V1000 | `ledger_entry` + `ledger_attestation` tables |
| V1001 | `actor_trust_score` table |
| V1002 | Supplement tables |
| V1003 | `ledger_entry_archive` table |
| V1004 | `actor_identity` pseudonymisation table |
| V1005 | `agent_signature` + `agent_public_key` columns on `ledger_entry` |
| V1006 | `agent_key_ref` column on `ledger_entry` |
| V1007 | `key_rotation_entry` subclass table |
| V1009 | `plain_ledger_entry` — `PlainLedgerEntry` for domain-agnostic event writes (`OutcomeRecorder`) |
| V1010 | `erasure_receipt_entry` — `ErasureReceiptLedgerEntry` (opt-in via `casehub.ledger.erasure-receipt.enabled=true`) |

**Consumers** own V1011+ for their own subclass join tables (V1004–V1007, V1009–V1010 are ledger base).

---

## Depends On

Nothing in the casehubio ecosystem. Quarkus + Hibernate ORM only.

## Depended On By

| Repo | How |
|---|---|
| `casehub-work` | Optional ledger module — extends `LedgerEntry` to record work item events |
| `casehub-qhorus` | Mandatory — extends `LedgerEntry` to record agent messages; provides ledger write integration |
| `casehub-engine` | Optional ledger module — extends `LedgerEntry` to record case events |
| `claudony` | Transitively via Qhorus and casehub-ledger |

---

## What This Repo Explicitly Does NOT Do

- Provide REST endpoints by default — `ledger-rest` is opt-in via explicit dependency (consumers may still define their own)
- Provide MCP tools (consumers define their own)
- Capture domain events (consumers wire their own `@ObservesAsync` observers)
- Replay events or project CQRS views
- Know anything about WorkItems, Cases, or agent channels

---

## Consumer Pattern

Consumers:
1. Extend `LedgerEntry` as a JPA `@Entity` (`@DiscriminatorValue`)
2. Add their own Flyway migration (V1004+ range) for the subclass join table
3. Wire a CDI observer to capture domain events as ledger entries
4. Optionally attach `ComplianceSupplement` or `ProvenanceSupplement`

See `docs/DESIGN.md` for the leaf hash scheme.

---

## Agent Identity Convention

Format: `{model-family}:{persona}@{major}` — e.g. `"claude:tarkus-reviewer@v1"`.  
Major version bump resets trust baseline to Beta(1,1) = 0.5 prior.  
Bump criteria: model family change, persona behaviour change, scope change. Do NOT bump for: bug fixes, tuning, CLAUDE.md changes that don't alter behaviour.

### Key Events and Services

**`AgentKeyRotatedEvent`** — CDI event fired by `KeyRotationService` and `ReactiveKeyRotationService` after a rotation is persisted. Observers: `ActorIdentityValidationEnricher` and `ScimActorDIDProvider` each evict their per-actorId cache on receipt.

**`ScimActorDIDProvider`** — `@Alternative` enterprise resolver. Maps actorId → DID via a SCIM2 Agent endpoint with a configurable TTL cache. Activated via `quarkus.arc.selected-alternatives`. See `docs/integration/scim2-agent-identity.md` for integration guide.

### Cloud KMS Signers

Cloud-managed Ed25519 signing lives in the `signing/` reactor. Each provider has a **pure Java module** (no framework deps — usable from `main()`) and a **Quarkus CDI adapter** module. The Vault module defines the `VaultTokenSource` SPI; cloud KMS modules use their own provider-native credential mechanisms.

| Pure Java Module | Quarkus Adapter | Cloud Provider | Key Classes |
|------------------|-----------------|----------------|-------------|
| `signing/vault-transit` | `signing/vault-transit-quarkus` | HashiCorp Vault Transit | `VaultTransitSigningClient`, `VaultTokenSource` SPI, `AppRoleVaultTokenSource`, `JwtVaultTokenSource`, `StaticVaultTokenSource`, `LoginBasedVaultTokenSource` |
| `signing/aws-kms` | `signing/aws-kms-quarkus` | AWS KMS | `AwsKmsSigningClient`, `AwsKmsContext`, `AwsKmsSigningConfig` |
| `signing/gcp-kms` | `signing/gcp-kms-quarkus` | GCP Cloud KMS | `GcpKmsSigningClient`, `GcpKmsClientWrapper`, `GcpKmsContext` |
| `signing/azure-keyvault` | `signing/azure-keyvault-quarkus` | Azure Key Vault | `AzureKeyVaultSigningClient`, `AzureKeyVaultClientWrapper`, `EcSignatureConverter` |

**`VaultTokenSource` SPI** (`io.casehub.ledger.signing.vault`): `token()` and `invalidate()`. Three implementations extend `LoginBasedVaultTokenSource` (abstract — lazy login with lease-aware TTL, 30s buffer before expiry): `AppRoleVaultTokenSource`, `JwtVaultTokenSource` (consolidates Kubernetes auth — accepts any JWT source including OIDC, federated identity), `StaticVaultTokenSource` (constant token, no-op invalidate).

**403-retry:** `VaultTransitAgentSigner` (Quarkus adapter) catches `VaultAuthenticationException` on both `fetchPublicKey()` and `sign()`, calls `tokenSource.invalidate()`, obtains a fresh token, and retries once. `VaultTransitSigningClient` throws `VaultAuthenticationException` on HTTP 403.

---

## Configuration

### Agent Identity / SCIM

Config prefix: `casehub.ledger.agent-identity.scim.*`

| Key | Purpose |
|-----|---------|
| `endpoint` | SCIM2 Agent endpoint URL |
| `auth-token` | Bearer token for the SCIM2 endpoint |
| `timeout-ms` | HTTP request timeout |
| `cache-ttl-minutes` | TTL for the per-actorId DID cache |
| `require-https` | Reject non-HTTPS endpoint URLs |

---

## Current State

- All modules on main: api, runtime, deployment, persistence-memory, rest, testing, consumer-compat-test, signing (8 sub-modules)
- 962 tests passing, native image validated
- Reactive/blocking service parity enforced at build time via `BlockingReactiveParityTest` (ArchUnit 1.4.1) — auto-discovers all `Reactive*Service` classes and asserts bidirectional method parity and `Uni<T>` returns
- All epics complete: MMR, PROV-DM, privacy/pseudonymisation, EigenTrust, trust routing signals, OTel auto-wiring
- No deployed production instances — schema migrations can be rewritten in place (no incremental migration scripts needed)
- Quarkiverse submission pending (eligibility discussion ongoing)

---

## Design Documents

- [docs/DESIGN.md](https://raw.githubusercontent.com/casehubio/casehub-ledger/main/docs/DESIGN.md) — full architecture, agent identity model, mesh topology decisions
- [docs/CAPABILITIES.md](https://raw.githubusercontent.com/casehubio/casehub-ledger/main/docs/CAPABILITIES.md) — capability applicability ratings and selection matrix
- [adr/INDEX.md](https://raw.githubusercontent.com/casehubio/casehub-ledger/main/adr/INDEX.md) — architectural decision records
