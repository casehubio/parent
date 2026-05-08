# Casehubio Platform Architecture

> **Purpose:** Before implementing *anything* in any casehubio repo, run the Platform Coherence Protocol below.
> Every implementation decision is a platform decision. A feature that seems local may duplicate something elsewhere,
> belong in a different repo, or open an opportunity to consolidate an existing abstraction.
>
> **Per-repo deep dives:** [docs/repos/](https://github.com/casehubio/parent/tree/main/docs/repos/)

> **Platform docs:** Paths below are local (use `Read`). If the path does not exist — standalone clone on another machine — replace `/Users/mdproctor/claude/casehub/parent/docs/` with `https://raw.githubusercontent.com/casehubio/parent/main/docs/` and use `WebFetch`.

---

## Platform Coherence Protocol

Run this before implementing any feature, API, abstraction, SPI, or data model change in any casehubio repo. This is not a bureaucratic gate — it is the practice that keeps the platform orthogonal, intuitive, and free of duplication.

> **These protocols are living documents — never treat them as dogma.** When implementation reveals a case the protocol doesn't handle well, update the protocol in the same session. When a rule turns out to be wrong or too coarse, correct it. When a new pattern emerges that isn't captured, add it. A protocol that doesn't adapt to new evidence is just friction. The goal is a platform that improves continuously, not one that enforces yesterday's decisions on tomorrow's problems.

The protocols index is at [`docs/protocols/INDEX.md`](/Users/mdproctor/claude/casehub/parent/docs/protocols/INDEX.md). One file per rule, self-contained and retrievable independently. Add new entries there; link from PLATFORM.md when a capability ownership entry needs it.

### Step 1 — Does this already exist?

Check the Capability Ownership table below. Then check the per-repo deep-dive for the repos most likely to already have it.

Ask: *Is there a class, SPI, CDI event, or service in another repo that does this, or 90% of this?*

If yes → use the existing abstraction. If the existing one doesn't quite fit, extend it (in the right repo) rather than creating a parallel one here.

### Step 2 — Is this the right repo?

Check the Boundary Rules below. Then ask:

- Which tier does this belong to? (Foundation / Orchestration / Integration / Application)
- Is this domain-agnostic infrastructure (→ foundation), process coordination logic (→ casehub-engine), integration/deployment-specific (→ claudony), or domain-specific application logic (→ devtown / aml / clinical)?
- Will this be useful to consumers other than just the current one? If yes, it belongs lower in the stack.
- Does this depend on anything that the target repo is not supposed to depend on?

If the right repo is a different one → stop. Implement it there, then consume it from here.

### Step 3 — Does this create a consolidation opportunity?

Ask: *Is there something in another repo that does a similar thing awkwardly, that this new abstraction would make redundant or easier?*

If yes → propose refactoring the other repo to use the new abstraction, even if it's more work. Parallel implementations rot; consolidated abstractions improve everything downstream.

Known consolidation candidates:
- `casehub-work-notifications` Slack/Teams channels → should delegate to `casehub-connectors` (parent#5, open)
- `callerRef` format (`case:{id}/pi:{id}`) defined in casehub-engine but used opaquely by casehub-work → consider a shared constant or typed value in `casehub-work-api`

### Step 4 — Is this consistent with the platform pattern?

Check how the same concern is handled in the two or three most similar places in the platform. Then implement it the same way. Specifically:

- SPIs: follow the SPI placement rule (operational SPIs in `api/spi/`; persistence SPIs in model modules)
- Ledger subclasses: JOINED inheritance, consumer-owned V1004+ migration, domain-agnostic leaf hash
- CDI events: async (`@ObservesAsync`) for ledger capture; sync for routing decisions
- Named datasources: Qhorus always on `qhorus`, domain tables never mixed in
- Flyway numbering: V1000–V1003 = ledger; V1–V999 = domain; V1004+ = ledger subclass joins
- Module structure: pure-Java SPI modules have no Quarkus deps; core library modules have no JPA; full extensions have both
- **Persistence module split rule:** JPA entity classes MUST live in a separate module from the domain model SPI. Any artifact that bundles JPA entities forces every downstream consumer to configure a datasource — including test modules that use in-memory repos. The correct split: `<name>-api` (domain POJOs + SPIs, zero JPA), `<name>` or `<name>-hibernate` (JPA entities + migrations). `casehub-work` is the canonical example: `casehub-work-api` is JPA-free; the runtime module has entities and is kept at arm's length. Violating this rule causes cascading datasource failures across all downstream test suites.
- No-op defaults: every SPI gets a default no-op implementation in the owning repo
- **Application tier rule:** domain logic (git, PRs, clinical protocols, AML investigations) belongs in application repos. Foundation repos must remain domain-agnostic. If it requires knowledge of a specific business domain, it does not belong in foundation.
- **Submodule folder naming:** short descriptive names — no repo prefix. `api` not `casehub-work-api`; `runtime` not `casehub-ledger-runtime`. See [`docs/protocols/maven-submodule-folder-naming.md`](/Users/mdproctor/claude/casehub/parent/docs/protocols/maven-submodule-folder-naming.md).

### Step 5 — Does this need a platform-level doc update?

If the capability ownership table, boundary rules, or deep-dive docs need updating after this implementation, update `casehub-parent/docs/PLATFORM.md` and/or the relevant `docs/repos/*.md` file.

Also ask: **did this session surface a non-obvious pattern, a corrected rule, or a gotcha?** If yes — add it to `docs/protocols/` now, before the session ends. Patterns worth capturing include:
- A solution that required research or multiple failed attempts to find
- A rule in this document that turned out to be wrong or too coarse (update it)
- A concurrency, boundary, or schema decision that would otherwise be re-discovered independently
- An architectural boundary that was refined through analysis (update the relevant LAYERING or deep-dive doc)

### Step 6 — After implementing: propagate to existing consumers

This step runs **after** the implementation is complete, not before. When you ship a new shared abstraction — a utility, SPI, service, or pattern — immediately search all repos for existing code that does the same thing differently and update it to use the new abstraction.

Do not leave parallel implementations in place. Parallel implementations rot: they diverge over time, create inconsistency in the audit record, produce different behaviour for the same conceptual operation, and make the codebase harder for LLMs to reason about consistently.

**The propagation checklist:**
1. `grep -r` across all repos for the pattern the new abstraction replaces
2. For each hit: replace with the new abstraction or open a tracked issue if the update requires a separate session
3. If a consumer repo needs the new abstraction and it isn't published yet: open the issue, link it to the implementation issue, don't leave it undocumented
4. Update the capability ownership table in this document if a capability has moved or consolidated

---

## Development Session Protocol

Before designing or implementing anything, run this sequence:

1. **Brainstorm first** — invoke `superpowers:brainstorming` before proposing a design. Explore the problem space, surface alternatives, understand constraints. Do not jump to implementation.
2. **TDD** — invoke `superpowers:test-driven-development` before writing implementation code. Name unit tests, integration tests, happy-path tests, robustness tests, and correctness tests as part of planning — not as an afterthought.
3. **Review before committing** — invoke `superpowers:requesting-code-review` before any commit that completes meaningful work.
4. **IntelliJ first** — for any rename, move, find-references, or type hierarchy query, use IntelliJ MCPs before reaching for bash. See [IntelliJ MCP tool guide](#intellij-mcp-tool-guide) below.

---

## What We're Building

A production-grade, compliance-first infrastructure stack for multi-agent AI systems on Quarkus. Targeted at regulated deployments (EU AI Act Art.12, GDPR Art.17/22).

Four tiers, always kept separate:
- **Foundation** — audit ledger, human task primitives, agent communication mesh, outbound connectors. Independently embeddable in any Quarkus app. Domain-agnostic.
- **Orchestration** — `casehub-engine` coordinates agents via hybrid choreography+blackboard. Depends on foundation only.
- **Integration** — `claudony` wires everything together and surfaces it in a browser dashboard. Depends on orchestration.
- **Application** — domain-specific applications built on the foundation. Each is a separate repo with no domain knowledge in the foundation. The pattern: bring your domain logic, use foundation primitives, modify nothing below.

---

## Repository Map

| Repo | GitHub | One-liner | Tier |
|------|--------|-----------|------|
| `casehub-parent` | [casehubio/parent](https://github.com/casehubio/parent) | BOM, CI dashboards, full-stack build tooling | — |
| `casehub-ledger` | [casehubio/ledger](https://github.com/casehubio/ledger) | Immutable tamper-evident audit ledger + trust scoring | Foundation |
| `casehub-work` | [casehubio/work](https://github.com/casehubio/work) | Human task lifecycle (WorkItem inbox, SLA, delegation, routing) | Foundation |
| `casehub-qhorus` | [casehubio/qhorus](https://github.com/casehubio/qhorus) | Peer-to-peer agent communication mesh | Foundation |
| `casehub-connectors` | [casehubio/connectors](https://github.com/casehubio/connectors) | Outbound message connectors (Slack, Teams, SMS, email) | Foundation |
| `casehub-engine` | [casehubio/engine](https://github.com/casehubio/engine) | Hybrid choreography+blackboard orchestration engine | Orchestration |
| `claudony` | [casehubio/claudony](https://github.com/casehubio/claudony) | Remote Claude CLI sessions + unified ecosystem dashboard | Integration |
| `casehub-poc` | [casehubio/casehub](https://github.com/casehubio/casehub) | **Retiring** — original POC; no new features | — |

Application tier (devtown, aml, clinical): see [APPLICATIONS.md](/Users/mdproctor/claude/casehub/parent/docs/APPLICATIONS.md).

---

## Build / Dependency Order

```
casehub-parent              (BOM — publish first; all others import it)
  casehub-ledger            (no casehubio deps)
  casehub-connectors        (no casehubio deps)
  casehub-work              (core: zero casehubio deps; ledger module: depends on casehub-ledger)
  casehub-qhorus            (depends on casehub-ledger)
  casehub-engine            (depends on casehub-work-core + optionally casehub-ledger)
  claudony                  (depends on casehub-qhorus + implements casehub-engine SPIs)

  — Application tier (opt-in, off by default in CI): see APPLICATIONS.md —
```

---

## Capability Ownership — "Where Does X Live?"

| Capability | Owner | Notes |
|---|---|---|
| Immutable entry chain (Merkle Mountain Range) | `casehub-ledger` | Domain-agnostic; consumers extend `LedgerEntry` via JPA JOINED |
| Cryptographic tamper evidence | `casehub-ledger` | `LedgerVerificationService`, inclusion proofs, Ed25519 checkpoints |
| Actor trust scoring (Bayesian Beta + EigenTrust) | `casehub-ledger` | `ActorTrustScore`, nightly `TrustScoreJob`, `TrustScoreRoutingPublisher` CDI events |
| GDPR Art.17 erasure / Art.22 decision records | `casehub-ledger` | `LedgerErasureService`, `ComplianceSupplement` |
| W3C PROV-DM lineage export | `casehub-ledger` | `LedgerProvExportService` |
| OTel trace linkage to audit entries | `casehub-ledger` | `LedgerTraceListener` auto-populates `traceId` from active OTel span |
| Human task inbox (WorkItem lifecycle) | `casehub-work` | 10 statuses, SLA, delegation, escalation, spawn |
| M-of-N parallel WorkItem completion (group policy primitive) | `casehub-work` | `MultiInstanceCoordinator`; `WorkItemGroupLifecycleEvent`; see LAYERING.md |
| Worker routing / selection strategies | `casehub-work-core` | `WorkBroker`, `WorkerSelectionStrategy` SPI — also used by casehub-engine |
| Label-based queue views | `casehub-work-queues` | Optional module on casehub-work |
| Semantic (embedding) worker matching | `casehub-work-ai` | Optional module; `SemanticWorkerSelectionStrategy` |
| Outbound notifications (Slack, Teams, SMS, email) | `casehub-connectors` | `Connector` SPI; `casehub-work-notifications` must delegate here |
| Agent-to-agent messaging (typed channels + messages) | `casehub-qhorus` | 9 speech-act types, 5 channel semantics, MCP tools |
| Agent commitment/obligation tracking | `casehub-qhorus` | `Commitment` with 7-state lifecycle |
| Normative audit of all agent interactions | `casehub-qhorus` | `MessageLedgerEntry` extends `LedgerEntry`; all 9 speech-act types recorded |
| Case/process orchestration (choreography + WAITING) | `casehub-engine` | `CaseInstance`, `EventLog`, `WorkOrchestrator` |
| Worker provisioner SPIs (provision, lifecycle, context) | `casehub-engine` (defines) / `claudony` (implements) | `WorkerProvisioner`, `CaseChannelProvider`, `WorkerContextProvider`, `WorkerStatusListener` |
| Remote Claude CLI sessions | `claudony` | `TmuxService`, `SessionRegistry`, WebSocket streaming |
| Browser + agent authentication | `claudony` | WebAuthn passkeys + `X-Api-Key` header |
| Ecosystem CI dashboards | `casehub-parent` | `dashboard.yml`, `pr-dashboard.yml`, `full-stack-build.yml` |
| Application domain logic (devtown, aml, clinical) | Application tier | See [APPLICATIONS.md](/Users/mdproctor/claude/casehub/parent/docs/APPLICATIONS.md) |

---

## Key Boundary Rules

**Do not add orchestration logic to `casehub-work`.** When a WorkItem completes, casehub-work fires a CDI event and stops. Homogeneous M-of-N group completion is casehub-work. Heterogeneous plan-level completion is casehub-engine. "Mark the WorkItem EXPIRED when its deadline passes" is casehub-work.

**Do not add WorkItem inbox management to `casehub-engine`.** casehub-engine depends on `casehub-work-core` (`WorkBroker`) only. WorkItem entities, Flyway migrations, REST endpoints must not flow into the engine.

**Do not add trust scoring to `casehub-work` or `casehub-engine`.** Trust lives in casehub-ledger and is surfaced via CDI routing events (`TrustScoreRoutingPublisher`). Consumers observe those events — they never compute trust themselves.

**Do not duplicate notification infrastructure.** `casehub-connectors` owns Slack/Teams/SMS/email. `casehub-work-notifications` must delegate here.

**Do not implement Qhorus channel semantics in `claudony`.** Claudony embeds Qhorus and adds SPI implementations. It must not re-implement channel, message, or commitment logic.

**Do not put CaseHub SPI implementations in `casehub-engine`.** casehub-engine defines them; deployment-specific implementations belong in the deploying application.

**Do not use `casehub-work` runtime in `casehub-engine`.** The engine depends on `casehub-work-core` only.

**Do not add domain logic to foundation repos.** If the capability requires knowledge of software development, clinical trials, or financial crime, it belongs in an application repo.

---

## Cross-Cutting Concerns

### Persistence

| Concern | Owner | Mechanism |
|---|---|---|
| Base ledger tables | `casehub-ledger` | Flyway V1000–V1004 |
| WorkItem tables | `casehub-work` runtime | Flyway V1–V999 |
| Qhorus tables | `casehub-qhorus` | Flyway V1–V7 (named `qhorus` datasource) |
| Engine tables | `casehub-engine` | Hibernate `drop-and-create` (no migrations yet) |
| Ledger subclass join tables | Each consumer | Consumer-owned Flyway, V1004+ numbering |

**Flyway numbering rule:** casehub-ledger owns V1000–V1003. Domain: V1–V999. Ledger subclass joins: V1004+.

**Named datasource rule:** Qhorus always runs on named `qhorus` datasource. Claudony uses separate `claudony` and `qhorus` persistence units.

### Observability

- OTel trace → ledger: `LedgerTraceListener` auto-populates `traceId` at `@PrePersist`
- Agent interactions: `MessageLedgerEntry` records all 9 message types
- WorkItem audit: `AuditEntry` (always-on) + optional `WorkItemLedgerEntry` (tamper-evident)
- Case decisions: `EventLog` (engine-internal) + optional `CaseLedgerEntry` (external, tamper-evident)

### Authentication

| Context | Owner | Mechanism |
|---|---|---|
| Extension-level | Consuming app | Extensions provide no auth |
| Browser → Claudony | `claudony` | WebAuthn passkeys |
| Agent → Claudony | `claudony` | `X-Api-Key` header |
| Channel write ACL | `casehub-qhorus` | `allowed_writers` on `Channel` |

### Privacy (GDPR)

All GDPR concerns centralised in `casehub-ledger`:
- Art.17 erasure: `LedgerErasureService` + `ActorIdentityProvider` SPI
- Art.22 decision records: `ComplianceSupplement`
- PII sanitisation: `DecisionContextSanitiser` SPI

### Agent Identity

Format: `{model-family}:{persona}@{major}` — e.g. `"claude:analyst@v1"`. Defined in casehub-ledger ADR 0004. Major version bump resets trust baseline.

### Implementation Protocols

Rules that apply across all casehubio modules:

| Protocol | Rule |
|---|---|
| [SQL type portability](protocols/sql-type-portability.md) | `DOUBLE PRECISION` not `DOUBLE`; `SMALLINT` not `TINYINT` |
| [Flyway migration rules](protocols/flyway-migration-rules.md) | Version namespace ranges; `MODE=PostgreSQL` in all H2 test URLs |
| [Optional module pattern](protocols/optional-module-pattern.md) | Jandex library module; zero cost when absent |
| [Quarkus test database](protocols/quarkus-test-database.md) | H2 `MODE=PostgreSQL`; Testcontainers for dialect validation |
| [Submodule folder naming](protocols/maven-submodule-folder-naming.md) | Short names — no repo prefix. `api` not `casehub-work-api` |

Full index: [`docs/protocols/INDEX.md`](/Users/mdproctor/claude/casehub/parent/docs/protocols/INDEX.md)

---

## Known Overlap Risks

1. **`EventLog` vs `CaseLedgerEntry`** — `EventLog` is internal (restart recovery). `CaseLedgerEntry` is external (tamper-evident). If a lifecycle transition doesn't fire `CaseLifecycleEvent`, it won't be ledgered.
2. **`AuditEntry` vs `WorkItemLedgerEntry`** — `AuditEntry` is always-on. `WorkItemLedgerEntry` is opt-in tamper-evident. Don't use `AuditEntry` for compliance claims.
3. **Notification duplication** — `casehub-connectors` and `casehub-work-notifications` both provide Slack/Teams. Must converge (parent#5, open).
4. **`callerRef` format is implicit** — carries `case:{caseId}/pi:{planItemId}`. casehub-work treats it as opaque. Consumers must know this format out of band.

---

## Per-Repo Deep Dives

| Repo | Local path |
|------|-----------|
| `casehub-ledger` | `/Users/mdproctor/claude/casehub/parent/docs/repos/casehub-ledger.md` |
| `casehub-work` | `/Users/mdproctor/claude/casehub/parent/docs/repos/casehub-work.md` |
| `casehub-qhorus` | `/Users/mdproctor/claude/casehub/parent/docs/repos/casehub-qhorus.md` |
| `casehub-engine` | `/Users/mdproctor/claude/casehub/parent/docs/repos/casehub-engine.md` |
| `claudony` | `/Users/mdproctor/claude/casehub/parent/docs/repos/claudony.md` |
| `casehub-connectors` | `/Users/mdproctor/claude/casehub/parent/docs/repos/casehub-connectors.md` |
| `casehub-devtown` | `/Users/mdproctor/claude/casehub/parent/docs/repos/casehub-devtown.md` |
| `casehub-aml` | `/Users/mdproctor/claude/casehub/parent/docs/repos/casehub-aml.md` |
| `casehub-clinical` | `/Users/mdproctor/claude/casehub/parent/docs/repos/casehub-clinical.md` |

Application tier: see [APPLICATIONS.md](/Users/mdproctor/claude/casehub/parent/docs/APPLICATIONS.md)
