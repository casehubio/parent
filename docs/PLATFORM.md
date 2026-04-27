# Casehubio Platform Architecture

> **Purpose:** Before implementing *anything* in any casehubio repo, run the Platform Coherence Check below.
> Every implementation decision is a platform decision. A feature that seems local may duplicate something elsewhere,
> belong in a different repo, or open an opportunity to consolidate an existing abstraction.
>
> **Per-repo deep dives:** [docs/repos/](https://github.com/casehubio/casehub-parent/tree/main/docs/repos/)

---

## Platform Coherence Protocol

Run this before implementing any feature, API, abstraction, SPI, or data model change in any casehubio repo. This is not a bureaucratic gate — it is the practice that keeps the platform orthogonal, intuitive, and free of duplication.

### Step 1 — Does this already exist?

Check the Capability Ownership table below. Then check the per-repo deep-dive for the repos most likely to already have it.

Ask: *Is there a class, SPI, CDI event, or service in another repo that does this, or 90% of this?*

If yes → use the existing abstraction. If the existing one doesn't quite fit, extend it (in the right repo) rather than creating a parallel one here.

### Step 2 — Is this the right repo?

Check the Boundary Rules below. Then ask:

- Which tier does this belong to? (Foundation / Orchestration / Integration)
- Is this domain-agnostic infrastructure (→ foundation), process coordination logic (→ casehub-engine), or integration/deployment-specific (→ claudony)?
- Will this be useful to consumers other than just the current one? If yes, it belongs lower in the stack.
- Does this depend on anything that the target repo is not supposed to depend on?

If the right repo is a different one → stop. Implement it there, then consume it from here.

### Step 3 — Does this create a consolidation opportunity?

Ask: *Is there something in another repo that does a similar thing awkwardly, that this new abstraction would make redundant or easier?*

If yes → propose refactoring the other repo to use the new abstraction, even if it's more work. Parallel implementations rot; consolidated abstractions improve everything downstream.

Known consolidation candidates (as of 2026-04-27):
- `quarkus-work-notifications` Slack/Teams channels → should delegate to `casehub-connectors`
- `callerRef` format (`case:{id}/pi:{id}`) defined in casehub-engine but used opaquely by quarkus-work → consider a shared constant or typed value in `quarkus-work-api`

### Step 4 — Is this consistent with the platform pattern?

Check how the same concern is handled in the two or three most similar places in the platform. Then implement it the same way. Specifically:

- SPIs: follow the SPI placement rule (operational SPIs in `api/spi/`; persistence SPIs in model modules)
- Ledger subclasses: JOINED inheritance, consumer-owned V1004+ migration, domain-agnostic leaf hash
- CDI events: async (`@ObservesAsync`) for ledger capture; sync for routing decisions
- Named datasources: Qhorus always on `qhorus`, domain tables never mixed in
- Flyway numbering: V1000–V1003 = ledger; V1–V999 = domain; V1004+ = ledger subclass joins
- Module structure: pure-Java SPI modules have no Quarkus deps; core library modules have no JPA; full extensions have both
- No-op defaults: every SPI gets a default no-op implementation in the owning repo

### Step 5 — Does this need a platform-level doc update?

If the capability ownership table, boundary rules, or deep-dive docs need updating after this implementation, update `casehub-parent/docs/PLATFORM.md` and/or the relevant `docs/repos/*.md` file.

---

## What We're Building

A production-grade, compliance-first infrastructure stack for multi-agent AI systems on Quarkus. Targeted at regulated deployments (EU AI Act Art.12, GDPR Art.17/22). All libraries are designed for Quarkiverse submission.

Three tiers, always kept separate:
- **Foundation** — audit ledger, human task primitives, agent communication mesh. Independently embeddable in any Quarkus app.
- **Orchestration** — `casehub-engine` coordinates agents via hybrid choreography+blackboard. Depends on foundation only.
- **Integration** — `claudony` wires everything together and surfaces it in a browser dashboard. Depends on orchestration.

---

## Repository Map

| Repo | GitHub | One-liner | Tier |
|------|--------|-----------|------|
| `casehub-parent` | [casehubio/casehub-parent](https://github.com/casehubio/casehub-parent) | BOM, CI dashboards, full-stack build tooling | — |
| `quarkus-ledger` | [casehubio/quarkus-ledger](https://github.com/casehubio/quarkus-ledger) | Immutable tamper-evident audit ledger + trust scoring | Foundation |
| `quarkus-work` | [casehubio/quarkus-work](https://github.com/casehubio/quarkus-work) | Human task lifecycle (WorkItem inbox, SLA, delegation, routing) | Foundation |
| `quarkus-qhorus` | [casehubio/quarkus-qhorus](https://github.com/casehubio/quarkus-qhorus) | Peer-to-peer agent communication mesh | Foundation |
| `casehub-connectors` | [casehubio/casehub-connectors](https://github.com/casehubio/casehub-connectors) | Outbound message connectors (Slack, Teams, SMS, email) | Foundation |
| `casehub-engine` | [casehubio/engine](https://github.com/casehubio/engine) | Hybrid choreography+blackboard orchestration engine | Orchestration |
| `claudony` | [casehubio/claudony](https://github.com/casehubio/claudony) | Remote Claude CLI sessions + unified ecosystem dashboard | Integration |
| `casehub` | [casehubio/casehub](https://github.com/casehubio/casehub) | **Retiring** — original POC; no new features | — |

---

## Build / Dependency Order

```
casehub-parent              (BOM — publish first; all others import it)
  quarkus-ledger            (no casehubio deps)
  casehub-connectors        (no casehubio deps)
  quarkus-work              (core: zero casehubio deps; ledger module: depends on quarkus-ledger)
  quarkus-qhorus            (depends on quarkus-ledger)
  casehub-engine            (depends on quarkus-work-core + optionally quarkus-ledger)
  claudony                  (depends on quarkus-qhorus + implements casehub-engine SPIs)
```

---

## Capability Ownership — "Where Does X Live?"

| Capability | Owner | Notes |
|---|---|---|
| Immutable entry chain (Merkle Mountain Range) | `quarkus-ledger` | Domain-agnostic; consumers extend `LedgerEntry` via JPA JOINED |
| Cryptographic tamper evidence | `quarkus-ledger` | `LedgerVerificationService`, inclusion proofs, Ed25519 checkpoints |
| Actor trust scoring (Bayesian Beta + EigenTrust) | `quarkus-ledger` | `ActorTrustScore`, nightly `TrustScoreJob`, `TrustScoreRoutingPublisher` CDI events |
| GDPR Art.17 erasure / Art.22 decision records | `quarkus-ledger` | `LedgerErasureService`, `ComplianceSupplement` |
| W3C PROV-DM lineage export | `quarkus-ledger` | `LedgerProvExportService` |
| OTel trace linkage to audit entries | `quarkus-ledger` | `LedgerTraceListener` auto-populates `traceId` from active OTel span |
| Human task inbox (WorkItem lifecycle) | `quarkus-work` | 10 statuses, SLA, delegation, escalation, spawn |
| Worker routing / selection strategies | `quarkus-work-core` | `WorkBroker`, `WorkerSelectionStrategy` SPI — also used by casehub-engine |
| Label-based queue views | `quarkus-work-queues` | Optional module on quarkus-work |
| Semantic (embedding) worker matching | `quarkus-work-ai` | Optional module; `SemanticWorkerSelectionStrategy` |
| Outbound notifications (Slack, Teams, SMS, email) | `casehub-connectors` | `Connector` SPI; `quarkus-work-notifications` must delegate here |
| Agent-to-agent messaging (typed channels + messages) | `quarkus-qhorus` | 9 speech-act types, 5 channel semantics, 39 MCP tools |
| Agent commitment/obligation tracking | `quarkus-qhorus` | `Commitment` with 7-state lifecycle |
| Structured agent telemetry (EVENT observability) | `quarkus-qhorus` | `AgentMessageLedgerEntry` extends `LedgerEntry` |
| Case/process orchestration (choreography + WAITING) | `casehub-engine` | `CaseInstance`, `EventLog`, `WorkOrchestrator` |
| Worker provisioner SPIs (provision, lifecycle, context) | `casehub-engine` (defines) / `claudony` (implements) | `WorkerProvisioner`, `CaseChannelProvider`, `WorkerContextProvider`, `WorkerStatusListener` |
| Remote Claude CLI sessions | `claudony` | `TmuxService`, `SessionRegistry`, WebSocket streaming |
| Browser + agent authentication | `claudony` | WebAuthn passkeys + `X-Api-Key` header |
| Ecosystem CI dashboards | `casehub-parent` | `dashboard.yml`, `pr-dashboard.yml`, `full-stack-build.yml` |

---

## Key Boundary Rules

**Do not add orchestration logic to `quarkus-work`.** When a WorkItem completes, quarkus-work fires a CDI event and stops. CaseHub decides what completing a WorkItem *means* in a case context. "Complete the parent when all children complete" is CaseHub. "Mark the WorkItem EXPIRED when its deadline passes" is quarkus-work.

**Do not add WorkItem inbox management to `casehub-engine`.** casehub-engine depends on `quarkus-work-core` (`WorkBroker`) only. WorkItem entities, Flyway migrations, REST endpoints, and audit stores must not flow into the engine.

**Do not add trust scoring to `quarkus-work` or `casehub-engine`.** Trust derives from attestation history across *all* actors. It lives in quarkus-ledger and is surfaced via CDI routing events (`TrustScoreRoutingPublisher`). Consumers observe those events — they never compute trust themselves.

**Do not duplicate notification infrastructure.** `casehub-connectors` owns Slack/Teams/SMS/email outbound delivery. `quarkus-work-notifications` must use or delegate to `casehub-connectors`. Do not implement a new outbound channel in quarkus-work, casehub-engine, or claudony.

**Do not implement Qhorus channel semantics in `claudony`.** Claudony embeds Qhorus and adds CaseHub SPI implementations on top. It must not re-implement channel, message, or commitment logic.

**Do not put CaseHub SPI implementations in `casehub-engine`.** `WorkerProvisioner`, `CaseChannelProvider`, etc. are environment-specific operational contracts. casehub-engine defines them; deployment-specific implementations belong in the deploying application (e.g. Claudony).

**Do not use `quarkus-work` runtime in `casehub-engine`.** The engine depends on `quarkus-work-core` only (a Jandex library, no JPA, no REST). Pulling in the runtime module would introduce WorkItem entities, datasource requirements, and Flyway migrations into the engine.

---

## Cross-Cutting Concerns

### Persistence

| Concern | Owner | Mechanism |
|---|---|---|
| Base ledger tables (`ledger_entry`, `ledger_attestation`, etc.) | `quarkus-ledger` | Flyway V1000–V1004 |
| WorkItem tables | `quarkus-work` runtime | Flyway V1–V999 |
| Qhorus tables | `quarkus-qhorus` | Flyway V1–V7 (named `qhorus` datasource) |
| Engine tables | `casehub-engine` | Hibernate `drop-and-create` (no migrations — no prod instances yet) |
| Ledger subclass join tables | Each consumer | Consumer-owned Flyway migration, V1004+ numbering |

**Flyway numbering rule:** quarkus-ledger owns V1000–V1003. Domain tables: V1–V999. Ledger subclass join tables: V1004+. Violating this breaks FK constraints at startup.

**Named datasource rule:** Qhorus always runs on a named `qhorus` datasource — never share it with domain tables. Claudony uses separate `claudony` and `qhorus` persistence units.

### Observability

- OTel trace → ledger: `LedgerTraceListener` in quarkus-ledger auto-populates `traceId` at `@PrePersist`
- Agent telemetry: `AgentMessageLedgerEntry` (EVENT type) in quarkus-qhorus; queryable via `list_events` / `get_channel_timeline` MCP tools
- WorkItem audit: `AuditEntry` entity (always present) + optional tamper-evident `WorkItemLedgerEntry`
- Case decisions: `EventLog` (engine-internal, restart-safe) + optional `CaseLedgerEntry` (external, tamper-evident)

### Authentication

| Context | Owner | Mechanism |
|---|---|---|
| Extension-level (quarkus-work, quarkus-qhorus) | Consuming app | Extensions provide no auth — consuming app owns it |
| Browser → Claudony | `claudony` | WebAuthn passkeys (`quarkus-security-webauthn`) |
| Agent → Claudony | `claudony` | `X-Api-Key` header (`ApiKeyAuthMechanism`) |
| Channel write ACL | `quarkus-qhorus` | `allowed_writers` field on `Channel` |

### Privacy (GDPR)

All GDPR concerns centralised in `quarkus-ledger`:
- Art.17 right to erasure: `LedgerErasureService` + `ActorIdentityProvider` SPI
- Art.22 automated decision records: `ComplianceSupplement` (attached by consumers)
- PII sanitisation before storage: `DecisionContextSanitiser` SPI

### Agent Identity

Format: `{model-family}:{persona}@{major}` — e.g. `"claude:tarkus-reviewer@v1"`.  
Defined and owned by `quarkus-ledger` (ADR 0004). Major version bump resets trust baseline (Beta(1,1) prior).  
See [quarkus-ledger DESIGN.md §Agent Identity Model](https://raw.githubusercontent.com/casehubio/quarkus-ledger/main/docs/DESIGN.md).

---

## Known Overlap Risks

1. **`EventLog` vs `CaseLedgerEntry`** — casehub-engine has two case audit mechanisms. `EventLog` is internal (restart recovery). `CaseLedgerEntry` is the external tamper-evident ledger. If a lifecycle transition doesn't fire `CaseLifecycleEvent`, it won't be ledgered.

2. **`AuditEntry` vs `WorkItemLedgerEntry`** — quarkus-work has two audit mechanisms. `AuditEntry` is always-on and queryable. `WorkItemLedgerEntry` is opt-in and tamper-evident. Don't use `AuditEntry` for compliance claims.

3. **Notification duplication** — `casehub-connectors` and `quarkus-work-notifications` both provide Slack/Teams. These must converge to a single pipeline.

4. **`callerRef` format is implicit** — `WorkItem.callerRef` carries `case:{caseId}/pi:{planItemId}` (defined in `CallerRef` in casehub-engine). quarkus-work treats it as opaque. Any consumer using `callerRef` must know this format out of band.

---

## Per-Repo Deep Dives

| Repo | Raw URL |
|------|---------|
| `quarkus-ledger` | https://raw.githubusercontent.com/casehubio/casehub-parent/main/docs/repos/quarkus-ledger.md |
| `quarkus-work` | https://raw.githubusercontent.com/casehubio/casehub-parent/main/docs/repos/quarkus-work.md |
| `quarkus-qhorus` | https://raw.githubusercontent.com/casehubio/casehub-parent/main/docs/repos/quarkus-qhorus.md |
| `casehub-engine` | https://raw.githubusercontent.com/casehubio/casehub-parent/main/docs/repos/casehub-engine.md |
| `claudony` | https://raw.githubusercontent.com/casehubio/casehub-parent/main/docs/repos/claudony.md |
| `casehub-connectors` | https://raw.githubusercontent.com/casehubio/casehub-parent/main/docs/repos/casehub-connectors.md |
