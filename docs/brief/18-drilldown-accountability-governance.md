# Drill-Down — Accountability & Governance

*Merkle chains, Bayesian trust, speech act enforcement, and watchdog
detection — the technical architecture behind structural accountability.*

---

## Architecture Overview

Accountability spans two repos that compose into a single governance
infrastructure:

- **Ledger** (12 active + 8 signing + 6 example modules) provides
  the tamper-evident audit trail and trust scoring engine. After the
  #213 framework extraction, all service logic lives in constructor-
  injected POJOs in `ledger-core`. Both Quarkus and Spring Boot are
  thin wiring layers.
- **Qhorus** (23 modules, 29 store interfaces, 30 SPI interfaces)
  provides the normative communications mesh — speech acts, commitment
  tracking, protocol enforcement, and watchdog monitoring.

The two compose structurally: every Qhorus message creates a
`LedgerEntry` via the shared `LedgerAppender` SPI. Trust scores
computed by the ledger feed into Qhorus's trust-gated routing.
Protocol violations recorded in the ledger enable compliance
reporting. This is not integration — it is one accountability
architecture expressed across two module boundaries.

---

## SPI Contracts

### Ledger SPIs (11 interfaces)

| SPI | Contract | Purpose |
|-----|----------|---------|
| `LedgerAppender` | `append(LedgerEntry)` → hash-chained commit | Single write path for all subsystems |
| `LedgerEntryRepository` | CRUD + range queries with inclusion proofs | Tenant-scoped persistence |
| `TrustScoreRepository` | Score CRUD with materialized snapshots | Low-latency trust lookups |
| `AttestationService` | `attest(entryId, verdict, confidence)` | Peer review of ledger entries |
| `TrustComputationService` | Bayesian Beta + EigenTrust recomputation | Incremental trust updates |
| `IdentityVerificationService` | DID binding, credential validation, key cache | Agent identity proofs |
| `ErasureService` | Token-to-identity severing with receipt | GDPR Art.17 compliance |
| `ContextSanitisationSPI` | Domain-specific PII removal | Pluggable privacy |
| `ComplianceSupplementProvider` | Regulatory evidence attachment | EU AI Act, SOC2, etc. |
| `SigningService` | Ed25519 checkpoint signing | HSM-backed via Cloud KMS |
| `FederationService` | Trust export/import/bootstrap | Cross-deployment trust |

### Qhorus SPIs (30 interfaces)

Key contracts in the communications mesh:

| SPI | Contract | Purpose |
|-----|----------|---------|
| `ChannelProtocol` | `evaluate(message, channelState)` → verdict | Message sequence validation |
| `WatchdogCondition` | `check(channelState)` → alert or clear | Pathology detection |
| `SummaryUpdateHook` | `onUpdate(channel, messages)` → summary | LLM-hookable summarisation |
| `ChannelGateway` | Backend-agnostic fan-out with delivery guarantee | AT_LEAST_ONCE delivery |
| `CommitmentStore` | Full lifecycle CRUD for obligations | Ground truth for promises |
| `DispatchGateStep` | `evaluate(message, context)` → pass/block | 12-step pipeline element |
| `TrustGate` | `evaluate(sender, channel)` → threshold check | Per-channel trust filtering |

### Dispatch Gate Pipeline — 12 Steps

Every message passes through this pipeline. No bypass path:

1. **Paused check** — channel suspension
2. **ACL** — sender authorisation
3. **Rate limiting** — per-sender, per-channel
4. **Capability routing** — trust-weighted role-based routing via
   eidos `AgentSelector`
5. **Trust gate** — per-channel trust threshold
6. **Type policy** — message type restrictions per channel
7. **Correlation integrity** — response must match open commitment
8. **Protocol evaluation** — `ChannelProtocol` sequence validation
9. **Enforcement gate** — advisory / blocking / quarantine decision
10. **Overwrite** — LAST_WRITE channel semantics
11. **Ledger** — Merkle hash-chained audit entry
12. **Fan-out** — backend-specific delivery

---

## Data Model

### Merkle Mountain Range (MMR)

The ledger uses a Merkle Mountain Range (RFC 9162) — an append-only
authenticated data structure. Each entry's hash chains to the
previous entry. The MMR structure enables O(log N) inclusion proofs
without storing the entire tree.

**Entry structure:**

```
LedgerEntry
├── entryId           — UUID
├── tenantId          — tenant scope
├── actorId           — who (pseudonymised for humans)
├── entryType         — discriminator (case, work, message, trust, ...)
├── payload           — domain-specific content (JSON)
├── previousHash      — chain link (SHA-256)
├── entryHash         — H(previousHash ∥ payload ∥ metadata)
├── timestamp         — wall clock
├── supplements[]     — compliance evidence attachments
└── attestations[]    — peer verdicts (SOUND/FLAGGED/ENDORSED/CHALLENGED)
```

**Checkpoint signing:**

Ed25519 signed checkpoints establish cryptographic milestones. Four
cloud KMS providers, each with a three-module structure:

| Provider | Core Module | Quarkus Module | Spring Module |
|----------|------------|----------------|---------------|
| AWS KMS | `signing-aws-core` | `signing-aws` | `signing-aws-spring` |
| GCP Cloud KMS | `signing-gcp-core` | `signing-gcp` | `signing-gcp-spring` |
| Azure Key Vault | `signing-azure-core` | `signing-azure` | `signing-azure-spring` |
| HashiCorp Vault | `signing-vault-core` | `signing-vault` | `signing-vault-spring` |

All providers implement a 403-retry protocol for token refresh.
Private keys never leave the HSM.

### Bayesian Trust Model

Trust computation uses Bayesian Beta reputation:

- **Prior:** Beta(α₀, β₀) — initialised from federation or default
- **Update:** Each attestation adds to α (positive) or β (negative)
- **Decay:** Exponential decay factor λ applied per time window —
  recent evidence weighs more
- **Asymmetric valence:** Negative decay rate < positive decay rate —
  bad performance persists longer than good performance fades

Four score types produce different trust lenses:

| Type | Scope | Use |
|------|-------|-----|
| `GLOBAL` | All interactions | Baseline reliability |
| `CAPABILITY` | Per capability domain | Domain-specific trust |
| `DIMENSION` | Named quality axis | Accuracy, timeliness, completeness |
| `QUALITY` | Per work type | Outcome quality for specific tasks |

**EigenTrust power iteration** computes transitive trust. An agent
trusted by trusted agents inherits credibility. The algorithm
iterates until convergence (configurable epsilon). Materialized
snapshots cache results for low-latency routing lookups.

### Speech Act Taxonomy — 10 Types

```
MessageType (enum)
├── QUERY      — creates obligation: recipient should respond
├── COMMAND    — creates obligation: recipient should execute
├── PROPOSE    — creates obligation: accept, counter, or decline
├── RESPONSE   — fulfils QUERY obligation
├── STATUS     — informational, no obligation
├── DECLINE    — terminates obligation
├── HANDOFF    — transfers obligation to another agent
├── DONE       — marks obligation fulfilled
├── FAILURE    — marks obligation failed
└── EVENT      — system-generated, no direct obligation
```

### Commitment Lifecycle

```
CommitmentState
├── OPEN          — obligation created (by QUERY, COMMAND, PROPOSE)
├── ACKNOWLEDGED  — recipient confirmed receipt
├── FULFILLED     — obligation satisfied (by RESPONSE, DONE)
├── FAILED        — obligation failed (by FAILURE)
├── DECLINED      — obligation rejected (by DECLINE)
├── DELEGATED     — obligation transferred (by HANDOFF)
└── EXPIRED       — deadline passed without resolution
```

Automatic deadline enforcement on EXPIRED. Delegation chains tracked
end-to-end via `delegationChain[]` on the commitment record.

---

## Runtime Behaviour

### Trust Score Recomputation

Trust recomputation is incremental — triggered on each attestation,
not batch-scheduled:

1. New attestation arrives for entry E by agent A
2. Load current Beta parameters for (subject, scoreType)
3. Apply exponential decay since last update
4. Update α or β based on verdict (SOUND/ENDORSED → α++,
   FLAGGED/CHALLENGED → β++)
5. Apply asymmetric valence weighting
6. Recompute posterior: trust = α / (α + β)
7. If transitive trust enabled: queue EigenTrust recomputation
8. Materialise snapshot for routing cache

EigenTrust recomputation runs asynchronously. Power iteration:
```
t(i) = Σⱼ c(i,j) · t(j)   (normalised)
```
where c(i,j) is the direct trust from i to j. Iteration continues
until max(|t_new - t_old|) < ε.

### Protocol Enforcement Pipeline

When a message enters a protocol-governed channel:

1. `ChannelProtocol.evaluate()` checks message against channel state
2. Verdict: PASS, VIOLATION(reason), or WARN(reason)
3. Enforcement mode determines action:
   - **Advisory:** log violation, dispatch message
   - **Blocking:** reject message, return error to sender
   - **Quarantine:** hold message, create review work item
4. If violation count > severity threshold → auto-escalate mode
   (advisory → blocking)
5. Violation recorded in ledger with protocol reference

### Watchdog Detection Loop

Watchdogs run on configurable schedules per channel:

1. `WatchdogCondition.check()` evaluates channel state
2. If alert: emit `WatchdogAlertEvent` (CDI async)
3. Alert feeds into notification pipeline
4. Alert can trigger case action:
   - Echo chamber → inject dissenting agent
   - Circular delegation → escalate to human supervisor
   - Conversation stall → inject convergence prompt
   - Barrier stuck → timeout the barrier
5. Alert resolution tracked in commitment store

### GDPR Erasure Flow

1. Erasure request received for human actor H
2. Look up pseudonymisation token T for H
3. Sever T → H mapping (the token becomes orphaned)
4. Ledger entries remain — hash chain intact, actor identity unknown
5. Generate tamper-evident erasure receipt (itself a ledger entry)
6. Run `ContextSanitisationSPI` over all entries with token T
7. Sanitised entries remain in chain — Merkle integrity preserved

The chain is never broken. Entries are not deleted. They become
permanently anonymous.

---

## Extension Points

| Extension | SPI | Pattern |
|-----------|-----|---------|
| Custom channel protocol | `ChannelProtocol` | CDI `@ApplicationScoped` |
| Custom watchdog condition | `WatchdogCondition` | CDI auto-discovery |
| Custom trust score type | Extend `TrustScoreType` enum | — |
| Custom compliance supplement | `ComplianceSupplementProvider` | CDI bean |
| Custom context sanitiser | `ContextSanitisationSPI` | Domain-specific PII rules |
| Custom attestation aggregation | `AggregationStrategy` | 3 built-in + custom |
| Custom KMS signer | `SigningService` | New cloud provider module |
| Custom channel gateway | `ChannelGateway` | Backend-specific delivery |
| Custom evidence collector | Strategy key routing | ops compliance module |
| Custom enforcement mode | `DispatchGateStep` | Pipeline extension |

---

## Module Map

### Ledger

| Module | Provides | Key Types |
|--------|----------|-----------|
| `ledger-api` | Contracts, 11 SPIs | `LedgerEntry`, `TrustScore`, `Attestation` |
| `ledger-core` | Framework-neutral services | `MerkleAppender`, `BayesianTrustEngine`, `EigenTrustComputation` |
| `ledger-runtime` | Quarkus CDI wiring | `LedgerLifecycleManager` |
| `ledger-spring` | Spring auto-config | `LedgerAutoConfiguration` |
| `ledger-persistence-jpa-common` | Shared JPA entities | 14 entity classes |
| `ledger-persistence-jpa` | Quarkus JPA | Panache repositories |
| `ledger-persistence-spring-jpa` | Spring Data JPA | Spring repositories |
| `ledger-compliance` | Compliance reporting | 6 report types, Qute templates |
| `ledger-signing-*` | 4 × 3 Cloud KMS | Ed25519 signing via HSM |

### Qhorus

| Module | Provides | Key Types |
|--------|----------|-----------|
| `qhorus-api` | Contracts, 30 SPIs | `Message`, `Commitment`, `Channel`, `WatchdogCondition` |
| `qhorus-runtime` | Message dispatch, protocol enforcement | `DispatchGatePipeline`, `CommitmentLifecycleManager` |
| `qhorus-runtime-core` | Framework-neutral logic | Protocol evaluator, watchdog engine |
| `qhorus-runtime-spring` | Spring auto-config | REST controllers, auto-configuration |
| `qhorus-compliance-report` | EU AI Act evidence | Render → sign → store pipeline |
| `qhorus-a2a-protocol` | A2A bridge | Agent cards, task messaging, SSE |
| `qhorus-a2a-outbound` | A2A outbound | Outbound agent communication |
| `qhorus-a2a-push-notification` | A2A push | Async notification delivery |
| `qhorus-graphql` | GraphQL surface | Channel, message, commitment queries |
| `qhorus-push` | Push delivery | Durable store-and-forward |

### 11 Watchdog Condition Types

| Watchdog | Detects | Response |
|----------|---------|----------|
| Barrier Stuck | Barrier channel waiting too long | Timeout the barrier |
| Approval Pending | Oversight gate past SLA | Escalate approval |
| Agent Stale | No output within expected window | Health check, replacement |
| Channel Idle | No activity on active channel | Inject prompt |
| Queue Depth | Message backlog exceeding capacity | Scale, throttle |
| Context Pressure | Memory limits approaching | Summarise, archive |
| Loop Detected | Cyclic message patterns | Break cycle, escalate |
| Obligation Fan-Out | Too many commitments created | Rate-limit, review |
| Conversation Stall | Discussion without convergence | Convergence prompt |
| Echo Chamber | Agents reinforcing without substance | Inject dissent |
| Circular Delegation | Obligations passed in circles | Escalate to human |
