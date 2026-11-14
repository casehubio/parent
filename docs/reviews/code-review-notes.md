# CaseHub Code Review Notes

Running notes, one section per repo. Brief by design. Add to it as each repo is reviewed.

Severity: **S1** exploitable / data loss · **S2** real bug · **S3** design or hygiene.
Status: `open` · `confirmed` (reproduced) · `issue #N` · `fixed`.

## Working context (read first after a context reset)

**Brief from owner.** Review each CaseHub repo for code quality, design, end-user ease of use, bugs and potential issues, plus market positioning. Platform is the base everything builds on. Owner codes mainly in Java. Keep these notes brief and accumulate per repo.

**Process per repo.**
1. Clone or locate, record commit in the review log.
2. Read CLAUDE.md, then the largest and most security- or integrity-critical sources first.
3. Check every cross-repo theme (T1..) and the "carry into downstream repos" questions from earlier repos.
4. Add a repo section here: strengths, findings table, carry-over answers, not-yet-reviewed, new carry-forward questions.
5. Commit and push this file to branch `claude/optimistic-archimedes-slr7c2` on `casehubio/parent`. Owner chose to push findings in full (2026-11-14) despite the repo being public.
6. Report in chat: verdict, top findings, positioning, open questions.

**Environment facts.**
- Local clones: `/home/user/platform`, `/home/user/parent`, `/home/user/casehub-ops`, `/home/user/casehub-desiredstate`, `/home/user/scaffold`; read-only clone `/home/user/casehubio/ledger`.
- Other repos: `list_repos` then `add_repo` (read access works for public repos; clone lands under `/home/user/casehubio/<name>`).
- Builds do not run here: `casehub-parent` POM resolves from GitHub Packages, unavailable offline. All reviews so far are static reads. Say so in each report.
- No PRs or issues unless the owner asks.

**Owner context and corrections so far.**
- BOM lives in `casehub-parent`; do not report "no BOM".
- Onboarding is in progress and is playbook-led (`platform/playbooks`). Report gaps as "entry point missing", not "no onboarding".
- Identity is delegable via `casehub-platform-oidc` (Quarkus OIDC, so Keycloak works). Built-in `authn` is a deliberate optional path. Authz has no external adapter yet.
- Owner has not yet answered the open questions at the bottom.

**Repo map (one line each, extend as reviewed).**
- **platform** (~98k lines, 241 modules): SPIs + defaults for identity, tenancy, ACL, preferences, notifications, registry, agents/LLM backends, MCP exposure, YAML playbooks, simulation. Pattern: `-core` POJO, Quarkus wiring, generated Spring.
- **ledger** (~23k lines): append-only audit log on platform. `LedgerEntry` JPA JOINED base; consumers subclass (`casehub-work`, `casehub-qhorus`). Merkle frontier per subject, attestations, EigenTrust scores, pseudonymised actors, retention, KMS signers.
- **work** (~40k lines): human/agent task layer. `WorkItemService` lifecycle, stores (JPA, memory, Mongo), optional Postgres RLS via `TenantAwareStore`, timers/expiry, queues, ledger adapter (`ledger/`), qhorus and flow adapters. Read-only clone `/home/user/casehubio/work`.
- **qhorus** (~45k lines): agent/human messaging mesh. Channels, messages, commitments, watchdog, gateway/delivery, A2A endpoint, cluster relay, own ledger repository and `MessageLedgerEntry`. Read-only clone `/home/user/casehubio/qhorus`.
- **neocortex** (~123k lines, 89 modules): AI reasoning layer. ONNX inference, hybrid RAG on Qdrant, CBR, memory backends (moved here from platform), corpus management, mind maps, Bayesian inference, cognition. Read-only clone `/home/user/casehubio/neocortex`.
- **desiredstate**, **ops**, **scaffold**: cloned, not reviewed. Others (work, qhorus, engine, eidos, connectors, ...) not cloned.

**Build order** (from `parent/build/modules-core.csv` dependencies; the file says row order is build order but rows are not topologically sorted, e.g. desiredstate is listed before engine and ras): platform; worker, ledger, connectors, pages; eidos; neocortex, qhorus; work; engine; ras, agency, workers, claudony; desiredstate; ops. Reviewed: platform, ledger, work, qhorus, neocortex (first pass). Not yet: worker, connectors, pages, eidos (all upstream of engine), then engine. Follow the owner's stated order; check this list before suggesting one.

## Review log

| Repo | Date | Commit | Method | Depth |
|---|---|---|---|---|
| platform | 2026-11-14 | d9805fd | static read, not built | foundations deep, rest sampled |
| ledger | 2026-11-14 | 11018f8 | static read, not built | core deep (hashing, Merkle, save path, signing, erasure, retention, API); trust maths, KMS signers, examples sampled or skipped |
| work | 2026-11-14 | adccdbc | static read, not built | lifecycle service, REST lifecycle API, tenancy/RLS, ledger integration deep; queues, ai, issue-tracker, flow, federation, progress, mongodb not read |
| qhorus | 2026-11-14 | 86adf50 | static read, not built | identity/tenancy, ledger integration, erasure, sender/ACL path, cluster filter deep; message/commitment/watchdog logic, gateway, A2A detail, compliance-report, slack, push, graphql not read |
| neocortex | 2026-11-14 | 4af2ac6 | static read, not built | Two passes. Read: RAG/Qdrant tenancy, exposed APIs, ONNX wrapper, `CognitionCore`, mood, appraisal (`EmotionMapper`, LLM appraisal), regulation prompt, CAPS settler, memory retriever, Bayes provenance, eval/quality docs, repo-wide greps. Still unread: strategy learning, goals, narrative, user/mental models, belief revision internals, mind-map consolidation phases, `CognitiveDerivationEngine`, CBR algorithms, corpus/knowledge pipeline, memory backends in detail |

## Cross-repo themes

Patterns found once that are likely to recur. Check each in every repo.

- **T1 Fail-open defaults.** Missing dependency gives a working, wide-open app. Look for `@DefaultBean` no-ops that allow, default methods returning `true`.
- **T2 Hand-rolled security.** JWT, sessions, token compare, JSON by string concat. Prefer a library.
- **T3 Ambient tenancy.** Tenant read from injected `CurrentPrincipal` rather than passed. Breaks in background jobs, schedulers, cross-tenant admin.
- **T4 Identity from string shape.** `ActorTypeResolver` prefixes (`system:`, `agent:`). Flag any privilege check on `isSystem()` / `actorType()`.
- **T5 Unsandboxed expressions.** Any user-supplied MVEL reaching `ExpressionEngine.compile`.
- **T6 List vs check drift.** Listing queries that disagree with the single-item authorization check.
- **T7 Check-then-act on stores.** Non-atomic consume/upsert; select-then-insert.
- **T8 Paging after filtering.** Post-fetch filtering that shortens a page and nulls the cursor.
- **T9 Reflection dispatch surface.** `getMethods()` on bean classes instead of the SPI interface; interface-level `@RolesAllowed` assumed enforced.
- **T10 `PolicyEnforcer` use.** Retries everything, timeout hops threads (loses request scope and transactions), no circuit breaker despite the API.
- **T11 Unconfigured clients.** `HttpClient.newHttpClient()` with no timeouts; per-class `new ObjectMapper()`.
- **T12 Docs claim vs code.** CLAUDE.md / guide statements the code does not honour.
- **T13 Untested wiring modules.** Quarkus/Spring/JPA shells with zero tests.
- **T15 Client-supplied attribution.** API accepts `actorId` / attestor from the request instead of the authenticated principal.
- **T16 Ambiguous canonical form.** Delimiter-joined hashing or signing input with no escaping or length prefix.
- **T17 Load-everything jobs.** Scheduled jobs that read a whole table into memory in one transaction.
- **T18 Quarkus/Spring hand-copies.** Logic duplicated across the two stacks rather than shared in a core.
- **T19 Bean displacement side effects.** A module's non-default bean or higher-priority `@Alternative` silently replacing another repo's implementation app-wide. Check every `implements <other repo SPI>` and every `@Priority`.
- **T20 Bypassing an upstream pipeline.** Consumer re-implements a write path (own sequence, own hash) instead of calling the owner's service.
- **T21 Stale copy after extraction.** Code moved to a new module but left behind in the old one under the same class names (P11, N7).
- **T22 Licence files.** No `LICENSE`/`NOTICE` in any of the nine repos checked; only the parent POM declares Apache 2.0. Neocortex carries 33 ASF-headed files that refer to a NOTICE file.
- **T14 Onboarding.** README, quick start, stability tiers. BOM lives in `casehub-parent`; each repo's README/guide should say so.

## platform

Strengths: framework-neutral cores with thin Quarkus/Spring wiring; consistent store SPIs; `@McpDomain` to GraphQL + REST + MCP + playbook step; simulation; no TODOs.

### Findings

| ID | Sev | Theme | Where | Note | Status |
|---|---|---|---|---|---|
| P1 | S1 | T9 | `callback-client-core` `CallbackDispatcher` | Auth is "header non-blank". Any public method on registered bean invocable. `CallbackInvoker` ignores `credentialRef`. | open |
| P2 | S1 | T5 | `expression-core` `MvelExpressionEngine` | No sandbox seen; `validate()` only checks blank. Subscription filters accept MVEL, API has no role. Not exploited. | open |
| P3 | S2 | T2 | `authn-core` `JwtIssuerCore` | ES256 signed as DER, JWS needs R‖S (`...inP1363Format`). Test verifies with same alg. Hand-built JSON, no control-char escaping. | open |
| P4 | S1 | T7 | `SessionManagerCore`, `JpaRefreshTokenStore` | Non-atomic refresh consume defeats reuse detection. Plaintext token as PK. Groups frozen for refresh TTL. | open |
| P5 | S2 | T8 | `acl-jpa` `JpaAccessControlProvider.accessibleResources(AclQuery)` | Denied rows removed after `limit+1` fetch, short page, null cursor, results lost. | open |
| P6 | S2 | T6 | `acl-jpa`, `acl-inmem-core` | Listings return literal `type:*`, ignore wildcard deny, include children under a denied parent. | open |
| P7 | S1 | T1 | `platform-api` `DefaultProcessExecutor` | No allow-list means allow all. Output over limit with no timeout hangs. Large stdin deadlocks. | open |
| P8 | S2 | T1,T2 | `streams-webhook-core` `WebhookReceiver` | `credentialRef` without bearer token skips auth. Non-constant-time compare. Case-sensitive header lookup. | open |
| P9 | S2 | | `yaml-core` `DefaultOrcSemaphore` | Re-entrancy by thread name; unnamed virtual threads collide. Replenisher can exceed max permits. | open |
| P10 | S2 | T7 | `yaml-core` `CorrelationScope` | Lost wakeup between `pending.get` and early-arrival put. | open |
| P11 | S2 | T9 | `mcp`, `mcp-core` | Duplicate FQCN `DomainModelRegistry`. Interface-only domains (`AclApi`) rely on interface `@RolesAllowed`; no test. | open |
| P12 | S3 | T1 | `AccessControlProvider`, `DefaultBeans` | `canAccess` defaults `true`; default principal `system`; allow-all ACL; auto-approve worker policy. | open |
| P13 | S3 | T4 | `ActorTypeResolver` | Type from actorId prefix; null is SYSTEM. No privileged use found in platform. | open |
| P14 | S3 | T12 | `platform-api` pom | Not zero-dep: CloudEvents compile, Mutiny, Jackson, mcp-api. Holds implementations. | open |
| P15 | S3 | | `Path` | Public ctor allows inconsistent state; `of("a/b") != parse("a/b")`; global mutable parser; `parent()` null not root. | open |
| P16 | S3 | T10,T12 | `governance-core` `DefaultPolicyEnforcer` | See T10. Wraps in `RetryExhaustedException` even with no retries. | open |
| P17 | S3 | T3 | ACL providers | Cross-tenant admin: parent lookup uses admin's own tenant. | open |
| P18 | S3 | T11 | repo-wide | 43 `new ObjectMapper()`, 11 bare `HttpClient`, 276 inline `java.util.` names, 17 `synchronized`. | open |
| P19 | S3 | T13 | repo-wide | ~60 modules with no tests (`registration`, `user-jpa`, `session-jpa`, `agent-http`, `datasource-alpha`). No static analysis or coverage in POM. | open |
| P20 | S3 | T14 | README, guides | README is two badges; no stability tiers across 241 modules. BOM exists in `casehub-parent` (corrected). Onboarding in progress via `playbooks/`. | in progress |

### Corrections and context (owner feedback, 2026-11-14)

- **BOM:** in `casehub-parent` (210 platform entries). Original "no BOM" finding was wrong; gap is only that platform docs don't point to it.
- **Onboarding:** playbooks are the intended path. 76 YAML files in 10 categories, each small and self-describing, with simulated `.test.yaml` tests. Good base. Missing: an entry point (README link, suggested reading order, how to run one).
- **Security is SPI-based, checked:**
  - Identity: yes. `casehub-platform-oidc` bridges Quarkus `SecurityIdentity`, so Keycloak or any OIDC IdP works via `quarkus-oidc`. `scim` covers group lookup against Keycloak/Okta/Azure AD. No Keycloak-specific module, and no integration test against Keycloak (spec defers it to consumers).
  - Authn: built-in `authn` is a deliberate choice (epic 525 D1, "platform-native ceremonies"; external IdP delegation listed as rejected alternative). It is optional and separate from the OIDC path. P3/P4 apply only when `authn` is used.
  - Authz: Keycloak Authorization Services considered and rejected in `2026-06-01-acl-design.md` (runtime dependency). OpenFGA/SpiceDB researched there, no adapter built. ACL SPI is pluggable, so an adapter is possible.
  - So: P1, P2, P5–P8, P12 are independent of IdP choice. Fail-open default (P12) still applies when `oidc` is present but no ACL backend is.
- **Open:** nothing in platform verifies `authn`-issued JWTs and there is no JWKS endpoint; which component validates them?

### Not yet reviewed

Generators (`graphql-generator`, `spring-generator`, `rest-spring-generator`), `yaml-step-runtime`, `playbook-compiler`, notification dispatch pipeline, Spring modules, `agent-config-core` remote loader, `registration-core`, `agent-gate-core`, `platform-signing`, `identity-core`.

### Carry into downstream repos

- Who calls `isSystem()` / `actorType()` for a privilege decision? (P13)
- Who registers `@CallbackEligible` SPIs, and which are sensitive? (P1)
- Who accepts expressions from users? (P2)
- Who relies on `PolicyEnforcer` timeouts inside a request or transaction? (P16)
- Who ships without a real `AccessControlProvider` on the classpath? (P12)
- Who uses `accessibleResources*` for UI lists? (P5, P6)

## ledger

Strengths: `tenancyId` passed explicitly through the SPI (avoids T3); Merkle code follows RFC 6962 domain separation and reads correct; per-subject row lock serialises appends; pseudonymisation by token is the right shape for erasure vs immutability; 9 worked examples.

### Findings

| ID | Sev | Theme | Where | Note | Status |
|---|---|---|---|---|---|
| L1 | S1 | T15 | `LedgerEntryApiCore.appendEntry`, `LedgerMutationResolver.appendLedgerEntry` | `actorId` taken from request; no role check. Any caller can write audit entries attributed to anyone. | open |
| L2 | S1 | T15 | `DefaultOutcomeRecorder.addAttestation`, attestation REST/GraphQL | Attestor is the configured default id, not the caller. No role check, no limit. Anyone can move trust scores under the system attestor's name. | open |
| L3 | S1 | T16 | `LedgerEntry.canonicalBytes()` | Pipe-joined, no escaping. `actorId="a\|b"` collides with `actorId="a", actorRole="b"`. Optional trailing parts (supplement, domainData, domain content) are interchangeable. Same weakness in `ErasureReceiptLedgerEntry.domainContentBytes`. Fix needs a format version. | open |
| L4 | S2 | T16 | `LedgerEntry.canonicalBytes()` | Not hashed or signed: `id`, `traceId`, `actorDid`, `agentPublicKey`, `agentKeyRef`. Signer attribution can be swapped without breaking the digest. | open |
| L5 | S2 | | `VerificationServiceCore.verify` | Compares recomputed values to digest and frontier in the same DB. Detects accidental corruption only. DB-level tamper needs the external checkpoint, which is off by default. No DB triggers or grants enforcing append-only. | open |
| L6 | S2 | T11 | `LedgerMerklePublisher.publish` | Fires async POST inside the transaction (publishes roots that may roll back). No retry or outbox. Parses private key and builds `HttpClient` on every append. Checkpoint lacks tenancy and timestamp. | open |
| L7 | S2 | T17 | `LedgerRetentionJob.runRetention` | `listAll()` loads the entire ledger, all tenants, daily, in one transaction. Groups by `subjectId` without tenancy. Per-subject catch inside one transaction. | open |
| L8 | S2 | | `LedgerRetentionJob`, `VerificationServiceCore.inclusionProof` | Retention deletes entries but leaves frontier and sequence rows. A later append makes `verify` fail permanently; proof index `seq-1` goes out of range. | open |
| L9 | S2 | T6 | `JpaLedgerEntryRepository.streamByActorId`, `countByActorAndVerdict` | Pass raw actorId; `findByActorId` tokenises. With pseudonymisation on, these return nothing for humans. | open |
| L10 | S2 | T3 | `LedgerErasureService` | Receipt stores the raw erased actorId in an immutable entry; subjectId is a deterministic UUID of it. Erasure is cross-tenant and the receipt always goes to the default tenant. `erase()` calls `em.clear()` mid-transaction. | open |
| L11 | S2 | T4 | `InternalActorIdentityProvider.tokenise` | Only HUMAN (or null) actor types are tokenised; type is caller-supplied or prefix-derived (P13). Mislabelled humans are stored raw. | open |
| L12 | S2 | T1 | `AgentEntrySigner.sign` | Signing failure logs a warning and stores the entry unsigned. | open |
| L13 | S3 | | attestations | Not in the Merkle tree and not hashed, yet they drive trust scores. | open |
| L14 | S3 | | `saveAttestation` | `REQUIRES_NEW`: commits even if caller rolls back; cannot see an entry saved in the caller's open transaction. | open |
| L15 | S3 | | `VerificationServiceCore.inclusionProof` | Loads every entry for the subject. Proof size is O(log N), cost is O(N); docs say O(log N). | open |
| L16 | S3 | T18 | `LedgerMerklePublisher` vs `MerklePublisherCore`; `SpringJpaLedgerEntryRepository` vs Jpa | Verbatim duplicates. Spring save pipeline is a hand copy with no tests. `AgentCryptographicVerifier` repeats platform's `SignatureVerifier` key decoding. | open |
| L17 | S3 | | `LedgerEntry` | "Immutable" entry is all public mutable fields; `supplements` and `supplementJson` can drift; `sequenceNumber` is `int`. | open |
| L18 | S3 | T12 | CLAUDE.md | States Quarkus 3.32.2; parent is on 3.39.3. | open |
| L19 | S3 | T13,T14 | repo-wide | No tests in `ledger-jpa-common`, `ledger-spring-jpa`, `ledger-spring`, `ledger-signing-spring`. README is two badges. | open |

### Platform carry-over answers

- `isSystem()`/`actorType` for privilege: not for authorization, but actor type gates pseudonymisation (L11).
- Callback SPIs, user expressions, `PolicyEnforcer`: no use found in what was read.
- ACL: ledger API does no access checks at all (L1, L2), so P12 is moot here.

### Not yet reviewed

EigenTrust and trust-score maths, KMS/Vault signing clients, federation import/export, `AuditedInterceptor`, PROV serializer, key rotation, in-memory repository parity, examples.

### Carry into downstream repos

- Who writes ledger entries, and do they set `actorId` from the principal? (L1)
- Who reads trust scores for routing or gating decisions? (L2)
- Any subclass overriding `domainContentBytes()` with delimiter-joined fields? (L3)
- Anyone enabling retention on long-lived subjects? (L8)

## work

Strengths: real README with a clear pitch; 10-state lifecycle with guarded transitions; `@Version` optimistic locking on `WorkItemEntity`; optional Postgres row-level security that fails closed when the tenant setting is absent; exclusion policy with blocked-attempt audit; expiry scans are filtered queries, not full loads.

### Findings

| ID | Sev | Theme | Where | Note | Status |
|---|---|---|---|---|---|
| W1 | S1 | T15 | `WorkItemLifecycleApi`, `DefaultWorkItemLifecycleApi` | `claimant` / `actor` are plain request parameters, not `@ContextParam("actorId")`. No role check. Caller can act as anyone. | open |
| W2 | S1 | | `WorkItemService` | No check that claimant is in `candidateUsers`/`candidateGroups`, and no check that actor is the assignee on `start`, `complete`, `reject`, `delegate`. Only accept/decline delegation check. Exclusion (four-eyes) policy is checked against the caller-supplied id, so W1 bypasses it. | open |
| W3 | S1 | T19 | `ledger/` `JpaWorkItemLedgerEntryRepository` | `@ApplicationScoped`, implements `LedgerEntryRepository`, so it displaces ledger's `@DefaultBean` repository app-wide. Its `save` is only `em.persist`: no sequence allocation, digest, frontier, pseudonymisation, signing, enrichers or sanitiser for any caller. By CDI rules; confirm with a test. | open |
| W4 | S1 | T20 | `ledger/` `LedgerEventCapture` | Own sequence (`latest + 1`, unlocked, races), own digest and frontier update. Raw human actorId stored, so ledger erasure (L10) does not cover work entries. No agent signature, no checkpoint publish. | open |
| W5 | S1 | | `LedgerEventCapture` (spawned branch) | Sets `causedByEntryId` on an already-persisted child entry. That field is in `canonicalBytes()`, so the child's digest and the subject's Merkle root no longer verify. Mutates an immutable entry. | open |
| W6 | S1 | T19 | `TenantScopedPrincipal` | `@Alternative @Priority(150)` outranks platform OIDC principal (`@Priority(100)`); platform javadoc claims the opposite. With work + oidc on the classpath every HTTP request would be actor `system`, default tenant, no groups. By CDI rules; confirm with a test. | open |
| W7 | S2 | | `TenantAwareStore.withCrossTenantQuery` | `SET LOCAL ROLE casehub_crosstenancy` is never reset, so RLS stays bypassed for the rest of the transaction. | open |
| W8 | S2 | T3 | `WorkItemService.create` | `tenancyId` and `createdBy` come from the request object; store reads tenant from the ambient principal. Two sources of truth. | open |
| W9 | S2 | T1 | `completeFromSystem`, `rejectFromSystem` | Skip outcome and schema validation and accept any non-terminal state. Exposed on the same SPI as the user paths. | open |
| W10 | S3 | T4 | `LedgerEventCapture` | Actor type from `ActorTypeResolver` prefix (P13, L11). | open |
| W11 | S3 | | `WorkItemService` | 997 lines. `complete` and `reject` each exist twice as copy-paste overloads. `io.casehub.work.api.WorkItem` fully qualified throughout. `delegationChain` is a comma-joined string. Timers scheduled inside the transaction before commit. | open |
| W12 | S3 | | `TenantAwareStore` | Tenant set by string concatenation with a quote check; `set_config(?, ?, true)` is safer. RLS DDL applied at startup needs role-creation rights. RLS off by default. | open |
| W13 | S3 | T13 | repo-wide | No tests in `work-support-core`, `progress-rest`, `persistence-spring-mongodb`, `deployment`. | open |

### Carry-over answers

- L1 (actor from principal?): no. Work feeds client-supplied actor ids into the ledger (W1, W4).
- L3 (delimiter-joined `domainContentBytes`): yes, `WorkItemLedgerEntry` joins `commandType|eventType`. Low risk as both are derived constants.
- P12 (ACL backend): work does not call `AccessControlProvider` at all.
- P13: used for ledger actor type only (W10).

### Not yet reviewed

`queues`, `ai`, `issue-tracker`, `flow`, `federation`, `progress-*`, `reports`, `persistence-mongodb-core`, `persistence-memory`, `qhorus` adapter, template and schedule services, CloudEvent inbound adapter, label rule engine (check T5), examples.

### Carry into downstream repos

- Does qhorus also ship its own `LedgerEntryRepository` bean or its own hashing? (W3, W4)
- Any other `CurrentPrincipal` alternatives and their priorities? Platform docs mention `QhorusInboundCurrentPrincipal`. (W6)
- Does engine call `completeFromSystem` / lifecycle ops with an actor it authenticated? (W1, W9)
- Anyone else updating a persisted ledger entry? (W5)

## qhorus

Strengths: honest javadoc on its own security boundary; channel `allowed_writers` policy and rate limiter exist; frontier read `ForUpdate`; tombstone design for message erasure keeps the original digest; 280 runtime tests.

### Findings

| ID | Sev | Theme | Where | Note | Status |
|---|---|---|---|---|---|
| Q1 | S1 | T1,T3 | `TenancyContextFilter`, `QhorusInboundCurrentPrincipal` | Tenant comes from unauthenticated `X-Tenancy-ID` header; actor is always `anonymous`. Documented, but it is the default. Outside a request it silently falls back to the default tenant. | open |
| Q2 | S1 | T15 | `MessageService`, `A2AChannelBackend.receive`, `A2AResource` | Sender is self-declared; `allowed_writers` and rate limits are checked against that string. Actor type comes from caller header `x-qhorus-actor-type`, which also gates pseudonymisation (L11). | open |
| Q3 | S1 | T16 | `MessageLedgerEntry.domainContentBytes` | Pipe-joins free-text `content`, `target`, `topic`, `reasoning` with no escaping. L3 is directly exploitable here since message content is arbitrary. | open |
| Q4 | S2 | T16 | `MessageLedgerEntry` | Persisted but not hashed: `routingOriginalTarget`, `routingSelectedAgent`, `routingStrategy`, `routingCandidateCount`, `correctsMessageId`. | open |
| Q5 | S1 | T19,T20 | `QhorusLedgerEntryRepository` | Third copy of the ledger save pipeline, also a non-default `LedgerEntryRepository` bean. Lacks agent signing and enrichers. With work's bean (W3) on the same classpath, injection of `LedgerEntryRepository` is ambiguous or order-dependent. Confirm how combined apps resolve it. | open |
| Q6 | S2 | T20 | `QhorusSequenceAllocator` | Allocates in `REQUIRES_NEW`, keyed by subject only. A rolled-back outer transaction leaves a gap; ledger `inclusionProof` indexes by `seq - 1` (L8) and breaks. No tenancy in the key. | open |
| Q7 | S2 | | `QhorusLedgerEntryRepository.save` | `synchronized`: single-JVM only (qhorus has a `cluster` module), pins virtual threads, and releases before the transaction commits. 11 `synchronized` uses in runtime/cluster. | open |
| Q8 | S1 | | `MessageContentErasureService` | Nulls `content` and signature on a hashed entry. Ledger `verify` has no tombstone handling, so the channel fails verification permanently after one erasure. `em.find` has no tenant check. Tombstone always written to the default tenant (same as L10). | open |
| Q9 | S2 | T1,T2 | `cluster` `InternalSecretFilter` | If no secret is configured, `/internal/*` is open. Plain `equals` compare. | open |
| Q10 | S3 | T13,T14 | repo-wide | README is badges only. No tests in `runtime-spring`, `connector-backend-core`, `notification-bridge-core`, `websocket-observer-spring`. `runtime-core` (9.6k lines) has 4 test files of its own. | open |

### Carry-over answers

- W3/W4: yes, qhorus ships its own repository bean and its own pipeline copy (Q5). Four write-path implementations now exist: ledger Quarkus, ledger Spring, work, qhorus.
- W6: `QhorusInboundCurrentPrincipal` is a plain `@ApplicationScoped` bean, so OIDC (100) and work's principal (150) both displace it. Precedence across repos: Mock (default) < qhorus (plain bean) < OIDC 100 < work 150 < test fixture 200.
- W5: qhorus also mutates a persisted entry (Q8).
- P13/L11: actor type from caller header (Q2).

### Not yet reviewed

`MessageService` flow, `CommitmentService`, `WatchdogEvaluationService`, `ChannelGateway`/delivery, `LedgerWriteService`, `MessageLedgerEntryRepository`, A2A protocol detail, agent-card signing, compliance-report, slack, push, webhook observer, graphql, cache, mesh.

### Carry into downstream repos

- Which app combines work + qhorus + ledger, and what does it do about the repository beans? (Q5)
- Does engine or claudony rely on `allowed_writers` as a security control? (Q2)

## neocortex

Two passes. Largest repo (123k lines, 89 modules) and the most original.

**What the cognitive side is.** A single-agent cognitive pipeline run as a phased tick (FOUNDATION, SOURCE, DERIVED, TERMINAL): PAD mood with time-based decay toward a baseline; drives (curiosity, competence, affiliation, autonomy); appraisal via Scherer stimulus-evaluation checks mapped to OCC-style emotions and Frijda action tendencies, projected to PAD via the ALMA table; emotion regulation using Gross's process model plus social regulation, chosen by an LLM; a CAPS (Mischel and Shoda) recurrent network settled by spreading activation with oscillation detection and cognitive distortions; BDI extraction for user/mental models; goals, narrative, strategy learning, mood-congruent memory retrieval; a mind-map knowledge graph with confidence origins and decay; Bayesian networks (junction tree) for evidence fusion. Rule-based where theory gives rules, LLM sub-calls where it does not, with keyword fallbacks.

Strengths: explicit tenant ids, filtered in every Qdrant query; APIs use `@ContextParam("tenancyId")`; README explains why; `MoodOrchestrator` uses an injected `Clock` and elapsed-time decay (double ticks are safe); `CapsSettler` is clean and numerically careful; ONNX wrapper closes resources on every failure path; feature flag per subsystem; a cognitive journal and pipeline trace for observability; eval artefacts are checked in.

### Findings

| ID | Sev | Theme | Where | Note | Status |
|---|---|---|---|---|---|
| N7 | S2 | T21 | `mindmap-intelligence` vs `inference-bayes` | 33 classes with identical names under `io.quarkmind.*` in both modules, with different content (`BayesInstance` 390 vs 1,442 lines). `mindmap-intelligence` depends on `inference-bayes`, so both are on the classpath and load order decides which wins. | open |
| N8 | S2 | | `CognitionCore` | Per-tick state in instance fields (`lastAgentId`, `lastTenantId`, `lastDescriptor`, `lastBriefing`, ...) used later for prompt rendering and mind-map lookups, while every method takes `agentId`/`tenantId` and some maps are keyed per agent. If one core serves more than one agent or tenant concurrently, state bleeds across them. Contract is undocumented. Same pattern: `CognitiveMemoryRetriever.setTickContext`. | open |
| N9 | S2 | | `MoodOrchestrator.record` | Appends to a plain `ArrayDeque` with no lock while `tick` drains it under a lock; `currentMood` and timestamps are unsynchronised. Signals can be lost or the deque corrupted. | open |
| N10 | S2 | T17 | cognition orchestrators | Agent state lives in 48 in-process `ConcurrentHashMap`s. Only `UserModelOrchestrator` evicts; only `InnerLifeOrchestrator` restores. Mood, drives, goals reset on restart, are not shared across nodes, and grow without bound. | open |
| N11 | S3 | T16 | state keys | `agentId + ":" + tenantId` in some orchestrators, `agentId + "|" + tenantId` in others. Agent ids contain colons, so keys can collide. `lastMoodDelta` is keyed by agent only. Fallback tenant is the literal `"default"`. | open |
| N12 | S3 | | `CognitionCore` | 1,255 lines; four telescoping constructors (up to 18 parameters) plus about ten setter-injected volatile collaborators; inline fully qualified names; `safeRun` swallows every subsystem failure with one generic warning. | open |
| N13 | S3 | T2 | 8 classes | Hand-rolled JSON extraction (`extractDouble`, `extractJsonString`, first `{` to last `}`) for LLM output, with Jackson already used 68 times elsewhere. A parse miss in `appraiseMood` is silent. | open |
| N14 | S3 | | `EmotionMapper` | Thresholds are inline literals, not in the documented config records. `mapTendencies` has no relevance gate and treats missing novelty (default 0) as low novelty, emitting INTERRUPTION at intensity 1.0. Uses `Instant.now()` rather than a clock. | check |
| N15 | S3 | | `EmotionRegulationGenerationPhase` | Reads `manor.regulation.social.enabled` through static `ConfigProvider` in a constructor: an application's config namespace inside the library, bypassing the config records. | open |
| N16 | S2 | | regulation strategies | `DELIBERATE_PROVOCATION` ("intentionally provoke an emotional response in another person for strategic purposes") and `CO_REGULATION` target other parties, enabled by default. With human counterparts this is emotional influence by design; needs an explicit policy gate, audit entry and default-off for human targets. EU AI Act Art. 5 is relevant given ledger's compliance pitch. | open |
| N17 | S3 | | docs | 146 of 157 cognition source files have no class-level javadoc; the design lives in 171 specs and 30 research notes with 2 ADRs. `architecture-justification.md` covers only RAG/inference and cites secondary blogs. | open |
| N18 | S3 | | evaluation | Evals are LLM-judged scores on pipeline traces. One checked-in case (`cross-tick-drives`) scores 5/5 with empty trajectories. No human-rated or baseline-compared study yet. | open |
| N1 | S2 | T1 | `CorpusApi` | Destructive re-index mutations exposed with no role restriction. | open |
| N2 | S3 | T1 | `TenantGuard.of` | Null principal yields a no-op guard. | open |
| N3 | S3 | T12 | platform `CLAUDE.md` | Still lists memory backends as platform modules. | open |
| N4 | S3 | | naming | `tenantId` (3,590 uses) vs `tenancyId` elsewhere; 221 files under `io.quarkmind.*`. | open |
| N5 | S3 | | `OnnxInferenceModel` | One lock serialises all inference per model. | open |
| N6 | S3 | | scope | Production retrieval and research-grade cognition share one repo and one version. | open |

Checked and cleared: agent sessions are keyed and pooled by the platform `SessionPipeline`, so the 22 `openSession` calls without `close` are not leaks.

### Not yet reviewed

Strategy learning, goal proposal, narrative, user/mental model orchestrators, belief revision internals, mind-map consolidation phases, `CognitiveDerivationEngine` (1,159 lines), CBR algorithms, corpus and knowledge pipeline, memory backends (JPA, SQLite, Mem0, Graphiti) in detail, 48 `synchronized` uses.

### Carry into downstream repos

- How does agency/engine instantiate `CognitionCore`: one per agent, or shared? (N8)
- Is any cognition state persisted by the consumer? (N10)
- Are regulation strategies ever applied to human counterparts? (N16)

## Cross-cutting conclusions (update as repos are added)

1. **Identity is asserted, not authenticated, at every API edge** (L1, L2, W1, Q1, Q2). One fix pattern: actor and tenant from `CurrentPrincipal` only, via `@ContextParam`; request-supplied actor only for a trusted-service role.
2. **The ledger write path has four implementations** (ledger x2, work, qhorus) with different guarantees. Ledger should own one `append` service; consumers should only supply subclass fields.
3. **`CurrentPrincipal` and `LedgerEntryRepository` resolution depends on which jars are present.** Needs one documented precedence table and a composition test in an app that includes everything.
4. **Erasure and retention both mutate or delete hashed data without verification knowing** (L8, L10, W5, Q8). Verification needs a defined model for tombstones and pruned ranges.
5. **Canonical hash input is ambiguous** (L3, Q3). Needs a versioned, length-prefixed encoding before data accumulates.

## Positioning notes

- Differentiators: one-annotation multi-surface exposure; simulation; accountability primitives (confirmation, consent tiers, DID, signing).
- Risk: breadth. Owns authn, sessions, authz, registry, notifications, rate limiting, each against a mature incumbent. Findings cluster there.
- Direction: identity is already delegable via OIDC. Remaining: authz adapter (OpenFGA/SpiceDB), library JWT inside `authn`, declare a small stable core, lead docs with the OIDC path.

- Ledger: the accountability story (Art. 12/22 snapshots, PROV export, pseudonymised erasure, Merkle proofs) is the strongest differentiator seen so far. Closest comparisons are transparency logs (Trillian, Rekor) and ledger databases (immudb, Azure SQL Ledger). Its edge is being embedded and domain-aware; its claim only holds once L1 to L5 are closed.
- Work: competes with the human-task parts of Camunda/Flowable/jBPM (WS-HumanTask lineage) and with Temporal-style "wait for signal". Edge: embedded in the app transaction, agent-or-human assignee, ledger-backed audit. Table stakes still missing: enforcement of who may claim and complete (W1, W2).
- Qhorus: agent-to-agent messaging with commitments, channel governance and ledger-backed transcripts. Neighbours: A2A protocol implementations, AutoGen/CrewAI group chat, Slack-style agent buses. Edge: typed speech acts with commitments and an auditable record. Weak point: participants self-identify (Q2).
- Neocortex retrieval: local ONNX inference + hybrid RAG + CBR on the JVM fills a real gap beside LangChain4j. Solid, conventional, sellable today.
- Neocortex cognition: I know of no other open implementation that combines appraisal theory, a CAPS personality network, Gross-model regulation, drives, BDI user models and mood-congruent retrieval in one running pipeline, on any stack. Nearest relatives: academic cognitive architectures (Soar, ACT-R, CLARION, LIDA), affective-computing engines (ALMA, GAMYGDALA, FAtiMA), and LLM agent work (Generative Agents memory/reflection; MemGPT/Letta, Mem0, Zep on memory only; persona prompting). Those are either pre-LLM and rule-bound, or LLM-native with no psychological model. Bridging the two is the original contribution.
- To make the "ground-breaking" claim hold: (1) evidence beyond LLM self-scoring, i.e. ablations and human ratings against a persona-prompt baseline; (2) durable, per-agent state (N8 to N10), since a mind that resets on restart undercuts the premise; (3) a published safety position on affective influence (N16); (4) separate the stable retrieval modules from the research modules so each can be judged on its own terms; (5) a short paper or technical report, because the audience for this is researchers as much as developers.

## Open questions

- Qhorus: are agents expected to authenticate (agent cards, DIDs) before posting, and where is that enforced?

- Work: is the lifecycle API expected to sit behind a trusted gateway that injects the actor? If not, W1/W2 are the top fix.
- Work: was `TenantScopedPrincipal` priority 150 meant to beat OIDC?

- Ledger: is the append/attest API meant for trusted services only? If so it needs a role, not network trust.
- Ledger: should the erasure receipt hold a hash of the actor id rather than the raw value?

- Is the callback dispatch endpoint meant to sit behind network-level trust only?
- Is MVEL in subscription filters intended for end users or admins only?
- Which modules are considered stable today?
