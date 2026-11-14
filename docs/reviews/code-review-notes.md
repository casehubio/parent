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
- Playbook naming is settled by the owner after research; do not re-raise the Ansible clash.
- Playbook steps are a designed surface (shaped plugins, `@GeneratePlugin` controls), not just generated RPC; connectors has its own `playbooks` module with voice and multi-domain examples.
- Owner regards playbooks as a primary, unique differentiator (powerful, type safe, less code than Java). Reviewed; see platform section. Agreed on power and brevity; type safety and uniqueness are partial.
- Onboarding is in progress and is playbook-led (`platform/playbooks`). Report gaps as "entry point missing", not "no onboarding".
- Identity is delegable via `casehub-platform-oidc` (Quarkus OIDC, so Keycloak works). Built-in `authn` is a deliberate optional path. Authz has no external adapter yet.
- Owner has not yet answered the open questions at the bottom.

**Repo map (one line each, extend as reviewed).**
- **platform** (~98k lines, 241 modules): SPIs + defaults for identity, tenancy, ACL, preferences, notifications, registry, agents/LLM backends, MCP exposure, YAML playbooks, simulation. Pattern: `-core` POJO, Quarkus wiring, generated Spring.
- **ledger** (~23k lines): append-only audit log on platform. `LedgerEntry` JPA JOINED base; consumers subclass (`casehub-work`, `casehub-qhorus`). Merkle frontier per subject, attestations, EigenTrust scores, pseudonymised actors, retention, KMS signers.
- **work** (~40k lines): human/agent task layer. `WorkItemService` lifecycle, stores (JPA, memory, Mongo), optional Postgres RLS via `TenantAwareStore`, timers/expiry, queues, ledger adapter (`ledger/`), qhorus and flow adapters. Read-only clone `/home/user/casehubio/work`.
- **qhorus** (~45k lines): agent/human messaging mesh. Channels, messages, commitments, watchdog, gateway/delivery, A2A endpoint, cluster relay, own ledger repository and `MessageLedgerEntry`. Read-only clone `/home/user/casehubio/qhorus`.
- **neocortex** (~123k lines, 89 modules): AI reasoning layer. ONNX inference, hybrid RAG on Qdrant, CBR, memory backends (moved here from platform), corpus management, mind maps, Bayesian inference, cognition. Read-only clone `/home/user/casehubio/neocortex`.
- **connectors** (~47k lines, 75 modules): outbound `Connector` SPI, inbound webhooks, capability platforms (bank, commerce, travel, calendar, contacts, document, chat, mobile, voice, web) with reference and provider implementations, GraphQL/MCP APIs. Read-only clone `/home/user/casehubio/connectors`.
- **desiredstate**, **ops**, **scaffold**: cloned, not reviewed. Others (work, qhorus, engine, eidos, connectors, ...) not cloned.

**Build order** (from `parent/build/modules-core.csv` dependencies; the file says row order is build order but rows are not topologically sorted, e.g. desiredstate is listed before engine and ras): platform; worker, ledger, connectors, pages; eidos; neocortex, qhorus; work; engine; ras, agency, workers, claudony; desiredstate; ops. Reviewed: platform, ledger, work, qhorus, neocortex, connectors. Not yet: worker, pages, eidos (upstream of engine), then engine. Follow the owner's stated order; check this list before suggesting one.

## Review log

| Repo | Date | Commit | Method | Depth |
|---|---|---|---|---|
| platform | 2026-11-14 | d9805fd | static read, not built | foundations deep, rest sampled |
| ledger | 2026-11-14 | 11018f8 | static read, not built | core deep (hashing, Merkle, save path, signing, erasure, retention, API); trust maths, KMS signers, examples sampled or skipped |
| work | 2026-11-14 | adccdbc | static read, not built | lifecycle service, REST lifecycle API, tenancy/RLS, ledger integration deep; queues, ai, issue-tracker, flow, federation, progress, mongodb not read |
| qhorus | 2026-11-14 | 86adf50 | static read, not built | identity/tenancy, ledger integration, erasure, sender/ACL path, cluster filter deep; message/commitment/watchdog logic, gateway, A2A detail, compliance-report, slack, push, graphql not read |
| neocortex | 2026-11-14 | 4af2ac6 | static read, not built | Five passes (adds inner life, gut feeling, personality evolution, mind-map extractor, DTW, hypothesis tracker; goals, user model, derivation engine, Qdrant CBR store, Mem0/Graphiti keys, zip integrity, knowledge pipeline). Read: strategy learning, belief revision, consolidation scheduler, CBR scorer and JPA store, corpus stores, ingestion, federation walker, plus RAG/Qdrant tenancy, exposed APIs, ONNX wrapper, `CognitionCore`, mood, appraisal (`EmotionMapper`, LLM appraisal), regulation prompt, CAPS settler, memory retriever, Bayes provenance, eval/quality docs, repo-wide greps. Still unread: strategy learning, goals, narrative, user/mental models, belief revision internals, mind-map consolidation phases, `CognitiveDerivationEngine`, CBR algorithms, corpus/knowledge pipeline, memory backends in detail |
| connectors | 2026-11-14 | 83b07fd | static read, not built | core SPI, HTTP helper, webhook router, Slack/Twilio/Gmail inbound, web fetch and images, bank (TrueLayer) payments and consent, confirmation gating, connector GraphQL APIs (identity only), voice provisioner, repo-wide greps. Not read: voice engine internals (11k lines), Discord gateway, chat IRC/Signal/Teams, calendar/contacts/document/travel/commerce providers, email inbound, notification bridge |

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
- **T23 Declared but unenforced control.** A safety annotation or policy type exists but nothing on the classpath turns it into behaviour (C1; compare P16 circuit breaker).
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

### Playbooks (reviewed 2026-11-14 at owner's prompt)

Owner's position: playbooks are an extensive and unique differentiator: very powerful, type safe, less code than Java.

What it is: `yaml-core` meta-language (variables with prefixed sources, `if`, `forEach`, typed CSV data, parameterised modules with outputs) plus a step language in `yaml-step-runtime`: one step = `step-type subject: params`, 13 ordered decorators (`if`, `forEach`, `loop`, `on-error`, `timeout`, `retry`, `semaphore`, `delay`, `signal`, `transform`, ...), structural steps (`block`, `if/then/else`, `match/cases` with guards, `parallel`, `concurrent`, `race`, `try/catch/finally`, `barrier`, `quorum`, `select`), coordination primitives (channel, semaphore, latch, signal, state machine, correlation scope, deadline), invoke bindings (MCP, script, process, agent, REST, GraphQL), agent sessions and pools with structured output. Steps come from `@Plugin` records, MCP tools, scripts with schema files, YAML step definitions, and any `@McpDomain` operation via generated plugins. Tests are themselves playbooks (`.test.yaml`) with simulation.

Assessment:
- **Power: agree.** The coordination vocabulary (quorum, race, barrier, correlation, deadlines, semaphores) and agent sessions as first-class steps go beyond Serverless Workflow, Step Functions, Argo, GitHub Actions and Kestra. Auto-exposing every domain operation and MCP tool as a step is distinctive.
- **Less code than Java: agree for orchestration.** The three-reviewer parallel example is about 20 lines. Step implementations are still Java, which is the right split.
- **Type safe: partly.** Checked before run: step names against the registry, structure, some cross-references; a composed JSON Schema gives editors parameter names, types and enums. Checked at run time: step inputs and outputs against their declarations (`ValidatingAction`), which is stronger than most YAML workflow tools. Not checked: `${...}` expressions and data flow between steps. A `capture` is not typed from the step's declared outputs, so `${result.totl}` fails at run time. Conditions are MVEL/JQ strings. The guide says parameter types are checked at parse time; in the code that check runs at execution. "Schema-checked with runtime contracts" is accurate today; "type safe" needs static data-flow checking, which is achievable because outputs are already declared, and would be a real first among YAML workflow languages.
- **Unique: partly.** Typed-plugin YAML orchestration exists (Kestra is the closest, with traction; also Serverless Workflow, Conductor, Windmill). The unique part is the combination: coordination primitives + agent sessions + domain operations as steps + simulation + tests in the same language.

Findings:

| ID | Sev | Theme | Where | Note | Status |
|---|---|---|---|---|---|
| P21 | S2 | T20 | execution paths | Three: interpreter (`StructuralStepEvaluator` + `DecoratorChain`, about 1,700 lines, what the runner and tests use), compiler to Serverless Workflow (`playbook-compiler`, 1,400 lines, used for validation), durable primitives (`coordination-core`, 1,150 lines, 2 tests). They do not accept the same language. | open |
| P22 | S2 | T14 | `playbooks/` `catalog-parsing-gate.test.yaml` | The gate test expects 3 shipped examples to fail compilation (`modules`, `rest`, `08-structured-output`). Onboarding material includes playbooks one of the paths rejects. Only 4 `.test.yaml` files for 76 examples. | open |
| P23 | S3 | T14 | example playbooks | Two file shapes (header + `---` + bare step list vs top-level `steps:`/`pools:`), mixed `camelCase` and `kebab-case` keys, JSON Schema embedded as a string in YAML. Several example steps are demo-only (`click`, `chan-produce`, `pipeline-consume`). | open |
| P24 | S2 | T12 | `yaml-language-guide.md` "Schema type safety" | Claims parse-time parameter type checks; `Walker` checks names and structure, types are validated in `ValidatingAction` at execution. | open |
| P25 | S2 | | interpreter | No durability: a playbook run does not survive a restart. This is the main axis on which Temporal, Step Functions and Kestra will be compared. | open |
| P26 | S2 | T5 | playbook trust model | `process`, `script`, `rest` and MVEL expressions make a playbook equivalent to code (P2, P7). Fine for developer-authored playbooks; needs a stated policy before tenants or agents author them. | open |

Owner's follow-up: "every API we build is a potential plugin step". Checked 2026-11-14:
- True by design: `graphql-generator` can emit a `@Plugin` record per `@McpDomain` operation. About 600 `@PlatformQuery`/`@PlatformMutation` operations exist across the repos read (work 116, qhorus 137, connectors 134, platform ~100, neocortex 66, ops 29, ledger 22).
- Potential, not yet actual: `-AgeneratePlugins` defaults to false and is switched on in one module (`connectors/graphql`). Three `@GeneratePlugin` uses, all in platform.
- Consequence for typing: operation signatures are Java types, so step inputs and outputs are already known at build time. Static data-flow typing of playbooks can be derived from them rather than hand-declared.

| ID | Sev | Theme | Where | Note | Status |
|---|---|---|---|---|---|
| P27 | S2 | T3 | `GraphQLResolverProcessor` plugin generation | Generated step calls `api.method(args)` and skips `@ContextParam` parameters when building the argument list. Operations that take `@ContextParam("tenancyId")` (work, ledger, neocortex style) would get no tenant, or not compile. Works for connectors because they read identity from the security context. | check |
| P28 | S2 | T9 | generated plugin steps | Steps call the SPI object directly, not the generated REST/GraphQL resource that carries `@RolesAllowed`. Role checks, confirmation and the acting identity of a playbook run are undefined. Every API-edge finding (L1, L2, W1, W2, Q2, N1, C1) becomes reachable in bulk from a playbook. | open |
| P29 | S3 | | `derivePluginName` | Step name is last domain segment + method (`work/lifecycle` gives `lifecycle-claim`). Different domains ending in the same segment collide, and the registry keeps the first silently. | open |
| P30 | S3 | | `GraphQLResolverProcessor` | One 2,969-line class emitting Java with `println`; the Spring generators use JavaPoet. Central to the strategy, hardest file to change safely. | open |

Owner correction (2026-11-14): not "just a step". The step surface is designed, not merely generated. Checked in `connectors/voice-pipeline-steps`, `connectors/playbooks` (8 voice and multi-domain playbooks, each with a `.test.yaml`; missed in the first connectors pass) and `@GeneratePlugin`:
- Shaping tools: scalar shorthand (`tts-synthesise: some text`), verb-subject form (`speaker register:`, `audio join:`), `absorbSiblings` so related keys sit beside the step, routing parameter (`platform: ref`), services injected into `@Execute` by type, binary values passed between steps by reference (`${sample.audio-data}`) where the REST form needs base64, streaming steps for fused pipelines, and `@GeneratePlugin(name, subject, absorb, capability, accessor, optionalParams, exclude)` to tune generated ones.
- Result: playbooks such as the joint-account voice confirmation and dinner booking read like a script of the business flow. Agreed this is a real differentiator: one API signature cannot be ideal for REST, GraphQL, MCP and YAML at once, and the hand-shaped layer resolves that for playbooks.

| ID | Sev | Theme | Where | Note | Status |
|---|---|---|---|---|---|
| P31 | S3 | | shaped plugins, e.g. `SpeakerPlugin` | The pleasant surface costs schema precision: one record with `operation` plus all-optional fields, required-ness enforced by hand at run time (`'name' is required`). The editor schema cannot say that `register` needs `name`. A per-subject variant model would keep both. | open |
| C14 | S2 | | `SpeakerPlugin.extractFromWav` | Assumes a 44-byte header and 16-bit mono 16 kHz PCM. Other sample rates, stereo or extended headers yield a wrong embedding with no error, in code used to gate an authorisation. | open |
| C15 | S2 | | voice playbooks 06/07 | Speaker identification (default threshold 0.8) is shown as the gate for a payment authorisation, with the "speakers" produced by TTS. Synthetic or cloned speech is the known weakness of voice biometrics; present it as one factor, not the authoriser. | open |
| C16 | S3 | | `ConnectorVoiceApi` | Audio travels as base64 in query parameters on the REST form (`audioBase64`), so it hits URL limits and access logs. `VoiceCapability.valueOf(...)` on user input gives a 500. | open |

Naming: owner has researched "playbook" and found it used well beyond Ansible; no better name was found. Decision stands; do not re-raise. (Supporting: the term is already used for agent instructions elsewhere, e.g. Google's conversational agents and Devin.) Only suggestion: always qualify as "CaseHub Playbooks" in docs and search metadata.

If every API is a step, API design is language design: naming, error style (no `"Error: ..."` strings, N31), idempotency (steps get retried), versioning and deprecation all become part of the playbook language contract.

Positioning suggestions: lead with coordination + agents + tests-in-language, not with "YAML workflows"; add static data-flow typing and then claim type safety; pick one execution path as canonical and state durability plans.

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

Five passes. Largest repo (123k lines, 89 modules) and the most original.

**What the cognitive side is.** A single-agent cognitive pipeline run as a phased tick (FOUNDATION, SOURCE, DERIVED, TERMINAL): PAD mood with time-based decay toward a baseline; drives (curiosity, competence, affiliation, autonomy); appraisal via Scherer stimulus-evaluation checks mapped to OCC-style emotions and Frijda action tendencies, projected to PAD via the ALMA table; emotion regulation using Gross's process model plus social regulation, chosen by an LLM; a CAPS (Mischel and Shoda) recurrent network settled by spreading activation with oscillation detection and cognitive distortions; BDI extraction for user/mental models; goals, narrative, strategy learning, mood-congruent memory retrieval; a mind-map knowledge graph with confidence origins and decay; Bayesian networks (junction tree) for evidence fusion. Rule-based where theory gives rules, LLM sub-calls where it does not, with keyword fallbacks.

Strengths: CBR toolkit is unusually complete (weighted local/global similarity with categorical tables, Gaussian/step/exponential decay, range queries, DTW with LB_Keogh for time series, edit distance for sequences, nested structures, MMR diversity, temporal decay, trust weighting, cross-encoder rerank, outcome-driven confidence, supersession) and uses sealed types with exhaustive switches; per-app CBR guides in `docs/cbr`; belief revision supersedes rather than overwrites, keeping provenance; ingestion does not advance its cursor on failure; federated corpus search has tiers and cycle detection; explicit tenant ids, filtered in every Qdrant query; APIs use `@ContextParam("tenancyId")`; README explains why; `MoodOrchestrator` uses an injected `Clock` and elapsed-time decay (double ticks are safe); `CapsSettler` is clean and numerically careful; ONNX wrapper closes resources on every failure path; feature flag per subsystem; a cognitive journal and pipeline trace for observability; eval artefacts are checked in.

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
| N19 | S2 | | cognition orchestrators (pattern) | N9 is systemic: `StrategyLearningOrchestrator.record` also mutates `ArrayDeque`s outside the tick lock and `tick` reads them unlocked. Treat every `record`/`tick` pair as suspect. | open |
| N20 | S2 | | `StrategyLearningOrchestrator` | Reflection runs on a JVM-wide static single-thread executor with an unbounded queue, never shut down. `lastReflectTimestamp` is set only on completion, so each tick during a slow LLM call queues another reflection for the same agent. | open |
| N21 | S3 | | `StrategyLearningOrchestrator`, `CognitionCore` | Reward signal is engagement (`responded`), which `CognitionCore` hard-codes to `true` on the default path, so the rate is uninformative. `engagementTrend` labels a dimension's level, not its change, as IMPROVING/DECLINING. Optimising style for engagement needs a stated position. | open |
| N22 | S2 | | `BeliefRevisionPhase` | One cursor for all agents; it advances even when an agent's revision threw, so that agent's evidence is skipped for good. `contradictionStrength` from the LLM is not clamped. Loads every node of every cognitive subgraph per run and puts all beliefs in one prompt. Only contradiction lowers confidence; nothing raises it. | open |
| N23 | S2 | T5 | belief revision, BDI extraction, strategy guidelines | Persistent prompt injection path: user text becomes an experience, an LLM writes `revisedBelief` / guideline text from it, and that text is stored and later rendered into the agent's own prompt. No trust tier separates user-derived text from instruction-bearing state. | open |
| N24 | S2 | | `ConsolidationScheduler` | `knownTenants` is in-memory and filled only by `consolidateNow`, so nothing consolidates after a restart until re-triggered. Single-JVM lock: each node runs all 26 phases (LLM calls, graph writes) independently. On-demand requests are dropped when busy. Idle check is global, not per tenant. | open |
| N25 | S2 | | `CbrSimilarityScorer` | A queried feature missing from the case is skipped in numerator and denominator, so a sparse case matching 1 of 5 features scores 1.0 and outranks a fuller, slightly imperfect match. Null schema or empty query also score 1.0. Standard practice is missing = 0 or a configurable policy. | open |
| N26 | S2 | T17 | `JpaCbrRecordStore.retrieveSimilar` (and Spring twin) | Loads and deserialises every live case for tenant + domain, scores in Java, then truncates to top-k. Fine for thousands, not beyond; the ceiling is undocumented. With `AllInDomain`, case types lacking a registered schema get score 1.0 (via N25). | open |
| N27 | S3 | | `JpaCbrRecordStore` | `SEMANTIC_ONLY` returns an empty list and `HYBRID` silently degrades to feature-only (INFO log per query) rather than signalling an unsupported capability. `recordOutcome` is an unversioned read-modify-write; concurrent outcomes lose updates. | open |
| N28 | S3 | T18 | CBR stores, scorer | Three near-identical stores (in-memory 579, JPA 542, Spring JPA 502 lines). `scoreDetailed` exists twice, copy-pasted with one extra argument. | open |
| N29 | S2 | | `CorpusIngestionService` | One document that always fails pins the cursor, so every poll re-ingests and re-embeds the whole change set, with no retry cap or dead-letter. MODIFIED is delete-then-ingest, so a failed ingest removes the document from search. `reconcile` ignores failures yet advances the cursor, and saves it under `corpusName` where other paths use `binding.name()`. Locks are per JVM. | open |
| N30 | S2 | | `FlatCorpusStore`, `ZipCorpusStore` `validatePath` | Only rejects blank and `_`-prefixed paths. `rootDir.resolve(path)` accepts `..` and absolute paths. Not reachable from the API paths I traced (entries go through the SQLite entry store), but the store is a public SPI. | open |
| N31 | S2 | | `CorpusApi` / `CorpusApiBean` | Methods declare `@ContextParam("corpusId")`, but the platform dispatcher I read resolves only `tenancyId` and `actorId` and throws on other keys; the bean ignores the parameter and uses a fixed `corpusRef`. Operations return `"Error: ..."` strings instead of failing, so REST callers get 200. No tenancy parameter on this API. | check |
| N32 | S3 | | `CognitiveDerivationEngine` | 1,159 lines, dozens of hard-coded tables mapping personality labels to parameters, not in the cited config. Uses Jungian function codes (`ni`, `te`, `fi`, ...), i.e. MBTI-style typology, alongside Big Five terms elsewhere. Weak empirical footing next to the Scherer/Gross/CAPS parts; reviewers will notice. | open |
| N33 | S3 | | consolidation phases | Ordering by scattered `@Priority` integers, cross-referenced in javadoc. Priorities 12 and 25 are each used twice, so those pairs run in undefined order. | open |
| N34 | S3 | | `GoalProposalOrchestrator` | Three `catch (Exception e) { return List.of(); }` blocks with no logging. `failureSuppressedGoalNames` is in-memory, so abandoned goals are re-proposed after restart. Otherwise well bounded: cap, cooldown, staleness, proposals returned rather than self-applied. | open |
| N35 | S2 | | user/mental models, personality evolution, relationship stage | Builds behavioural profiles and BDI models of people from conversation. Erasure exists per store (`MindMapStore.eraseEntity`, memory/CBR erase) but I found no single operation that erases a subject across memory, CBR, mind map, profiles, Qdrant and in-process state. GDPR profiling duties apply. | open |
| N36 | S2 | T16 | `Mem0CaseMemoryStore`, `GraphitiCaseMemoryStore`, `CbrPointBuilder.pointId` | Tenant isolation in shared backends relies on joined keys (`tenant::entity`, `tenant#caseType#caseId`) with no check that components exclude the separator. | open |
| N37 | S3 | | `QdrantCbrRecordStore` | Dual write to memory store then Qdrant is non-atomic (reconciliation service mitigates). `upsertWithRetry` retries immediately with no backoff. Dense embedding is computed without the null check the sparse path has. Four futures awaited with no timeout. | open |
| N38 | S2 | | `ZipIntegrityChecker` | `ChainManifest` records a `contentHash` per archive, but `check()` verifies only existence, entry counts and metadata agreement. It never recomputes the hash. `ZipFile` handles are not closed. `ChainManifest` reads and writes JSON by hand (480 lines). | open |
| N39 | S3 | T17 | `KnowledgePipelineOrchestrator.search` | On a cache miss, walks every cached query for the tenant and loads each one's entities to test subsumption. Default domain is the literal `"location"`. Query subsumption itself is a good idea. | open |
| N40 | S2 | | cognition journal vs ledger | `CognitiveJournal` has only in-memory implementations, and neocortex has no ledger dependency. Belief revisions, goal proposals, regulation choices, personality transitions and agent-initiated contact are therefore not in the tamper-evident record. This is CaseHub's most distinctive possible combination and it is not wired. | open |
| N41 | S3 | | `InnerLifeOrchestrator` | Agent decides unprompted whether to start a conversation; gated by civility constraints, rate window, novelty and minimum observations (well designed). On LLM or parse failure the drained observation buffer is not restored, unlike the gate paths. Observation text is unbounded between ticks. Uses `synchronized` plus a lock. | open |
| N42 | S3 | | `GutFeelingParticipant` | Fallback path calls `memoryStore.scan` although the constructor allows a retriever with a null store (NPE). The affect scan is tenant-wide with no agent filter, so one agent's gut feeling is derived from every agent's affect memories. | check |
| N43 | S3 | | `PersonalityEvolutionOrchestrator` | Agent type can change (`previousTypeLabel` to `newTypeLabel`, dominant/auxiliary function), with drift ceiling, halt and dampening, and each transition stored as a CBR case. Halt flags are in memory, so a halted agent resumes after restart. Built on the typology in N32. Key order here is `tenancy:agent`, a third variant (N11). | open |
| N44 | S3 | | `MindMapExtractor` | Candidate-term extraction keeps only `[a-zA-Z0-9'-]` and capitalised words, so names with accents or non-Latin scripts are mangled and context lookup misses. Uses `AgentProvider` directly while the rest uses `SessionPipeline`. Otherwise strong: mentions, contradictions, confidence origin, proper JSON parser. | open |
| N45 | S3 | | cognition + mindmap-intelligence (repo-wide habits) | 81 `Instant.now()` calls against 12 classes with an injected `Clock`; 85 `String.format("%.2f")` calls building prompts (decimal comma in some locales); about 22 catch blocks that return an empty default with no log; 23 embedded prompt constants with no versioning or external override. | open |
| N1 | S2 | T1 | `CorpusApi` | Destructive re-index mutations exposed with no role restriction. | open |
| N2 | S3 | T1 | `TenantGuard.of` | Null principal yields a no-op guard. | open |
| N3 | S3 | T12 | platform `CLAUDE.md` | Still lists memory backends as platform modules. | open |
| N4 | S3 | | naming | `tenantId` (3,590 uses) vs `tenancyId` elsewhere; 221 files under `io.quarkmind.*`. | open |
| N5 | S3 | | `OnnxInferenceModel` | One lock serialises all inference per model. | open |
| N6 | S3 | | scope | Production retrieval and research-grade cognition share one repo and one version. | open |

Checked and cleared: agent sessions are keyed and pooled by the platform `SessionPipeline`, so the 22 `openSession` calls without `close` are not leaks.

### Not yet reviewed

Narrative and mental-model internals, social-norm detection, most individual consolidation phases, Qdrant retrieval path and reconciliation, structural chunker, Bayes internals (junction tree, structure learning, causal engine), Spring modules. Checked and fine: memory backends call `MemoryPermissions.assertTenant` consistently; SQLite FTS input is sanitised; DTW (Sakoe-Chiba, Itakura, early abandon) reads correct; `SearchResource` exposes no HTTP annotations of its own.

### Carry into downstream repos

- How does agency/engine instantiate `CognitionCore`: one per agent, or shared? (N8)
- Is any cognition state persisted by the consumer? (N10)
- Are regulation strategies ever applied to human counterparts? (N16)

## connectors

47k lines, 75 modules. Two generations side by side: the original send-only `Connector` SPI (Slack, Teams, Twilio, WhatsApp, email) and a newer family of capability "platforms" (`bank`, `commerce`, `travel`, `calendar`, `contacts`, `document`, `health`, `location`, `project`, `mobile`, `chat`, `voice`, `web`), each as `-spi` / `-ref` / provider modules.

Strengths: webhook module is the best security code seen so far (constant-time compare, 5-minute replay window, proper JSON parsing, 200-on-reject to avoid probing, sanitised security log); Twilio, Slack command and Discord interaction endpoints all verify signatures; connector APIs take the user from the authenticated principal (no T15); `HttpHelper` sets connect and request timeouts; OAuth state is single-use with expiry; payment code uses `BigDecimal` minor units with a precision guard, an idempotency key, a PISP consent check and a hosted bank authorisation page; voice provisioner pins SHA-256 checksums for every native library and model and refuses anything unlisted; only one module without tests.

### Findings

| ID | Sev | Theme | Where | Note | Status |
|---|---|---|---|---|---|
| C1 | S1 | T23 | `@RequiresConfirmation` on `PaymentInitiation.initiatePayment`, `Checkout`, document and contact delete | No connectors POM runs the confirmation generator, and no cloned repo depends on the confirmation module. The generator emits a CDI `@Decorator`, but these capability objects are created with `new` (`new TrueLayerPaymentInitiation(...)`, inner `ShopifyCheckout`), so a decorator cannot intercept them. The gate looks inert. Bank-side authorisation still applies to TrueLayer payments. | open |
| C2 | S1 | | `web` `DefaultWebPlatform.DefaultFetch` | Agent-facing URL fetch with no scheme or host restriction, following redirects: reaches localhost, internal services and cloud metadata. Body is unbounded and returned to the caller. | open |
| C3 | S1 | | `DefaultFetch` | Every stored session cookie is re-added against the target URI (`add(uri, cookie)`), so cookies captured for one site are sent to every site fetched. | open |
| C4 | S1 | T2 | `GmailPushInboundConnector.validateJwt` | Decodes the JWT payload and checks issuer, audience, expiry. The signature is never verified, so the token can be forged. If no audience is configured, validation is skipped entirely. | open |
| C5 | S2 | T3 | `WebhookRequest.tenancyId()` | Tenant read from an `x-tenancy-id` header on the provider's request. Providers do not send it and their signatures do not cover it. Tenant should come from a mapping of the verified payload (Slack `team_id`, Twilio account, mailbox). Gmail messages get a null tenant. | open |
| C6 | S2 | | webhook delivery | No dedupe on provider event id, so replays inside the window and provider retries deliver twice. Handlers run inline before the 200, which invites those retries. Any exception returns 200 and the event is lost. | open |
| C7 | S2 | T3 | `bank-truelayer`, `bank-spi` | No tenancy anywhere; consent and tokens keyed by user id alone. Access and refresh tokens stored in plain columns. Token exchange omits `redirect_uri` although the auth request sends it. Pending OAuth states are in-process and never purged if abandoned. Unknown payment status maps to AUTHORIZATION_REQUIRED. | open |
| C8 | S2 | | `WebImageProcessor` | Downloads every `<img>` on a fetched page and sends each to a vision model. Attacker-controlled HTML sets the count, so cost and time are unbounded (and each download is another C2 request). | open |
| C9 | S2 | T11 | 9 provider clients | No request timeout: TrueLayer client and consent service, Microsoft Graph and Drive, Amadeus, Gmail history and watch, Twilio WhatsApp, Slack command. | open |
| C10 | S3 | T2 | `HttpHelper` | Logs the full URL and response body on failure; Slack and Teams webhook URLs are credentials. `jsonEscape` misses control characters. `send` returns a bare boolean, no retry. Destination URL is not checked against the provider's host. | open |
| C11 | S3 | | `SlackInboundConnector` | Answers the `url_verification` challenge before checking the signature. | open |
| C12 | S3 | T12,T14 | README | Describes five outbound connectors, `io.casehubio` group id, `casehub-connectors-core`, `0.2-SNAPSHOT`. None of the capability platforms, voice or web are mentioned. | open |
| C13 | S3 | T18 | module layout | Four Slack modules (`connectors-api` Slack, `webhook` Slack inbound, `chat-slack`, `slack-bot`) and two Discord ones, with signature code duplicated. Old and new SPI families overlap with no stated migration path. | open |

### Carry-over answers

- T15: clean. T19/T20: none. N31: connectors also use extra `@ContextParam` keys (`httpHeaders`, `queryParams`, `requestUrl`), so the generated REST layer must support more keys than the MCP dispatcher I read; N31 probably affects MCP only.
- P8: connectors' own webhook code does not share platform's weaknesses.

### Not yet reviewed

Voice engine internals, Discord gateway, IRC/Signal/Teams chat, calendar/contacts/document/travel/commerce providers, email inbound, notification bridge, mesh bridge.

### Carry into downstream repos

- Does any app wire the confirmation module, and does it wrap capability objects? (C1)
- Who exposes `web.fetch` to agents, and with what URL policy? (C2, C3)
- How do engine/claudony map inbound provider events to tenants? (C5)

## Cross-cutting conclusions (update as repos are added)

1. **Identity is asserted, not authenticated, at every API edge** (L1, L2, W1, Q1, Q2). One fix pattern: actor and tenant from `CurrentPrincipal` only, via `@ContextParam`; request-supplied actor only for a trusted-service role.
2. **The ledger write path has four implementations** (ledger x2, work, qhorus) with different guarantees. Ledger should own one `append` service; consumers should only supply subclass fields.
3. **`CurrentPrincipal` and `LedgerEntryRepository` resolution depends on which jars are present.** Needs one documented precedence table and a composition test in an app that includes everything.
4. **Erasure and retention both mutate or delete hashed data without verification knowing** (L8, L10, W5, Q8). Verification needs a defined model for tombstones and pruned ranges.
6. **Safety controls exist as types but are not wired** (C1 confirmation, P16 circuit breaker, N40 journal to ledger). Each needs an end-to-end test proving the control fires.
7. **Agent-reachable tools lack an egress policy** (C2, C3, C8; P7 process execution). One shared URL/host policy and budget would cover them.
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
- Neocortex CBR: the Java CBR field is small and mostly academic (jColibri, myCBR, ProCAKE), with little recent activity. A maintained, typed, multi-backend CBR library with time-series and sequence similarity, wired to agent memory, has no obvious current competitor. It is also the most explainable form of agent memory (per-feature similarity breakdown), which suits regulated domains. Fix N25 first: ranking correctness is the product.
- Neocortex corpus: versioned zip corpus with chain manifest, federation and provenance is closer to a knowledge-base product than a RAG helper. Differentiator is integrity and lineage; reliability of ingestion (N29) is what a buyer will test.
- Neocortex autonomy: agents propose their own goals from drives, adapt their style from engagement, revise beliefs, evolve personality and model the people they talk to. Each is bounded in code, but together this is the part of CaseHub with the highest ethical and regulatory exposure and the least external explanation. A short governance document (what is autonomous, what needs approval, what is logged to ledger, how a person is forgotten) would turn a risk into a selling point.
- Neocortex Bayes: `inference-bayes` is a full Bayesian toolkit (junction-tree inference, PC and hill-climbing structure learning, influence diagrams, causal and counterfactual engine, calibration, explanation traces, hypothesis tracking), used for theory of mind. Open Java options are thin (UnBBayes, Jayes; SMILE is commercial; pgmpy is Python). It sits under `io.quarkmind` and would stand as its own library.
- The combination nobody else has: cognition whose every belief change, goal, regulation choice and personality shift is written to a tamper-evident ledger. Both halves exist in CaseHub; they are not connected (N40).
- To make the "ground-breaking" claim hold: (1) evidence beyond LLM self-scoring, i.e. ablations and human ratings against a persona-prompt baseline; (2) durable, per-agent state (N8 to N10), since a mind that resets on restart undercuts the premise; (3) a published safety position on affective influence (N16); (4) separate the stable retrieval modules from the research modules so each can be judged on its own terms, and drop or justify the MBTI-style typology (N32); (5) a short paper or technical report, because the audience for this is researchers as much as developers.
- Connectors: the capability platforms (bank, commerce, travel, calendar, documents, voice) are what let agents act in the world, which is where MCP servers and tool marketplaces (Composio, Zapier, Arcade, Pipedream) compete. CaseHub's angle is typed SPIs with consent tiers, confirmation and simulation built in, plus local voice. That angle only holds if confirmation actually fires (C1) and egress is bounded (C2).

## Open questions

- Connectors: is confirmation meant to be enforced by the calling layer (engine/agency) rather than by decorators?

- Qhorus: are agents expected to authenticate (agent cards, DIDs) before posting, and where is that enforced?

- Work: is the lifecycle API expected to sit behind a trusted gateway that injects the actor? If not, W1/W2 are the top fix.
- Work: was `TenantScopedPrincipal` priority 150 meant to beat OIDC?

- Ledger: is the append/attest API meant for trusted services only? If so it needs a role, not network trust.
- Ledger: should the erasure receipt hold a hash of the actor id rather than the raw value?

- Is the callback dispatch endpoint meant to sit behind network-level trust only?
- Is MVEL in subscription filters intended for end users or admins only?
- Which modules are considered stable today?
