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
| `api/` | `casehub-ledger-api` | Pure-Java SPIs and model types — no JPA, no Quarkus framework deps |
| `runtime/` | `casehub-ledger` | Full extension: JPA entities, services, Flyway migrations, CDI |
| `deployment/` | `casehub-ledger-deployment` | Quarkus build-time augmentation |
| `persistence-memory/` | `casehub-ledger-memory` | Zero-datasource in-memory `@Alternative @Priority(1)` implementations of all persistence SPIs — for `@QuarkusTest` isolation and ephemeral installs. Add as `compile`-scope dependency in consumer modules to activate. |

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

`LedgerEnricherPipeline` is an `@ApplicationScoped` CDI bean that owns enricher pipeline execution — shared by the JPA `@EntityListeners` path and the in-memory path. It is not an SPI (consumers do not implement it) but is the shared execution point for any consumer that adds enrichers.

See `docs/DESIGN.md` for service class structure.

### SPIs (Consumer-Implemented or Built-In Alternatives)

| SPI | Default | Built-in Alternative | Purpose |
|---|---|---|---|
| `LedgerEntryRepository` / `ReactiveLedgerEntryRepository` | — | JPA default; `InMemoryLedgerEntryRepository @Alternative @Priority(1)` in `casehub-ledger-memory` (wins over JPA by priority) | Persistence for ledger entries |
| `LedgerMerkleFrontierRepository` | — | JPA default (`JpaLedgerMerkleFrontierRepository @Alternative`) | Read/replace the per-subject Merkle MMR frontier — extracted from direct `EntityManager` injection in `LedgerVerificationService` |
| `ActorTrustScoreRepository` | — | JPA default | Persistence for trust scores |
| `ActorIdentityProvider` | — | JPA default | Tokenise / resolve / erase actor identities (GDPR) |
| `DecisionContextSanitiser` | no-op | — | Sanitise PII from decision context JSON before storage |
| `LedgerTraceIdProvider` | OTel span | — | Override OTel trace ID extraction |
| `TrustImportService` | no-op default | JPA default (seed-if-absent) | Import trust scores from external payload |
| `TrustBootstrapSource` | no-op default | — | Fetch prior trust data for first-time actors |

### Agent Identity Pipeline

Ledger consumes identity SPIs from `casehub-platform-identity` — it does not own them.

The write-time pipeline (enrichers, always active):

| Enricher | Priority | What it does |
|----------|----------|--------------|
| `ActorDIDEnricher` | 40 | Calls `ActorDIDProvider` (from `casehub-platform-identity`); populates `LedgerEntry.actorDid` |
| `ActorIdentityValidationEnricher` | 50 | Calls `DIDResolver` + `AgentCredentialValidator` (from `casehub-platform-identity`); sets `pendingIdentityStatus` |

The binding persistence observer (`ActorIdentityBindingObserver`) fires async and calls the JPA-backed
`JpaActorIdentityBindingRepository` to persist each validation outcome as an `ActorIdentityBindingEntry`
(V1008 schema). This is the ledger's own concern — platform does not touch persistence.

Enforcement: `LedgerIdentityEnforcementListener` (`@EntityListeners`) gates persist in ENFORCE mode
(`casehub.ledger.agent-identity.validation-mode=ENFORCE`). Config prefix for validation mode
stays in ledger; DID resolution and SCIM lookup config moved to `casehub.identity.*`.

See [`docs/repos/casehub-identity.md`](casehub-identity.md) for the identity module deep-dive.

### Supplements (Optional Attachments)

| Supplement | Purpose |
|---|---|
| `ComplianceSupplement` | GDPR Art.22 / EU AI Act Art.12 decision fields |
| `ProvenanceSupplement` | Data lineage — source entity, workflow reference |

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
| V1008 | `actor_did` column on `ledger_entry` + `actor_identity_binding` join table |

**Consumers** own V2000+ for their own subclass join tables.

---

## Depends On

| Repo | What |
|------|------|
| `casehub-platform-api` | `ActorType`, `ActorTypeResolver` (identity primitives) |
| `casehub-platform-identity` | `ActorDIDProvider`, `DIDResolver`, `AgentCredentialValidator` SPIs; identity model types and CDI event records |

## Depended On By

| Repo | How |
|---|---|
| `casehub-work` | Optional ledger module — extends `LedgerEntry` to record work item events |
| `casehub-qhorus` | Mandatory — extends `LedgerEntry` to record agent messages; provides ledger write integration |
| `casehub-engine` | Optional ledger module — extends `LedgerEntry` to record case events |
| `claudony` | Transitively via Qhorus and casehub-ledger |

---

## What This Repo Explicitly Does NOT Do

- Provide REST endpoints (consumers define their own)
- Provide MCP tools (consumers define their own)
- Capture domain events (consumers wire their own `@ObservesAsync` observers)
- Replay events or project CQRS views
- Know anything about WorkItems, Cases, or agent channels
- Own DID resolution or VC validation logic (those live in `casehub-platform-identity`)
- Own SCIM2 agent lookup (that is `ScimActorDIDProvider` in `casehub-platform-identity`)

---

## Consumer Pattern

Consumers:
1. Extend `LedgerEntry` as a JPA `@Entity` (`@DiscriminatorValue`)
2. Add their own Flyway migration (V2000+ range) for the subclass join table
3. Wire a CDI observer to capture domain events as ledger entries
4. Optionally attach `ComplianceSupplement` or `ProvenanceSupplement`
5. Optionally activate a `casehub-platform-identity` alternative (`KeyDIDResolver`, `WebDIDResolver`, `ScimActorDIDProvider`) for agent identity binding

See `docs/DESIGN.md` for the leaf hash scheme.

---

## Agent Identity Convention

Format: `{model-family}:{persona}@{major}` — e.g. `"claude:tarkus-reviewer@v1"`.  
Major version bump resets trust baseline to Beta(1,1) = 0.5 prior.  
Bump criteria: model family change, persona behaviour change, scope change. Do NOT bump for: bug fixes, tuning, CLAUDE.md changes that don't alter behaviour.

---

## Current State

- 523 tests passing, native image validated
- Reactive/blocking service parity enforced at build time via `BlockingReactiveParityTest` (ArchUnit 1.4.1) — auto-discovers all `Reactive*Service` classes and asserts bidirectional method parity and `Uni<T>` returns
- All epics complete: MMR, PROV-DM, privacy/pseudonymisation, EigenTrust, trust routing signals, OTel auto-wiring, agent DID/VC binding
- Identity infrastructure (SPIs, resolvers, SCIM provider) extracted to `casehub-platform-identity` — ledger retains enrichers, binding persistence, and enforcement
- No deployed production instances — schema migrations can be rewritten in place (no incremental migration scripts needed)
- Quarkiverse submission pending (eligibility discussion ongoing)

---

## Design Documents

- [docs/DESIGN.md](https://raw.githubusercontent.com/casehubio/casehub-ledger/main/docs/DESIGN.md) — full architecture, agent identity model, mesh topology decisions
- [docs/CAPABILITIES.md](https://raw.githubusercontent.com/casehubio/casehub-ledger/main/docs/CAPABILITIES.md) — capability applicability ratings and selection matrix
- [adr/INDEX.md](https://raw.githubusercontent.com/casehubio/casehub-ledger/main/adr/INDEX.md) — architectural decision records
