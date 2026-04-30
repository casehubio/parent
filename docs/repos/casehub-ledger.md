# casehub-ledger — Platform Deep Dive

**GitHub:** [casehubio/casehub-ledger](https://github.com/casehubio/casehub-ledger)  
**Platform doc:** [PLATFORM.md](https://raw.githubusercontent.com/casehubio/casehub-parent/main/docs/PLATFORM.md)

---

## Purpose

Domain-agnostic, immutable, cryptographically tamper-evident audit ledger for any Quarkus application. Zero knowledge of business domain. Consumers extend it; it never extends them.

---

## Key Abstractions

### Core Model

| Class | Role |
|---|---|
| `LedgerEntry` | Abstract `@Entity` with `@Inheritance(JOINED)`. Core fields: `subjectId`, `sequenceNumber`, `entryType` (COMMAND/EVENT/ATTESTATION), `actorId`, `actorType` (HUMAN/AGENT/SYSTEM), `actorRole`, `occurredAt`, `traceId`, `causedByEntryId`, `digest`, `supplementJson` |
| `LedgerAttestation` | Peer verdict: SOUND / FLAGGED / ENDORSED / CHALLENGED, with `confidence` and `evidence` |
| `ActorTrustScore` | Per-actor Bayesian Beta score: `trustScore`, `globalTrustScore` (EigenTrust), `alphaValue`, `betaValue` |
| `LedgerMerkleFrontier` | Stored MMR frontier (≤log₂(N) rows per subject) |
| `ActorIdentity` | Token↔identity mapping for pseudonymisation |

### Services (CDI Beans)

| Bean | Purpose |
|---|---|
| `LedgerVerificationService` | `verify(UUID subjectId)`, `inclusionProof(UUID entryId)` |
| `LedgerMerkleTree` | Pure static RFC 9162 MMR: `leafHash()`, `append()`, `treeRoot()`, `inclusionProof()`, `verifyProof()` |
| `LedgerMerklePublisher` | Opt-in Ed25519 tlog-checkpoint publisher |
| `LedgerProvExportService` | W3C PROV-DM JSON-LD export per subject |
| `LedgerErasureService` | GDPR Art.17 token-severing erasure |
| `TrustScoreJob` | `@Scheduled` nightly trust recomputation |
| `TrustScoreRoutingPublisher` | CDI events post-compute: `TrustScoreFullPayload`, `TrustScoreDeltaPayload`, `TrustScoreComputedAt` |

### SPIs (Consumer-Implemented)

| SPI | Purpose |
|---|---|
| `LedgerEntryRepository` / `ReactiveLedgerEntryRepository` | Persistence for ledger entries |
| `ActorTrustScoreRepository` | Persistence for trust scores |
| `ActorIdentityProvider` | Tokenise / resolve / erase actor identities (GDPR) |
| `DecisionContextSanitiser` | Sanitise PII from decision context JSON before storage |
| `LedgerTraceIdProvider` | Override OTel trace ID extraction |

### Supplements (Optional Attachments)

| Supplement | Purpose |
|---|---|
| `ComplianceSupplement` | GDPR Art.22 / EU AI Act Art.12 decision fields |
| `ProvenanceSupplement` | Data lineage — source entity, workflow reference |

### Flyway Migrations

| Version | Contents |
|---|---|
| V1000 | `ledger_entry` + `ledger_attestation` tables |
| V1001 | `actor_trust_score` table |
| V1002 | Supplement tables |
| V1003 | `ledger_entry_archive` table |
| V1004 | `actor_identity` pseudonymisation table |

**Consumers** own V1004+ for their own subclass join tables.

---

## Depends On

Nothing in the casehubio ecosystem. Quarkus + Hibernate ORM only.

## Depended On By

| Repo | How |
|---|---|
| `casehub-work` | Optional `casehub-work-ledger` module — `WorkItemLedgerEntry` subclass |
| `quarkus-qhorus` | Mandatory — `AgentMessageLedgerEntry` subclass; `LedgerWriteService` |
| `casehub-engine` | Optional `casehub-ledger` module — `CaseLedgerEntry` subclass |
| `claudony` | Transitively via Qhorus and casehub-ledger |

---

## What This Repo Explicitly Does NOT Do

- Provide REST endpoints (consumers define their own)
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

Leaf hash canonical form: `subjectId|seqNum|entryType|actorId|actorRole|occurredAt` — domain subclass fields excluded so the chain stays domain-agnostic.

---

## Agent Identity Convention

Format: `{model-family}:{persona}@{major}` — e.g. `"claude:tarkus-reviewer@v1"`.  
Major version bump resets trust baseline to Beta(1,1) = 0.5 prior.  
Bump criteria: model family change, persona behaviour change, scope change. Do NOT bump for: bug fixes, tuning, CLAUDE.md changes that don't alter behaviour.

---

## Current State

- 192+ tests passing, native image validated
- All epics complete: MMR, PROV-DM, privacy/pseudonymisation, EigenTrust, trust routing signals, OTel auto-wiring
- No deployed production instances — schema migrations can be rewritten in place (no incremental migration scripts needed)
- Quarkiverse submission pending (eligibility discussion ongoing)

---

## Design Documents

- [docs/DESIGN.md](https://raw.githubusercontent.com/casehubio/casehub-ledger/main/docs/DESIGN.md) — full architecture, agent identity model, mesh topology decisions
- [docs/CAPABILITIES.md](https://raw.githubusercontent.com/casehubio/casehub-ledger/main/docs/CAPABILITIES.md) — capability applicability ratings and selection matrix
- [adr/INDEX.md](https://raw.githubusercontent.com/casehubio/casehub-ledger/main/adr/INDEX.md) — architectural decision records
