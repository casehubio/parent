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
- Owner (2026-11-15): "the playbook levels is the start of it all coming together"; clarified: **levels = how the examples are structured, to teach and to act as integration tests**. Found in `platform/playbooks`: numbered series `agent-interaction-patterns/01..08` (each "builds on" the previous) with `compilation.test.yaml` + `execution.test.yaml` run by `YamlTestEngine`. Not found under the name "levels" in any cloned repo or in `casehubio/examples` (cloned 99b6d72); may be on an unmerged branch. Measured: 72 example playbooks, 9 referenced by tests (8 numbered + 1 simulation) plus a catalogue parsing gate; 6 of 8 execution assertions are `result.succeeded == true`; tests run through the interpreter runner, not engine (P32). Seams for the levels to cross: three runners (P32, G6, G7), plugin generation off by default (P41), agency YAML separate dialect (A1); desiredstate plugins reuse the platform step runtime (model to follow).
- Owner vision (2026-11-15): an end-to-end system that can build, deploy, run and manage itself; written by LLMs for LLMs; every front-end and back-end operation reachable by an LLM through MCP, or by generating or reusing playbooks, with playbooks + CBR as the learning loop. Hopes a complete stack gains traction. Owner accepts the findings and is confident the gaps can be closed. My view given: the whole-stack thesis is coherent and the loop exists in parts (ops/desiredstate deploy, engine run, ras detect, CBR retain, evolution improve); traction risk is breadth before one closed loop is demonstrable and trustworthy; lead with one loop, one proof.
- Owner hopes CBR is a strong differentiator. Reviewed end to end (neocortex toolkit + engine integration); see engine section. Agreed; weakest link is the no-op Reuse step.
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
- **eidos** (~21k lines): agent identity. `AgentDescriptor`, `AgentRegistry` (JPA/in-memory), vocabularies, capability and disposition health, prompt rendering, org model, eval harness. Read-only clone `/home/user/casehubio/eidos`.
- **engine** (~128k lines, 51 modules): CMMN-style blackboard case engine. Reactor, layered case context, bindings/goals/milestones, workers (function, SWF, playbook, agent, ReAct, A2A, human, sub-case), planning, recovery, routing, stigmergy, evolution; REST/GraphQL/MCP API with `@AclCheck`. Read-only clone `/home/user/casehubio/engine`.
- **agency** (~47k lines, 25 modules): orchestration patterns, org topologies, autonomy budgets and graduation, deliberation, governance, YAML/annotation pattern surfaces, engine adapter, speech. Clone at `/home/user/casehubio/agency`.
- **desiredstate** (~37k lines, 47 modules): generic reconciliation runtime, four authoring surfaces, Terraform/Ansible bridges, org-unit reconciliation. Clone at `/home/user/casehub-desiredstate`.
- **ops** (~20k lines, 11 modules): desiredstate domains (K8s apps, agent topology, infra, compliance, Podman, claudony) plus 9 MCP/REST APIs. Labelled research. Clone at `/home/user/casehub-ops`.
- **scaffold** (2.2k lines): deployable app embedding engine + ops with a web console; package `io.casehub.flow`. Clone at `/home/user/scaffold`. Not cloned: worker, workers, applications. Claudony and ras cloned. Also cloned: `casehubio/examples` (99b6d72), `casehub-pages`, `casehub-mosaic`. Others (work, qhorus, engine, eidos, connectors, ...) not cloned.

**Build order** (from `parent/build/modules-core.csv` dependencies; the file says row order is build order but rows are not topologically sorted, e.g. desiredstate is listed before engine and ras): platform; worker, ledger, connectors, pages; eidos; neocortex, qhorus; work; engine; ras, agency, workers, claudony; desiredstate; ops. Reviewed: platform, ledger, work, qhorus, neocortex, connectors. Reviewed also: eidos, engine (four passes). Remaining repos cloned and unreviewed: desiredstate, ops, scaffold. Not cloned: worker, pages, workers, agency, claudony, ras, and the applications. For engine, first establish which playbook runner and evaluator wiring it uses (P32, P41) and whether it supplies an expression engine (P33). worker and pages still unreviewed. Follow the owner's stated order; check this list before suggesting one.

## Review log

| Repo | Date | Commit | Method | Depth |
|---|---|---|---|---|
| platform | 2026-11-14 | d9805fd | static read, not built | foundations deep, rest sampled |
| ledger | 2026-11-14 | 11018f8 | static read, not built | core deep (hashing, Merkle, save path, signing, erasure, retention, API); trust maths, KMS signers, examples sampled or skipped |
| work | 2026-11-14 | adccdbc | static read, not built | lifecycle service, REST lifecycle API, tenancy/RLS, ledger integration deep; queues, ai, issue-tracker, flow, federation, progress, mongodb not read |
| qhorus | 2026-11-14 | 86adf50 | static read, not built | identity/tenancy, ledger integration, erasure, sender/ACL path, cluster filter deep; message/commitment/watchdog logic, gateway, A2A detail, compliance-report, slack, push, graphql not read |
| neocortex | 2026-11-14 | 4af2ac6 | static read, not built | Five passes (adds inner life, gut feeling, personality evolution, mind-map extractor, DTW, hypothesis tracker; goals, user model, derivation engine, Qdrant CBR store, Mem0/Graphiti keys, zip integrity, knowledge pipeline). Read: strategy learning, belief revision, consolidation scheduler, CBR scorer and JPA store, corpus stores, ingestion, federation walker, plus RAG/Qdrant tenancy, exposed APIs, ONNX wrapper, `CognitionCore`, mood, appraisal (`EmotionMapper`, LLM appraisal), regulation prompt, CAPS settler, memory retriever, Bayes provenance, eval/quality docs, repo-wide greps. Still unread: strategy learning, goals, narrative, user/mental models, belief revision internals, mind-map consolidation phases, `CognitiveDerivationEngine`, CBR algorithms, corpus/knowledge pipeline, memory backends in detail |
| connectors | 2026-11-14 | 83b07fd | static read, not built | core SPI, HTTP helper, webhook router, Slack/Twilio/Gmail inbound, web fetch and images, bank (TrueLayer) payments and consent, confirmation gating, connector GraphQL APIs (identity only), voice provisioner, repo-wide greps. Not read: voice engine internals (11k lines), Discord gateway, chat IRC/Signal/Teams, calendar/contacts/document/travel/commerce providers, email inbound, notification bridge |
| eidos | 2026-11-14 | 5c93420 | static read, not built | JPA registry, query API, render pipeline (structure, prompts, visibility), capability and disposition health, vocab (MBTI sample), in-memory org registry, eval outline, carry-over greps. Not read: `CdiVocabularyRegistry` (679 lines), capability resolver/matching, annotation processors, descriptor YAML preprocessing, eval judges in detail, org annotations |
| engine | 2026-11-14 | 6c28a48 | static read, not built | Four passes (128k lines, 51 modules): spine, CBR, routing/trust + gates + planning + stigmergy + evolution surface, then context/persistence/ReAct/goal formation. Read: README, reactor, case REST API and service, ACL filter and health check, core dispatch handler (rules, budget), instance cache and evaluation serializer, failure-recovery coordinator, worker execution orchestrator (part), playbook integration (`PlaybookWorkerFunctionProvider`, `StepFileCallableDispatcher`), ledger capture wiring, system principal, test bean-exclusion lists, evolution API surface. Not read: planning (HTN/DAG, 10k), stigmergy/swarm, routing and trust, goal formation/revision, CBR retrieval, context layers, milestones, signals, sub-cases, judgment, schedulers, persistence, work adapter, A2A, ReAct, annotations/codegen/generator, Spring modules |
| agency | 2026-11-14 | d76df37 | static read, not built | Two passes: execution driver, structured invoker, engine adapter, topologies (graduated), budgets, governance (vouch, LLM routing, triage), negotiation rules, mediation, YAML and annotation governance surface, default beans. Second: scope enforcement, hierarchical, multi-swarm, pattern compiler, judgment dispatch, speech-ws, prompt optimisation, memory hygiene. |
| desiredstate | 2026-11-15 | e690fdd | static read, not built | One pass: reconciliation loop, plan approval gate, step and parallel executors, Terraform and Ansible bridges, bridge state wiring, eidos org policies. |
| ops | 2026-11-15 | d787b63 | static read, not built | One pass: the 9 API classes, approval authoriser and evaluator, cluster service and K8s client registry, compliance module, LLM trigger evaluator, self-maintenance. |
| scaffold | 2026-11-15 | 131e902 | static read, not built | Quick pass: REST resources, auth config, embedded approval service, app loader, README. |
| pages | 2026-11-15 | 6602b4d | static read, not built | One pass: README, sink scan (innerHTML, unsafeHTML, new Function, postMessage), iframe plugin, backend data/relay/SQL, terminal, dev auth, playbook control resource, panel registry, mosaic dependency shape. |
| mosaic | 2026-11-15 | 13475e1 | static read, not built | One pass: sink scan, markdown renderer, approval gate, work-item-detail actions, GDPR erasure request, fetch/credential usage across components, README. |
| claudony | 2026-11-15 | a47e6ac | static read, not built | One pass: auth mechanism and config, API key service, terminal WebSocket, worker command builder, tmux agent session, MCP tools, role usage. |
| ras | 2026-11-15 | c179222 | static read, not built | One pass: engine, case trigger, trigger claim sequence, feedback tuning strategy and job, feedback state, missed-detection endpoint. |

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
- **T22 Licence files.** Only engine has a `LICENSE` file; none of the other repos checked do; only the parent POM declares Apache 2.0. Neocortex carries 33 ASF-headed files that refer to a NOTICE file.
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
| P21 | S2 | T20 | execution paths | Three: interpreter (`StructuralStepEvaluator` + `DecoratorChain`, about 1,700 lines, what the runner and tests use), compiler to Serverless Workflow (`playbook-compiler`, 1,400 lines, used for validation), durable primitives (`coordination-core`, 1,150 lines, 2 tests). They do not accept the same language. | platform#827 |
| P22 | S2 | T14 | `playbooks/` `catalog-parsing-gate.test.yaml` | The gate test expects 3 shipped examples to fail compilation (`modules`, `rest`, `08-structured-output`). Onboarding material includes playbooks one of the paths rejects. Only 4 `.test.yaml` files for 76 examples. | platform#827 |
| P23 | S3 | T14 | example playbooks | Two file shapes (header + `---` + bare step list vs top-level `steps:`/`pools:`), mixed `camelCase` and `kebab-case` keys, JSON Schema embedded as a string in YAML. Several example steps are demo-only (`click`, `chan-produce`, `pipeline-consume`). | platform#827 |
| P24 | S2 | T12 | `yaml-language-guide.md` "Schema type safety" | Claims parse-time parameter type checks; `Walker` checks names and structure, types are validated in `ValidatingAction` at execution. | platform#827 |
| P25 | S2 | | interpreter | No durability: a playbook run does not survive a restart. This is the main axis on which Temporal, Step Functions and Kestra will be compared. | issue #540 |
| P26 | S2 | T5 | playbook trust model | `process`, `script`, `rest` and MVEL expressions make a playbook equivalent to code (P2, P7). Fine for developer-authored playbooks; needs a stated policy before tenants or agents author them. | platform#827 |

Owner's follow-up: "every API we build is a potential plugin step". Checked 2026-11-14:
- True by design: `graphql-generator` can emit a `@Plugin` record per `@McpDomain` operation. About 600 `@PlatformQuery`/`@PlatformMutation` operations exist across the repos read (work 116, qhorus 137, connectors 134, platform ~100, neocortex 66, ops 29, ledger 22).
- Potential, not yet actual: `-AgeneratePlugins` defaults to false and is switched on in one module (`connectors/graphql`). Three `@GeneratePlugin` uses, all in platform.
- Consequence for typing: operation signatures are Java types, so step inputs and outputs are already known at build time. Static data-flow typing of playbooks can be derived from them rather than hand-declared.

| ID | Sev | Theme | Where | Note | Status |
|---|---|---|---|---|---|
| P27 | S2 | T3 | `GraphQLResolverProcessor` plugin generation | Generated step calls `api.method(args)` and skips `@ContextParam` parameters when building the argument list. Operations that take `@ContextParam("tenancyId")` (work, ledger, neocortex style) would get no tenant, or not compile. Works for connectors because they read identity from the security context. | platform#827 |
| P28 | S2 | T9 | generated plugin steps | Steps call the SPI object directly, not the generated REST/GraphQL resource that carries `@RolesAllowed`. Role checks, confirmation and the acting identity of a playbook run are undefined. Every API-edge finding (L1, L2, W1, W2, Q2, N1, C1) becomes reachable in bulk from a playbook. | parent#548 |
| P29 | S3 | | `derivePluginName` | Step name is last domain segment + method (`work/lifecycle` gives `lifecycle-claim`). Different domains ending in the same segment collide, and the registry keeps the first silently. | platform#827 |
| P30 | S3 | | `GraphQLResolverProcessor` | One 2,969-line class emitting Java with `println`; the Spring generators use JavaPoet. Central to the strategy, hardest file to change safely. | platform#827 |

Owner correction (2026-11-14): not "just a step". The step surface is designed, not merely generated. Checked in `connectors/voice-pipeline-steps`, `connectors/playbooks` (8 voice and multi-domain playbooks, each with a `.test.yaml`; missed in the first connectors pass) and `@GeneratePlugin`:
- Shaping tools: scalar shorthand (`tts-synthesise: some text`), verb-subject form (`speaker register:`, `audio join:`), `absorbSiblings` so related keys sit beside the step, routing parameter (`platform: ref`), services injected into `@Execute` by type, binary values passed between steps by reference (`${sample.audio-data}`) where the REST form needs base64, streaming steps for fused pipelines, and `@GeneratePlugin(name, subject, absorb, capability, accessor, optionalParams, exclude)` to tune generated ones.
- Result: playbooks such as the joint-account voice confirmation and dinner booking read like a script of the business flow. Agreed this is a real differentiator: one API signature cannot be ideal for REST, GraphQL, MCP and YAML at once, and the hand-shaped layer resolves that for playbooks.

| ID | Sev | Theme | Where | Note | Status |
|---|---|---|---|---|---|
| P31 | S3 | | shaped plugins, e.g. `SpeakerPlugin` | The pleasant surface costs schema precision: one record with `operation` plus all-optional fields, required-ness enforced by hand at run time (`'name' is required`). The editor schema cannot say that `register` needs `name`. A per-subject variant model would keep both. | platform#827 |
| C14 | S2 | | `SpeakerPlugin.extractFromWav` | Assumes a 44-byte header and 16-bit mono 16 kHz PCM. Other sample rates, stereo or extended headers yield a wrong embedding with no error, in code used to gate an authorisation. | open |
| C15 | S2 | | voice playbooks 06/07 | Speaker identification (default threshold 0.8) is shown as the gate for a payment authorisation, with the "speakers" produced by TTS. Synthetic or cloned speech is the known weakness of voice biometrics; present it as one factor, not the authoriser. | open |
| C16 | S3 | | `ConnectorVoiceApi` | Audio travels as base64 in query parameters on the REST form (`audioBase64`), so it hits URL limits and access logs. `VoiceCapability.valueOf(...)` on user input gives a 500. | open |

Naming: owner has researched "playbook" and found it used well beyond Ansible; no better name was found. Decision stands; do not re-raise. (Supporting: the term is already used for agent instructions elsewhere, e.g. Google's conversational agents and Devin.) Only suggestion: always qualify as "CaseHub Playbooks" in docs and search metadata.

If every API is a step, API design is language design: naming, error style (no `"Error: ..."` strings, N31), idempotency (steps get retried), versioning and deprecation all become part of the playbook language contract.

Deep pass on the playbook runtime (2026-11-14): read `StructuralStepEvaluator`, `DecoratorChain`, `CatalogStepRunner`, `PluginScanner`, `Walker` (partly), `VariableResolver`, `ConditionEvaluator`, `PlaybookRunnerCore`, `PlaybookCompiler` entry, plugin generation in `GraphQLResolverProcessor`. Not read: `coordination-core` internals, `FusionPass`, state-machine DSL, most of `yaml-test-core`, module expander, APT plugin processor.

What is solid: structural evaluation uses virtual-thread structured concurrency with sealed step types and exhaustive switches; `try/catch/finally` exposes a typed `${error.type/message/step/detail}`; `select`, `race`, parallel with advance-after and cancel-remaining are carefully written; decorators compose as functions; variable errors are helpful (lists available prefixes); a sole `${x.y}` reference keeps its type, interpolation inside text becomes a string; tests exist at unit level for most of this.

| ID | Sev | Theme | Where | Note | Status |
|---|---|---|---|---|---|
| P32 | S1 | T23 | `PlaybookRunnerCore` (in `yaml-test-core`), `YamlTestExecutor` | The only non-test code that builds an evaluator passes no `ExecutionScope` and no expression engine. In that runner `select`, `cancel`, `background`, parallel advance-after, pause/resume, barrier, quorum and `${result.*}` return "requires an ExecutionScope" or do nothing, and any condition that is not a literal boolean throws. Nothing in platform main code creates a root `DefaultExecutionScope`. The production runner lives in a test module; `playbook-runner` is a 66-line wrapper. Check what engine wires. | platform#827 |
| P33 | S1 | T5 | conditions (`when`, `if`, `until`, match guards) | Template-then-evaluate: variables are substituted into the condition text, then the text is evaluated. A value containing expression syntax (LLM output, transcript, webhook field) becomes code; with MVEL that is execution (P2). Also the "Norway problem": a value of `no`, `off`, `n`, `0`, `y`, `on` is read as a boolean. Fix: bind variables as data to a compiled expression. | platform#827 |
| P34 | S2 | T23 | `DecoratorChain.wrapOnError` | `on-error: handler` turns the failure into a success carrying marker keys. Nothing reads `on-error.fallback`; the named handler never runs. | platform#827 |
| P35 | S2 | T23 | `DecoratorChain.wrapTransform` | `transform` is a no-op (returns the result unchanged). | platform#827 |
| P36 | S2 | | `PlaybookRunnerCore` capture | `capture` is honoured only for top-level plugin steps. Captures inside `if/then`, `block`, `parallel`, `try` (used in shipped examples, e.g. parallel agent reviews, voice confirmation) are dropped. Step outputs are also flat-merged into one map, later keys overwriting earlier. | platform#827 |
| P37 | S2 | | `PluginScanner` record path | For `@Plugin` records (the main, generated and shaped path): a missing `@Required` parameter is not rejected and primitives silently default to 0/false; numeric parameters arriving as strings after interpolation throw `ClassCastException`; `float`, enums, nested records and `byte[]` are passed through uncoerced. Input/output validation (`ValidatingAction`) wraps only YAML-defined actions. Required-ness is otherwise enforced only by the editor schema. | platform#827 |
| P38 | S2 | | `DecoratorChain.wrapTimeout` | Runs the step on another thread inside a try-with-resources executor; `close()` waits for the task, so a step that ignores interruption makes the timeout block forever. Timeout wraps retry, so it bounds all attempts together (worth documenting). | platform#827 |
| P39 | S3 | | `DecoratorChain` | `loop: until` stops silently at 1,000 iterations and reports success. `retry` retries every failure by default, including validation errors, and treats an uncategorised failure as retryable. `forEach parallel` and `parallel` have no fail-fast and no concurrency bound. `cancel` clears the thread's interrupt flag in `finally`, which can swallow a real interrupt. `background` discards the result and any error. A skipped guard returns the same empty success as an executed step. | platform#827 |
| P40 | S2 | T12 | `yaml-language-guide.md` vs code | Guide's guard decorator is `if`; code and examples use `when`. Guide examples use bare `${risk}`, `${status}`, `${event}`; the resolver rejects bare references ("use `${var.x}`"). `at`, `from`, `cancel`, `background` decorators are undocumented. `invoke:` escape hatch is documented but `CatalogStepRunner` throws on `InvokeStep`. Shipped `if/else` and `when` examples use literal `true`/`false` only. | platform#827, #544 |
| P41 | S2 | T20 | `PlaybookCompiler` | Its own hard-coded registry of 20 step types with different names from the runtime (`rest-request` vs `rest-call`, `mcp-call`, `graphql-exec`, `process-exec`) and its own syntax rules ("verbose form is removed"). `log` compiles to an empty task. No consumer found in the repos cloned so far. Confirms P21: two dialects. | engine#1322 |
| P42 | S3 | | trust | `VariableSource.env()` and `systemProperty()` exist as sources; if registered, any playbook can read every environment variable. Add to the trust policy in P26. | platform#827 |

Revised assessment after the deep pass:
- **Design and vocabulary: strong, as the owner says.** The language, the shaping tools and the structural evaluator are the real thing.
- **Type safety: weaker than first credited.** On the record-plugin path there is neither parse-time nor run-time enforcement of required parameters or types (P37); enforcement is the editor schema. The earlier "runtime contracts" credit applies to YAML-defined actions only.
- **Delivery gap:** much of the advertised power is implemented and unit-tested in the evaluator but not reachable through the shipped runner (P32), and three documented features do nothing (P34, P35, `invoke:`). The engine review must establish which runner real applications use.
- Priority order: (1) one canonical runner in main code that wires scope and expression engine; (2) fix P33; (3) enforce parameter contracts for record plugins at parse time, which also delivers the type-safety claim; (4) implement or remove `on-error` and `transform`; (5) capture in nested scopes; (6) reconcile guide, examples and compiler.

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
| W1 | S1 | T15 | `WorkItemLifecycleApi`, `DefaultWorkItemLifecycleApi` | `claimant` / `actor` are plain request parameters, not `@ContextParam("actorId")`. No role check. Caller can act as anyone. | work#423 |
| W2 | S1 | | `WorkItemService` | No check that claimant is in `candidateUsers`/`candidateGroups`, and no check that actor is the assignee on `start`, `complete`, `reject`, `delegate`. Only accept/decline delegation check. Exclusion (four-eyes) policy is checked against the caller-supplied id, so W1 bypasses it. | work#423 |
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
| C1 | S1 | T23 | `@RequiresConfirmation` on `PaymentInitiation.initiatePayment`, `Checkout`, document and contact delete | No connectors POM runs the confirmation generator, and no cloned repo depends on the confirmation module. The generator emits a CDI `@Decorator`, but these capability objects are created with `new` (`new TrueLayerPaymentInitiation(...)`, inner `ShopifyCheckout`), so a decorator cannot intercept them. The gate looks inert. Bank-side authorisation still applies to TrueLayer payments. | connectors#256 |
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

## eidos

21k lines. Agent identity: a structured `AgentDescriptor` (slot, capabilities with epistemic domains, disposition, goals, constraints), a registry with vocabulary-aware capability matching, capability and disposition health, system-prompt rendering in three formats, an organisational model, and an evaluation harness.

Strengths: cleanest repo so far on the carry-over themes. Tenant explicit in every SPI and taken from the principal at the API edge; read-only exposed API that filters private goals and constraints; sealed result types (`CapabilityStatus`, `DispositionStatus`, `AgentSelection`); thresholds are per-tenant preferences, not constants; the LLM pass in rendering is confined to disposition and goal narratives, while constraints and objectives are rendered structurally and cached by content hash; A2A card excludes private items; vocabularies are URI-identified with cross-vocabulary equivalence and subsumption (SKOS/XKOS style) and graded capability matching; eval uses structured-output judges; no `CurrentPrincipal` or ledger-repository beans of its own.

### Findings

| ID | Sev | Theme | Where | Note | Status |
|---|---|---|---|---|---|
| E1 | S2 | T22 | `eidos-vocab` | Ships vocabularies named after proprietary instruments: MBTI, DiSC, Belbin, SDI, Enneagram. The MBTI terms use the 16Personalities role names (Architect, Logician, Commander, ...). No trademark notice or disclaimer anywhere in the repo. Legal exposure for a public Apache-licensed project; at minimum rename to neutral terms or add attribution and non-affiliation notices. | open |
| E2 | S3 | | `MbtiTypeTerm`, `JungianFunctionTerm`, disposition evolution | The 0.35/0.20 function weights are cited to "Myers & Briggs (1962)" but are design choices. This is where neocortex's typology (N32, N43) originates. Big Five and SVO vocabularies also exist; defaulting to those would be easier to defend. | open |
| E3 | S2 | | `JpaAgentRegistry.find` | `JOIN FETCH a.capabilities c` combined with a filter on `c` returns descriptors whose capability list contains only the matching rows (standard JPA fetch-join pitfall). Callers then see a truncated descriptor. | check |
| E4 | S3 | T7 | `JpaAgentRegistry.register` | Delete then insert with `em.clear()` in between (detaches the caller's entities); concurrent registers of the same agent race to a unique violation; events fire before commit. | open |
| E5 | S3 | | `EidosAgentApi` | `filterPrivate` removes private goals and constraints but returns `briefing`, `templates`, `providerConfigs` and `extensionData` to any caller in the tenant. No role. `getAgent` returns null (200) for a missing agent. `findAgents` with no parameters lists everything, unpaginated. | check |
| E6 | S3 | | `DefaultDispositionHealth.probe` | Compares normalised effective weights against un-normalised base weights (`effective(aux) >= dominant.weight()`); correct only if the base profile sums to 1. Any non-empty activation history reports `Drifted`, so `Aligned` is effectively "never used". | check |
| E7 | S3 | T3 | `DefaultCapabilityHealth` | `ActorCapacityView.getCapacity(agentId)` has no tenant (platform SPI limitation). | open |
| E8 | S3 | T10 | org model | `InMemoryOrgRegistry` is the only `OrgRegistry` in this repo (desiredstate adds a bridge); org structure is lost on restart unless re-declared. Key is `tenancy:id` (T16). | open |
| E9 | S3 | T12,T14 | README | Seven lines; links to `docs/DESIGN.md`, which does not exist. | open |

### Carry-over answers

- T15, T19, T20: clean. Ledger is used only for compliance attestations and trust scores in agent selection.
- N32/N43 trace back to E2.

### Not yet reviewed

`CdiVocabularyRegistry`, `CapabilityResolver` and match degrees, annotation processors, descriptor YAML preprocessing, template registry, eval judges in detail, org annotations and `OrgStructure` DSL.

### Carry into engine

- Does engine use `AgentSelector` with trust ranking, and whose trust scores (L2 says they are forgeable)?
- Does engine pass `tenancyId` from the principal into `AgentQuery`?

## engine

First pass. 128k lines, 51 modules. A CMMN-style case engine built as a blackboard: a case holds a layered context (semantic, episodic, working), bindings fire workers when context conditions hold, goals and milestones are evaluated against context, and workers can be functions, Serverless Workflow, playbooks, LangChain4j agents, ReAct loops, A2A agents, humans (via work) or sub-cases. On top: a planning layer (HTN/DAG), three-level failure recovery with plan adaptation, trust-weighted agent routing, CBR retrieval of past cases, stigmergy/swarm coordination, and a gated self-improvement loop ("evolution").

Strengths:
- **The API edge is done right, and is the model for the other repos.** `EngineCaseApi` takes tenant via `@ContextParam("tenancyId")`, declares `@AclCheck(resourceType, action, resourceIdParam)` per operation, and the service repeats the check (`requireCaseAccess`) with actor and tenant from `CurrentPrincipal`. Starting a case grants ACLs from the definition's `authorization` block.
- Bindings and goals evaluate expressions with the context as data (JQ by default), not by text substitution; no P33 here.
- Durable by design: event log, scheduler-backed worker execution (Quartz or db-scheduler), input hash per execution, `loadOrRestoreCaseInstance`, event-log replay. This is the durability the playbook interpreter lacks.
- Per-case serialised evaluation with quiescence and signal-settlement tracking; dispatch budgets per case and external.
- Failure recovery classifies TRANSIENT / REASONING / FUNDAMENTAL and escalates from retry, to excluding the agent and patching the local plan (versioned), to goal decomposition, to a triage handler.
- System identity is a qualified bean (`@EngineSystem SystemCurrentPrincipal`), not a priority contest.
- Real README with concepts and a quick start. Has a LICENSE file (the only reviewed repo that does).

### Findings

| ID | Sev | Theme | Where | Note | Status |
|---|---|---|---|---|---|
| G1 | S1 | T17 | `CaseInstanceCache` / `CaseInstanceCacheImpl` | Interface has `put`, `get`, `clear`, `getAll` and no remove. Every case started, with its full context, stays in a `ConcurrentHashMap` for the life of the JVM. | open |
| G2 | S1 | | cache + `CaseEvaluationSerializer` + reactor | Live case state and per-case serialisation are JVM-local. `signal`, `query` and friends throw "Case instance not found" unless the case is in this node's cache. Effectively single-node (or needs sticky routing); I found no clustering statement in the docs. | open |
| G3 | S2 | | `AclEnforcementHealthCheck` | Probes with `canAccess("__probe__", rid, null)` at startup. The in-memory and JPA providers call `action.deniedBy()`, so a real ACL provider would throw NPE during boot. REST tests exclude the real provider and use fakes, which is why it would not show. | check |
| G4 | S2 | T8 | `CaseService.listCases` | Fetches a page, then filters by ACL, so pages come back short; `total` is the filtered page size and `hasMore` is computed from it. One ACL lookup per row. | open |
| G5 | S2 | | `CaseContextChangedEventHandler.evaluateAndDispatch` | Any exception in rule evaluation, dispatch, goals or observations is caught and logged. The case stays RUNNING with nothing scheduled and no fault event. 28 catch-log-continue blocks across the handlers. | open |
| G6 | S1 | T20 | playbooks in engine | Engine runs playbook workers through `new PlaybookCompiler()` (no plugin registry) to Serverless Workflow. Only the compiler's 20 built-in step types are accepted; shaped and generated plugin steps (voice, connectors, any `@McpDomain` operation) fail with "Unknown step type". So the playbooks that run in the test runner and the playbooks engine accepts are different languages (P21, P41). | engine#1322 |
| G7 | S2 | T23 | `yaml-cbr` `StepFileCallableDispatcher` | The bridge that does run plugin steps (`casehub:step-file`) builds a fourth evaluator with no scope and no expression engine (P32), passes step parameters unresolved and `services = null`, treats an unknown action as success, logs step failures and carries on, and runs on the common pool. | platform#827 |
| G8 | S2 | T19 | test `application.properties` across modules | Composition needs long `quarkus.arc.exclude-types` and `selected-alternatives` lists, dummy connector credentials, and comments such as "both are `@DefaultBean`, ARC cannot resolve". Evidence that classpath activation does not compose; every application will need its own list. | open |
| G9 | S2 | T19 | ledger capture | Engine writes case and worker-decision entries through `LedgerEntryRepository.save` (correct, delegates to ledger's pipeline). But engine depends on work and qhorus, whose repository beans compete for that type (W3, Q5). Which one engine's entries go through in a composed app is decided by exclusion lists. | check |
| G10 | S3 | | `rules()` | CBR retrieval runs on every context change. Bindings cut by the dispatch budget are dropped and only reconsidered on the next context change. Plan items for the case are reloaded per evaluation. | open |
| G11 | S3 | T3 | `SystemCurrentPrincipal` | Background identity is `system`, default tenant, cross-tenant admin. | open |
| G12 | S3 | T11 | `A2AClient` | Message send has no request timeout (the agent-card fetch has 5 s). | open |
| G13 | S3 | T18 | `MvelExpressionEngine` | Engine carries its own MVEL engine alongside platform's. | open |
| G14 | S3 | | hygiene | `CaseContextChangedEventHandler` is 1,569 lines with 40 collaborators; `RuntimeBeans` 1,427; 489 inline fully qualified `io.casehub` names; 38 `synchronized`. No tests in the Spring modules. | open |

### CBR across CaseHub (reviewed 2026-11-14 at owner's prompt)

Owner's position: CBR is hoped to be a strong differentiator.

How it fits together: neocortex supplies the toolkit (schemas, similarity, stores, decay, diversity, rerank, outcome-driven confidence). Engine wires it into execution through a per-definition `CbrConfig` (features extracted from case context by JQ or lambda, weights, top-k, minimum similarity, scope and temporal decay, cross-type, retrieval timing):
- **Retrieve:** automatically on case start or on each context change (`CbrRetrievalService`), bounded per-case cache.
- **Reuse:** retrieved plan traces go through `CbrPlanAdapter` and an ensemble analyser, then flow as `RetrievedExperience` into agent routing (`ExperienceSignalProvider`: per-worker success rate on similar cases, with a reason string), human-task routing (`CbrHumanTaskRoutingStrategy`), implementation routing, judgment, the worker's own context (agents see what worked before), plan execution, playbook selection, and the case context (`cbrEnsemble`).
- **Revise:** outcomes adjust stored case confidence with a learning rate; supersession.
- **Retain:** `CbrCaseRetainObserver` at case close builds a plan trace from plan items (binding, capability, worker, outcome) plus features, outcome label and the producing agent's trust score.
Also used in desiredstate (fault policy, situation recompiler) and neocortex cognition (strategy evidence, personality transitions).

Assessment: **agree this is a differentiator, and the integration is the differentiating part.** I know of no workflow engine, case-management product or agent framework with case-based planning in the execution loop. Agent-memory products (Letta, Mem0, Zep) and research systems (Reflexion, ExpeL, Voyager's skill library) store experience as text or embeddings; this stores structured, typed cases with plan traces and returns a per-feature similarity breakdown and a stated reason for each routing nudge. "The system improves with every closed case and can show why it chose this worker" is a claim regulated buyers can use.

What weakens the claim today:

| ID | Sev | Theme | Where | Note | Status |
|---|---|---|---|---|---|
| G15 | S2 | T23 | `CbrPlanAdapter`, ensemble analyser | The Reuse step has no real implementation in the repos read: defaults are `NoOpCbrPlanAdapter` and `NoOpCbrPlanEnsembleAnalyzer`; the only others are tracking decorators. Adaptation is the hard part of CBR and is left to each application. A fallback outcome-vote consensus exists. | open |
| G16 | S3 | | `GoalAwarePlaybookSelector` | Score per goal is `similarity x quality x horizonWeight`; the goal's content never enters, so every candidate gets the same multiplier and ranking is by similarity x quality. "Goal-aware" is nominal. `MindMapGoalDistanceCalculator` exists and looks like the missing input. | check |
| G17 | S2 | | ranking inputs | Engine inherits N25 (a sparse case matching one feature scores 1.0) and N26 (JPA store scores every live case in Java, here potentially on every context change). Retain skips features that fail to evaluate, which produces exactly the sparse cases N25 over-ranks. | open |
| G18 | S2 | | trust in CBR | Retain stamps each case with the producing agent's trust score and stores can weight by trust; trust scores are movable through the ledger attestation API (L2). | open |
| G19 | S3 | | `CbrCaseRetainObserver` | Every closed case is retained with entity id `case-retain`; no deduplication or case-base maintenance beyond age and trust purgers; problem text and features can carry personal data with no per-person erasure path (N35). Producer is "first successful worker". | open |
| G20 | S3 | | evidence | No measurement that CBR improves outcomes (routing accuracy, time to resolution, success rate with and without). Examples exist (`cbr-ensemble-*`). | open |

To make it a headline: (1) ship one real adapter and ensemble analyser (even simple substitution and majority-vote on steps) so the default is not a no-op; (2) fix N25 and add a minimum-support rule for success rates from small k; (3) publish a with/without-CBR comparison on one domain; (4) add a per-decision explanation view ("chosen because 4 of 5 similar cases succeeded with this worker") since explainability is the edge over embedding memory; (5) define case-base maintenance and erasure.

### Engine second pass (2026-11-14): routing and trust, action gates, work adapter, planning, stigmergy, evolution

What these are:
- **Routing:** composable signal providers (trust, experience/CBR, goal, personality, workload) feed agent, human-task and implementation routing. Trust uses a maturity model per capability: BOOTSTRAP (too few observations), QUALIFIED, BORDERLINE (within a margin of the threshold), EXCLUDED; "all borderline" escalates to human oversight; quality floors per dimension; fallback binding.
- **Action gates:** a chained `ActionRiskClassifier` returns `Autonomous` or `GateRequired(reason, reversible, candidateGroups, expiresIn, scope, quorum)` for a planned action; most restrictive wins; a classifier error fails safe to `GateRequired`. A gate becomes a WorkItem (multi-instance when a quorum is set) and the case waits.
- **Planning:** GOAP planner over capabilities with preconditions and effects producing a dependency DAG, with CBR contingencies attached; LLM decomposition; adaptive strategy; replanning that blacklists the failed action; deeper decomposition and forward-replan revision.
- **Stigmergy:** swarm coordination through shared state, with detection of signal consensus, coordination storms and interest convergence, team and role tracking, budgeted swarm provisioning, eviction per case.
- **Evolution:** a gated self-improvement loop, including a `code-evolution` domain: research, hypotheses, improvement cases, stage gates through a conductor inbox, budget enforcer, circuit breaker, regression evaluation by health-score delta, rollback policy, and a structural deny list that stops it modifying its own safety machinery.

Assessment: this is the most ambitious layer in CaseHub and the code read is careful (sealed decisions, fail-safe gate on classifier error, explicit budgets and deny lists). Risk-classified action gates with quorum approval are a better human-in-the-loop design than anything in the agent frameworks I know.

| ID | Sev | Theme | Where | Note | Status |
|---|---|---|---|---|---|
| G21 | S2 | T23 | action gates vs platform confirmation | Engine's `ActionRiskClassifier`/`ActionGate` and platform's `@RequiresConfirmation`/`OperationConfirmationProvider` (used by connectors for payments, checkout, deletes) are unconnected; engine references neither. C1 stays open: nothing turns a connector's confirmation annotation into an engine gate. Natural fix: a risk classifier that reads the step's confirmation/consent tier, and a confirmation provider backed by action gates. | parent#548 |
| G22 | S2 | T1 | `ChainedActionRiskClassifier` | With no classifiers registered the decision is `Autonomous`. Fail-safe applies to errors, not to absence. | open |
| G23 | S2 | | `TrustWeightedImplementationRoutingStrategy.score` | A BOOTSTRAP candidate scores its workload score (1.0 when idle); a QUALIFIED one scores `trust x 0.6 + workload x 0.4`, below 1.0 unless trust is perfect. An unknown idle agent outranks a proven one, and a fresh identity resets to BOOTSTRAP (whitewashing). `bootstrapEscalationRequired` defaults to false. | check |
| G24 | S3 | | `TrustRoutingPolicy.isBorderline` | Symmetric band: with defaults a score of 0.70 to 0.80 is "borderline" and excluded, so the effective bar is above 0.80. Worth stating in docs. | open |
| G25 | S2 | T1 | `GatePolicy.effectiveMode` | A stage with no configured mode defaults to `AUTO`. For a loop that can propose code changes the safe default is `GATED`. | open |
| G26 | S3 | | `CodeEvolutionDenyPatternProvider` | Protection of the safety machinery is a deny list of 28 name fragments. New or renamed safety classes are unprotected until added; an allow list of modifiable areas is the stronger shape. | open |
| G27 | S3 | | `GoapDecompositionStrategy` | Five distinct failure causes throw the same message ("GOAP decomposition produced no plan"). "Open world" state sets every unknown precondition to false. | open |
| G28 | S3 | | work adapter | Engine creates WorkItems as `createdBy("casehub-engine")` with tenant from the request; completion flows back through work's lifecycle, so W1/W2 (anyone can complete as anyone) apply to gate approvals and human tasks. | open |

Carry-over update: L2 (movable trust scores) now has three consumers: routing (G23), attestation gating, and CBR retain (G18).

### Engine third pass (2026-11-14): context layers, goal formation, milestones, persistence, ReAct

Read: `WritableLayerImpl` (part), `GoalFormationEvaluator`, `MilestoneSLAOrchestrator`, `JpaCaseInstanceRepository` (save, find, update), `ReActWorkerFunctionHandler`. Checked for `@Version` across persistence.

Good: context layers use read/write locks, versions and freezing; state change and event-log append happen in one transaction; milestone status is derived from the event log; SLA and worker paths fall back to the repository on a cache miss; ReAct has an explicit tool list per worker (other workers or local functions), a cycle bound, and emits each cycle (reasoning, tool calls, token usage) as an event; engine goal formation is opt-in, capped (max goals, max per reflection, cooldown) and has an `autoApprove` switch.

| ID | Sev | Theme | Where | Note | Status |
|---|---|---|---|---|---|
| G29 | S2 | T7 | engine persistence | No `@Version` on any entity in `persistence-jpa-common`/`persistence-hibernate`. `updateStateAndAppendEvent` loads the row and overwrites state and the full context snapshot. `CaseInstance.version` exists but is not used as a lock. Two writers to one case silently lose an update; compounds G2. The whole context is rewritten on each state change. | open |
| G30 | S2 | | cache fallback inconsistency | `MilestoneSLAOrchestrator` and worker execution restore a case from the repository when it is not cached; `CaseHubReactor.signal/query` and `DefaultRecoveryCoordinator.handleFailure` do not (throw, or return false). After a restart, which operations work depends on the path. | open |
| G31 | S2 | | ReAct tools vs action gates | A ReAct tool that wraps another worker calls `runtime.execute(workerName, args)` directly inside the loop. I did not find the risk classifier on that path, so an action that would be gated when dispatched by a binding may run ungated when an agent calls it as a tool. | check |
| G32 | S3 | | `ReActWorkerFunctionHandler` | All tool parameters are declared as strings, losing the capability's types. The only budget is `maxCycles`; no token or cost ceiling per loop. | open |
| G33 | S3 | | `GoalFormationEvaluator` | With `autoApprove` off, a proposal is written to the event log and nothing else: no WorkItem or gate asks a human to approve it, so proposals are either automatic or inert. `lastFormationTime` grows per agent and tenant with no eviction. | open |
| G34 | S3 | | `WritableLayerImpl.get` | Returns live nested maps and lists; a caller can mutate them without the lock or a version bump. | open |

Engine review status: spine, CBR, routing/trust, gates, work adapter, planning (GOAP), stigmergy (surface), evolution (surface), context, persistence, ReAct read. Still unread: goal revision and abandonment, signals and sub-cases in detail, judgment, schedulers, A2A handler, annotations/codegen/generator (about 9k lines), Spring modules, examples.

### Carry-over answers

- **P32/P33/P41 (which playbook runner):** engine uses the compiler path for workers and a degraded interpreter for step files (G6, G7). Neither wires an execution scope. Engine's own conditions are safe (data-bound JQ).
- **T15:** clean at the engine API. Worker and agent identities inside a case are definition-supplied.
- **E-carry (trust ranking):** engine has trust-weighted routing (`TrustScoreAgentTrustProvider`, `TrustWeightedImplementationRoutingStrategy`, `EngineAwareAgentSelector`). Not yet read; L2 (forgeable attestations) feeds it.
- **P12:** engine is the first consumer that enforces ACLs; with the default no-op provider it logs "permissive".
- **W1/W9:** work adapter not yet read.

### Not yet reviewed

See the status line at the end of the third pass above.

## agency

First pass (owner: "the most important layer, bringing agentic AI to the org"). ~47k main lines, 25 modules, commit d76df37. `agency-core` (24.6k) holds orchestration (ExecutionModel = routing + activation + aggregation + judgment + termination; patterns supervisor/debate/loop/parallel/voting/conditional/sequence/HTN; topologies centralised/hierarchical/hive/hybrid/graduated/distributed; multi-swarm with conflict mediation; autonomy budgets; degradation), deliberation (conversation and negotiation protocols, judgment, coalition formation), governance (trust and CBR routing, vouching, attestation intents, LLM triage), perception, social memory hygiene, prompt optimisation. `agentic-yaml` (4k) declares patterns in YAML; `annotations` is the Java peer; `engine-adapter*` runs patterns as engine workers with checkpoint/resume; `speech-*` (12k) is voice; `summarisation-*`.

Strengths:
- Best code quality of the reviewed repos: small classes (largest 431 lines), sealed result types everywhere (`InvocationResult`, `RiskDecision`, `BudgetGrant`, `TriageDecision`, `MediationResult`), constructor-injected POJOs, policies composed not inherited.
- `ExecutionModel` is the right abstraction: every named pattern is a choice of five policies, so a new pattern is configuration. Cleaner than CrewAI/AutoGen/LangGraph, where patterns are separate code paths.
- LLM is consistently advisory inside a deterministic envelope: trust filter first, LLM chooses among eligible, choice validated against the eligible set, fallback to classifier (`LlmAgentRoutingStrategy`); triage and mediation fail closed to Abandon on parse or agent error.
- One correct structured-output helper (`StructuredAgentInvoker`: string-aware JSON extraction, typed errors, cost metadata).
- Patterns run inside durable engine cases with checkpoint and resume (`PatternWorkerFunctionHandler`, `CheckpointingListener`, `ResumableDriver`), with timeout and cancel. This is what the agent frameworks lack.
- Autonomy is a budgeted, graduated quantity (`AutonomyBudgetPool` with reserve fraction, `DecisionScope` STIMULUS_DRIVEN -> TASK_ADAPTATION -> FULL_AUTONOMY, cascade to lowest scope on degradation). The concept is the differentiator for "agents in an org".
- Tests: 33.6k lines in `agency/` exercise core; engine-adapter has checkpoint and resume integration tests (earlier note of "0 tests" for engine-adapter-core was wrong: its tests live in `engine-adapter`).
- `docs/yaml-coverage.md` is an honest living matrix of what is YAML-expressible.

### Findings

| ID | Sev | Theme | Where | Note | Status |
|---|---|---|---|---|---|
| A1 | S1 | T-declared-unenforced | `agentic-yaml` `GovernanceSpec`, `PatternDefinition.governance()`; `annotations` `@OversightGate/@TrustRouted/@CbrRouted/@Attestation` | Governance on a pattern is parsed and validated but nothing reads it. No main code calls `.governance()`; the pattern compiler ignores it. A YAML author who writes `governance: oversight: ... candidateGroups: [senior-reviewers]` gets no gate, no trust routing, no attestation. Coverage doc marks these "Done" (its "Done" = spec + tests). | agency#476 |
| A2 | S1 | same | `annotations/deployment` | `AgencyAnnotationsProcessor` has one `@BuildStep` (feature name). `PatternAnnotationStep`, `GovernanceAnnotationStep`, `CustomizeAnnotationStep` are plain classes never invoked from a build step. The whole annotation surface (`@Supervisor`, `@Debate`, ..., governance) is inert in an application. | agency#476 |
| A3 | S2 | autonomy | `GraduationState`, `GraduatedTopology.executeGraduated`, `HybridTopology`, `CentralisedTopology` | Autonomy is earned by not being scope-gated, not by outcome quality. Every non-`ScopeGated` outcome is `SUCCESS`; `FeedbackSignal.FAILURE` is never emitted in main code. Once the window is 80% success each further feedback upgrades a level, so `windowSize + 1` decisions reach FULL_AUTONOMY. No link to ledger trust scores, judgments or case outcomes. | open |
| A4 | S2 | autonomy | `GraduationState` | `scopeFloor` acts as a ceiling, is one field for all agents, and is never cleared: after a cascade no agent can be promoted again for the life of the object. Signal lists grow without bound (`CopyOnWriteArrayList`, window read by `subList`). State is in memory only: earned autonomy resets on restart, and is not written to the ledger. | open |
| A5 | S2 | T1/Q2 | `deliberation/*/protocol/*Rules`, qhorus `SuggestedAction` | Protocol violations (non-participant sender, proposer accepting own proposal, round limit) produce `DispatchAdvisory` with LOG/ESCALATE/INVESTIGATE/REROUTE; nothing rejects the message. Combined with self-declared senders in qhorus (Q2), a negotiation or coalition outcome can be decided by a party not in it. | open |
| A6 | S2 | T-fail-open | `AgencyBeans` | `NoOpAttestationIntentWriter` is the default: vouches and lifecycle attestations are silently dropped unless a writer is supplied. Also NoOp reflection stores, semantic integrity checker, thread summary store. No startup warning seen. | open |
| A7 | S2 | robustness | `AbstractExecutionDriver` | Per-execution state in instance fields; agents dispatched sequentially even for parallel/voting; `await().indefinitely()` per agent (bounded only when run through the engine adapter's timeout); listener exceptions not isolated. | open |
| A8 | S3 | budget | `AutonomyBudgetPool` and callers | All three direct callers (`SwarmRoutingStrategy`, `CollectiveReasoningAggregation`, `SwarmProvisioningAdvisorImpl`) acquire with `RESERVED`, so the reserve fraction never constrains them. Tokens are recorded after the call, so the limit is exceeded by one call's worth; check-then-act on tokens. Pool is per topology instance, in memory, not per tenant or per org unit. | open |
| A9 | S3 | T2 | `agentic-yaml` `CallerConfigRegistry` and registries | YAML guards and title/scope expressions use MVEL (P2, unsandboxed). Fine for classpath YAML; a risk the moment patterns are tenant-authored. | open |
| A10 | S3 | prompt | `LlmAgentRoutingStrategy`, `LlmConflictMediator`, `LlmTriageHandler` | Case context, beliefs and failure detail are appended to prompts unbounded and undelimited. Agent-authored text reaches the mediator and triage prompts (N23 class). Output validation limits the damage for routing; mediation `updatedConclusion` is free text. | open |
| A11 | S3 | layering | `StructuredAgentInvoker` | Lives above neocortex, which hand-rolls JSON parsing; does not use platform `ResponseFormat`. Belongs in platform agent-api. | open |
| A12 | S3 | docs | `README.md`, repo root | README is 35 lines ("reusable building blocks") for the layer the owner calls most important; no end-to-end example of an org unit with agents, oversight and budget. No LICENSE (T22). | open |
| A13 | S3 | concurrency | `GraduatedTopology` | `configure()` assigns `cascadeThreshold` and `loopPriorities` instance fields; a topology instance shared across cases is overwritten by the last `configure`. | open |

### Agency second pass (2026-11-14): scope enforcement, hierarchy, multi-swarm, YAML compiler, judgment, speech, prompt optimisation, memory hygiene

| ID | Sev | Theme | Where | Note | Status |
|---|---|---|---|---|---|
| A14 | S1 | T-declared-unenforced | engine `DecisionScope.isPermitted`, `AgentCapabilityGuard`, agency `DecisionOutcome.ScopeGated` | **Decision scope is never enforced.** `isPermitted(DecisionType)` has no caller in engine or agency main code; the only `AgentCapabilityGuard` is `NoOpAgentCapabilityGuard` (always Permitted) and nothing calls `check`; `ScopeGated` is never constructed. Scope reaches telemetry and prompt context only. So A3's `SCOPE_VIOLATION` can never occur: every agent in a graduated topology climbs to FULL_AUTONOMY, and FULL_AUTONOMY means nothing different at runtime. Supersedes A3 as the core issue. | open |
| A15 | S2 | human-in-loop | `PatternCompiler.resolveJudgment`, `DirectJudgmentDispatcher`, `EngineAgentInvoker` | YAML judgment always gets `NoOpVerifier` + `DirectJudgmentDispatcher`, which throws `IllegalArgumentException` for a human caller (null `agentRef`) and awaits agents indefinitely. `EngineAgentInvoker`: "HumanAgent not supported in v1". `CallerConfigSpec.Human` (candidate groups, quorum, deadline) is parsed in full. Humans join only at engine binding level, not inside a pattern. | open |
| A16 | S2 | budget | `PatternCompiler` swarm branch | Creates one `AutonomyBudgetPool("swarm-yaml")` at compile time. The pool has no reset, so the budget is shared by every execution and every tenant of that pattern for the life of the process; once spent, the pattern is denied until restart. Topology pools are per case (correct). | open |
| A17 | S2 | T1 | `speech-ws` `SpeechWebSocket` (`/ws/avatar`) | No authentication annotation or principal use. Agent and tenant come from static config. Client chooses `llmModel` per message; `SpeakerIdentify(name)` lets the client assert who is speaking, which keys the cognition user model. History list unbounded and shared with the proactive thread without synchronisation; proactive tick swallows all exceptions. Fine as a demo, not as a deployed surface. | open |
| A18 | S2 | belief | `MultiSwarmTopology.processL2Finding`, `applyResult` | Belief entrenchment = the source swarm's self-reported confidence x 100, so a swarm that reports 1.0 displaces other swarms' conclusions under AGM revision. Mediated results are added with `expand` (no consistency check). `pendingNotifications` feeds `conflictLevel` and is not obviously drained. | open |
| A19 | S3 | robustness | `HierarchicalTopology.computeDepth` | Follows `parentMap` with no cycle guard: a cyclic org chart loops forever in `configure`. Same mutable-field issue as A13. All topology executors only map outcome to feedback; they do not execute anything. | open |
| A20 | S3 | memory | `MemoryHygieneOrchestrator.doTick` | Fetches the top `consolidationBatchSize` records for the tenant, then filters by agent in memory: in a busy tenant an agent's memories may never be in the batch. Eviction is a hard `erase` reported only to an event sink (not ledger); missing trust score defaults to 1.0. Field named `RetentionConfig`. | open |
| A21 | S3 | tenancy | `PromptVariantStore`, `InMemoryPromptVariantStore` | Variants keyed by (signature, slot), no tenant: an instruction learned from one tenant's outcomes is appended to every tenant's system prompt. In-memory default, so learned prompts vanish on restart. Good: the meta-prompt contains only outcome counts, no case content; proposals go through engine's evolution loop. | open |
| A22 | S3 | structure | `agentic-yaml` | Directory `io/casehub/agency/agentic/yaml` holds package `io.casehub.agency.core.yaml`. `PatternCompiler` uses fully qualified names throughout and unchecked casts to `ExecutionModel<T>`. `AgencySpecsResource` (`/api/agency/specs`) is unauthenticated (read-only catalogue). | open |

Pattern across A1, A2, A14, A15: agency's control vocabulary (oversight, scope, human judgment, governance annotations) is fully modelled and tested as data, and the last step that makes it bite is missing each time. Orchestration itself (ExecutionModel, patterns, checkpointing, routing) is wired and works.

Status after second pass: still unread are hive/distributed internals, BJT networks, conversation projections, perception renderers, speech-sherpa, summarisation, Spring modules.

### Carry-over answers
- G21/C1 (who enforces confirmation and gates): not agency today. Agency declares oversight (A1, A2) but enforcement still rests on engine's `ActionRiskClassifier` path only.
- L2 (movable trust): vouching adds another writer of ENDORSED attestations; gated by `VouchEligibility`, dropped by default (A6).
- Tenancy: `tenancyId` passed explicitly in coalition, attestation, social memory; absent from budgets and graduation state.

### Not yet reviewed
Hierarchical/hive/distributed topology internals, multi-swarm bus and BJT escalation networks, pattern compiler detail, conversation projections, perception (rag, narrative), prompt optimiser internals, social memory hygiene scoring, speech (sherpa, ws), summarisation, Spring modules.

## desiredstate

First pass, commit e690fdd. ~37k main lines, 47 modules. Generic desired-state runtime: goal compiler -> immutable graph -> diff against actual -> four-phase plan (remove, suspend, resume, add; BFS layers) -> executor (simple, parallel, or case-backed via engine) -> fault and drift policy -> CloudEvents. Surfaces: annotations, YAML, TypeScript DSL, YAML plugins. Bridges: Terraform (go-plugin gRPC, no Terraform CLI) and Ansible. `eidos/` module reconciles organisational units. No REST/MCP surface of its own (library; ops exposes it).

Strengths:
- Clean, well-named domain model: sealed results everywhere (`ProvisionResult`, `StepOutcome`, `DriftDecision`, `GateDecision`, `RevertCondition`), immutable graph with CAS updates, pruning before growing, explicit lifecycle state machine.
- Four authoring surfaces compile to one `GraphDescriptor`; build-time validation in the Quarkus extensions.
- Fault handling is a real design: threshold tiers with pluggable count store, review nodes as graph mutations, CBR retrieve/adapt for faults and situations, outcome tracking.
- Terraform bridge speaks the provider protocol directly (v5/v6, mTLS, cty msgpack) with SHA-256 and GPG verification and a zip-slip guard. Rare in Java and a real asset.
- **Org autonomy is enforced here** (unlike agency's `DecisionScope`, A14): `selfDetermination` drives human gating (<0.3), plan approval, bottom-up proposals (>=0.5), topology change (>0.7) and drift exemption.
- Tests are substantial (runtime 10k lines, yaml 3.3k, terraform 2.8k); TCK contract tests for bridge providers.
- OTel spans throughout.

### Findings

| ID | Sev | Theme | Where | Note | Status |
|---|---|---|---|---|---|
| D1 | S1 | T-declared-unenforced | `ReconciliationLoop.TenantLoop.reconcileTypes` | The per-type resync path plans and executes with no reference to `approvalGate`. It is the default periodic path when a router is present and no resync override is set. A plan awaiting human approval (or rejected) is executed by the next type resync. | open |
| D2 | S1 | state | `BridgeRecorder`, `BridgeDiscovery`, `NoOpBridgeOutputStateStore` | Both wiring paths build `BridgeProvisioner` and `BridgeActualStateAdapter` with the two-arg constructor, i.e. the no-op state store. For Terraform, `read` with empty prior state returns nothing -> NotFound -> ABSENT -> provision (create) -> output state discarded. As wired, each cycle would create the resource again. The only real store is in-memory and is never wired. Not run; verify with a real provider. | open |
| D3 | S1 | concurrency | `ReconciliationLoop.TenantLoop` | Nothing serialises cycles for a tenant. `reconcile` runs from the event stream, the debounce scheduler, start and rollback; `reconcileTypes` from a scheduler pool sized to the number of distinct intervals. Two cycles can provision the same node. No leader election or lock anywhere, so two replicas double-provision (same class as engine G2). | open |
| D4 | S2 | durability | `PlanApprovalGate` | Pending plans live in a `ConcurrentHashMap`; lost on restart (the approval WorkItem remains, orphaned). After a rejection the pending entry is removed and nothing remembers it: the next cycle computes the same plan and appears to submit it again, every cycle. An approved plan is executed as stored, without re-reading actual state (desired version is checked, actual is not). | open |
| D5 | S2 | bug | `AnsibleProcess.execute` | Reads stdout with `readAllBytes()` before `waitFor(timeout)`. A hung playbook blocks forever; the timeout is unreachable. | open |
| D6 | S2 | tenancy | `TenantProviderRegistry` | "Per-tenant process isolation" keys the pool on the hash of credentials resolved from one `credentialRef`; `tenancyId` is not passed to the resolver. All tenants share one provider process and one cloud identity unless the resolver is ambient-tenant-aware. | open |
| D7 | S2 | events | `StateEvent`, `TenantLoop.start` | `StateEvent` has no tenant; every tenant loop subscribes to the same merged stream and reconciles on any batch. On stream failure the subscription ends with a log line and is not re-established: that tenant silently falls back to resync only. | open |
| D8 | S2 | drift | `TerraformBridgeProvider.doReadState` | Drift = plan has errors or requires replace. In-place attribute drift (the common case) is reported as present. | open |
| D9 | S3 | supply chain | `ProviderRegistryClient`, `GpgSignatureVerifier` | Signing keys come from the same registry response and `trustedKeyIds` defaults to empty; missing signing data downgrades to the response's own shasum with a warning; match is on key id not fingerprint; cached binaries are not re-verified; no size limit. `binaryPath` executes any path from config. | open |
| D10 | S3 | injection | `PlaybookGenerator` | Node spec values are written into a playbook; Ansible evaluates Jinja in values, so a spec value containing a `lookup('pipe', ...)` expression runs a command on the controller. Matters if specs are ever tenant-authored. | open |
| D11 | S3 | design | `ReconciliationLoop` | 1,357 lines, three telescoping constructors up to 20 parameters plus a builder, half the collaborators nullable, fully qualified names inline. The one god class in an otherwise tidy repo. | open |
| D12 | S3 | robustness | `ParallelTransitionExecutor` | On layer timeout it calls `shutdownNow()` then `close()`, which waits for tasks: a provisioner that ignores interrupt blocks the cycle. Timed-out steps are recorded Failed though they may complete. | open |
| D13 | S3 | policy | `eidos/` `OrgDriftPolicy`, `OrgPlanApprovalPolicy`, `OrgGoalCompiler` | Thresholds 0.3 / 0.5 / 0.7 are literals in four classes. `OrgDriftPolicy`'s last three branches all return reconcile. Exemptions are `Never` revert. Approval depends on the gate D1 bypasses. | open |
| D14 | S3 | T-deser | `GraphSerializer` | Stored graph JSON carries class names resolved with `Class.forName`. Fine while the table is trusted; needs an allow-list if graphs are ever imported. | open |
| D15 | S3 | docs | `README.md` | 9 lines. No LICENSE (T22). CLAUDE.md is the real documentation. | open |

### Carry-over answers
- T fail-open defaults: `NoOpHumanNodeHandler` and `NoOpPendingApprovalHandler` skip or fail (correct, fail-closed). `NoOpPlanApprovalPolicy` auto-approves (expected default).
- Autonomy: two unconnected scales now exist: org-unit `selfDetermination` (enforced here) and agent `DecisionScope` (agency, unenforced).

### Not yet reviewed
`TransitionPlanner` internals, `CrossDomainCompositionEngine`, `LifecycleManager`, `CaseTransitionExecutor` (engine-adapter), work-adapter, annotations/YAML/TS compilers, plugin runtime and shell primitive, cty codec, persistence, examples, Spring modules.

## ops

First pass, commit d787b63. ~20.5k main lines, 11 modules. Domain implementations of the desiredstate SPI quad: `service/` (9.7k: K8s provisioning, application lifecycle, approvals, CVE, scaling, case descriptors, 9 `@McpDomain` APIs), `deployment/` (agent topology, the primary target), `infra/`, `compliance/`, `container/` (Podman), `claudony/`, thin `app/` and `runtime/` image. README labels every domain "Research"; severities below assume it will be exposed as shipped.

Strengths:
- Risk-based approval is a coherent design: `K8sApprovalEvaluator` classifies by node type, action and namespace (namespace delete = CRITICAL, deployment delete = HIGH), threshold HIGH, plan persisted, approval delivered as a WorkItem, roles per risk tier.
- Compliance has the right shape: control = node, evidence collector -> ledger entry, stale or failing evidence = DRIFTED, so posture is a reconciliation target and each check is an audit record.
- `LlmTriggerEvaluator` validates the LLM's choice against the catalogue and treats unknown output as reject (same safe pattern as agency routing).
- Test volume exceeds main (service 12k, deployment 6.6k, topology-tests 4.9k with live-instance profile).
- README is honest about maturity.

### Findings

| ID | Sev | Theme | Where | Note | Status |
|---|---|---|---|---|---|
| O1 | S1 | T-authz | `service/api/Ops*Api` (9 classes) | No `@RolesAllowed`, `@AclCheck` or equivalent on any operation. `@ContextParam("tenancyId")` is used on create/list in three classes only. Shipped `application.properties` has no HTTP auth policy. Every operation is callable by any caller that reaches the port, over REST and MCP. | open |
| O2 | S1 | T-tenancy | `OpsApplicationApi`, `OpsDeploymentApi`, `OpsClusterApi` | Object access by id with no tenant comparison. `listApplications` selects all tenants. Get, update (`servicesJson`, i.e. what gets deployed), delete, deploy and rollback take the tenant from the stored entity, not the caller. Cluster get/delete/test likewise. | open |
| O3 | S1 | T-attribution | `OpsApprovalApi.approve/reject` | `actorId` is an optional request parameter that overrides the principal; roles are still taken from the real principal. A caller with the role can record an approval under any name via `completeFromSystem`. Unknown plan -> risk LOW -> no role needed. | open |
| O4 | S1 | T-fail-open | `ConfigDrivenApprovalAuthorizer` | Role lists default to empty, and empty means authorised, for CRITICAL too. `runtime/` sets them; `app/` and any embedder do not. LOW and MEDIUM never need a role. | open |
| O5 | S1 | TLS | `ClusterReferenceEntity.trustCerts`, `K8sClientRegistry.register` | `trustCerts` defaults to true (entity field and the two-arg `register`), which disables certificate verification on the cluster API connection that carries the bearer token. | open |
| O6 | S2 | SSRF / secrets | `OpsClusterApi.registerCluster`, `K8sClientRegistry` | A caller supplies `apiUrl` and `credentialRef` freely. Any resolvable credential ref can be paired with any URL, so a stored token can be sent to a caller-chosen host. Needs ref ownership by tenant and a host policy. | open |
| O7 | S2 | T-ambient-tenancy | `rest/TenancyFilter` | Tenant from `X-Tenancy-ID` header, default `default`; property set on the request and not read anywhere in main code. Dead but misleading; remove or replace with principal. | open |
| O8 | S2 | bug | `K8sClientRegistry.register` | Re-registering a cluster keeps the existing client and only replaces metadata, so a changed URL or credential does not take effect until a 401 refresh. | open |
| O9 | S2 | maturity | `compliance/` | 1,074 lines. Four collectors, all local file checks (file exists, config hash, certificate expiry, log directory). No control catalogue ships (only two test YAMLs); SOC2/GDPR/EU AI Act/DORA/NIS2 are labels a user must supply. Evidence hash input is pipe-joined with free-text `detail` (L3). | open |
| O10 | S2 | design | `Ops*Api` | API classes use `EntityManager` directly, return JPA entities (including `credentialRef`, `tenancyId`), mutate without `@Transactional` in the API class, and return null for not-found in some methods and throw in others. `ClusterService.testConnectivity` is a stub returning UNKNOWN. | open |
| O11 | S3 | autonomy | `SelfMaintenanceMonitor` | The service can deploy a replacement of itself from an image ref; guarded by a flag and bootstrap phase only, no approval gate or signature check on the image. | open |
| O12 | S3 | state | `ApplicationLifecycleService.activeLoops`, registries | Active-loop tracking and client registry are in memory; `StartupRecoveryService` exists (not read). Inherits D3 single-node assumption. | open |
| O13 | S3 | docs | repo root | No LICENSE (T22). README lists an `iot` module that is not in this repo. | open |

### Carry-over answers
- D1/D2: ops does not use the Terraform/Ansible bridges; `infra/` has its own standalone backend. So "augments Terraform" is not yet demonstrated anywhere in code.
- Engine's API edge pattern (`@AclCheck`, tenant from context, service re-check) is not followed here; ops is the furthest from it of all reviewed repos.

### Not yet reviewed
`deployment/` (agent topology provisioner, targets, drift, trust routing provider), `container/` Podman client and provisioner, `claudony/`, `infra/` compiler and provisioner, K8s handlers and watch manager, case descriptors, scaling, CVE, bootstrap, topology compiler, startup recovery.

## scaffold

Quick pass, commit 131e902. 2.2k main lines, one backend module plus a web console (Quinoa). Deployable Quarkus app that embeds engine and ops and exposes `/api/scaffold/*` (cases, topology, catalogue, deployments, approvals, reconciliation) with `Embedded*` services (in-process) or REST clients to a remote ops.

- Good: resources take actor and tenant from `CurrentPrincipal` (better than ops); service interfaces with embedded and remote implementations; health checks; tests larger than main (3.1k).
- S1 **SC1**: no auth policy for `/api/**` in `application.properties` (only a permit rule for static files) and no role annotations; inherits O1 to O4 because it calls the ops API classes in-process.
- S2 **SC2**: `EmbeddedApprovalService.listPendingApprovals(tenancyId)` ignores the tenant; `getApproval(id)` has no tenant check.
- S2 **SC3**: `EmbeddedApprovalService` calls `opsApprovalApi.approve(approvalId, actorId)` with a `String`; ops at d787b63 declares `approve(UUID, Optional<String>)`. Looks like API drift between the two repos' heads (not built, so unconfirmed).
- S3 **SC4**: README is the Quarkus starter text under the title "flow" with badge links to `casehubio/flow`; Java package is `io.casehub.flow`. This is the first thing a new user runs and it explains nothing about CaseHub. `AppLoader.parse` swallows all exceptions and returns empty.
- Not reviewed: web UI, catalogue service, demo seed script.

## pages (casehub-pages)

First pass, commit 6602b4d (owner: mosaic builds on this). TypeScript monorepo, ~90k lines of non-test TS in 32 packages plus ~12k Java in `backend/` (data relay and query, push, layout, MCP, playbook runtime, terminal, dev auth), IntelliJ plugin, LSP. A page is a recursive component tree (layouts, charts, tables, forms, hosted Web Components) bound by reference to datasets in a reactive pipeline; authored via TypeScript DSL or YAML. Clones: `/home/user/casehubio/casehub-pages`, `/home/user/casehubio/casehub-mosaic` (13475e1, not reviewed, ~50 domain components).

Strengths:
- Best README and only complete licence set of all repos (LICENSE + Apache text). Capabilities table, getting started, guides.
- Clear architecture: data defined once and bound by reference; one event model (snapshot/append/replace/remove) for HTTP, WebSocket and generated sources; cross-filtering; everything is a `Component` node.
- Test volume exceeds source in the core packages (pages-runtime 20k test vs 10k, pages-data 20k vs 10k, yaml-core 12.8k vs 10.9k).
- **`backend/data` is the best-secured API edge outside engine**: `@Authenticated`, tenant from JWT claim, per-tenant cache. `SqlQueryBuilder` validates columns against an allow-list, quotes identifiers and binds values. `RelayClient` checks scheme, optional host allow-list, blocks loopback/site-local/link-local and disables redirects (better than connectors C2).
- `cross-parser-test` module checks Java/TypeScript parser parity for the shared YAML core.
- Real developer tooling: LSP, IntelliJ plugin, builder with grid editing, step viewer.

### Findings

| ID | Sev | Theme | Where | Note | Status |
|---|---|---|---|---|---|
| PG1 | S1 | RCE | `backend/terminal-runtime` `TerminalResource` (`/api/terminals`), `TerminalWebSocket` (`/ws/terminal/{id}/...`) | No authentication on either. Create a tmux session in any working directory, send keystrokes, read output: a shell on the server for anyone who reaches the port. FIFO at a predictable `/tmp` path. Must be authenticated, role-gated and off by default. | open |
| PG2 | S1 | T-authz | `backend/playbook-runtime` `PlaybookControlResource` (`/playbook/*`), `ActivationResource`, `PlaybookLibraryResource` | No authentication. `/playbook/start` accepts YAML in the request and runs it with REST and GraphQL dispatchers (server-side requests without the relay's target validation) and a caller-supplied `callbackUrl` + `callbackToken`. One global orchestrator: a single playbook state shared by all users and tenants. | open |
| PG3 | S1 | XSS | `pages-runtime/src/content.ts`, `pages-viz` `PagesMetric`, `yaml-core/src/expression/js-expression-engine.ts` | `renderHtml` assigns `props.content` to `innerHTML`; `renderMarkdown` assigns `marked.parse()` output unsanitised (marked does not sanitise); JS expressions compile with `new Function` + `with`. README says YAML pages can be "stored in a database". Whoever can author or influence a page (or data bound into html/markdown) runs script in every viewer's session. A sanitiser exists only in `pages-aria`. Needs a trust model: sanitise by default, JS expressions only for bundled pages. | open |
| PG4 | S1 | isolation | `pages-viz` `PagesIframePlugin`, `pages-iframe-api` `BrowserComponentBus`, `pages-data` post-message sources | README: "iframe-isolated microfrontends ... sandboxed". The iframe has no `sandbox` attribute and loads same-origin (`/pages/component/{id}/index.html`), so it has full access to the parent. Messages are posted with target `*`; no listener checks `event.origin` or `event.source`. Any frame can inject a dataset or a filter. | open |
| PG5 | S2 | auth | `backend/auth` `DevAuthResource` | Issues a signed JWT for any name and any roles. Guarded by `@UnlessBuildProfile("prod")`: present in every profile not literally named prod (staging, demo). Should be opt-in by an explicit dev flag. | open |
| PG6 | S2 | SSRF | `backend/data` `RelayClient` | Good baseline; gaps: resolves the host for the check and again for the request (DNS rebinding), misses any-local and IPv6 unique-local, forwards arbitrary method and headers, no response size limit, allow-list optional. | open |
| PG7 | S2 | layering | `platform/notifications` -> `casehub-pages-push`; `pages/backend` -> `casehub-platform-yaml-core`, simulation | Repo-level dependency cycle between platform and pages. README claims "Foundation tier, zero upstream CaseHub dependencies", which holds for the npm packages only. Push should move to platform or the pages backend should split. | open |
| PG8 | S2 | playbooks | `backend/playbook*` (5k Java), `packages/yaml-core` (10.9k TS) | A fourth playbook executor (UI scenario playbooks: navigate/wait/assert/graphql/rest/simulate) and a TypeScript port of yaml-core. Adds to P32/G6/G7. Parity test exists for parsing, not for execution semantics. | pages#669 |
| PG9 | S2 | extension API | `pages-runtime/src/panel-registry.ts`; mosaic `package.json` files | The extension point mosaic depends on is a module-global `Map<string,string>`: no collision check, no props schema, no version, and two bundled copies of pages-runtime give two registries (panel silently missing). Mosaic depends on pages packages with `*` ranges and `portal:` links; pages root version is 0.0.0. No API contract between the two. | open |
| PG10 | S3 | hygiene | repo root | `test-results/`, `test-completions/`, both `yarn.lock` and `package-lock.json` committed; mosaic root has eight screenshot PNGs. | open |

### For mosaic (not reviewed; ~50 components incl. `approval-gate`, `audit-trail-viewer`, `gdpr-erasure-action`, `agent-personality-workbench`)
- Mosaic is the UI of the controls. It inherits PG3/PG4 for every panel that shows agent- or user-authored text (conversations, narratives, audit trails): one unsanitised markdown render exposes the approver's session.
- An approval button is only as strong as the API behind it (W1/W2, O3, D1). The UI must not be the place a check lives.
- Before mosaic grows: versioned panel contract (PG9), default-sanitised content components, origin-checked message bus, and a statement of which package versions mosaic supports.

### Not yet reviewed
pages-runtime site/activation internals, pages-data pipeline, pages-builder, pages-aria, LSP, graph packages, push protocol and stores, MCP backend, data-json app catalogue, layout store, IntelliJ plugin, all of mosaic.

## mosaic (casehub-mosaic)

First pass, commit 13475e1. ~75k non-test TS lines, 44k test; 66 components + 10 packages (Lit Web Components), VS Code and IntelliJ plugins, 18-line Java app. The domain UI for the Java layers: work item inbox/detail/workbench, approval gate, notification inbox, channel activity and conversation viewers, audit trail, trust panels, org/HTN/SWF/case diagrams, agent catalogue/profile/personality workbench, evolution config, desired-state graph, reconciliation status, compliance summary, GDPR erasure action, 2D agent avatar.

Strengths:
- One component per concern with a consistent contract (properties in, `{topic}:selected` events out, `registerPanel`); generic shells (`split-workbench`, `list-pane`, `detail-pane`) reused by domain wrappers.
- Accessibility is designed in: ARIA roles, live-region `announce()`, keyboard shortcuts, progressbar semantics on quorum.
- **`channel-activity/markdown.ts` is the right pattern**: `marked` then DOMPurify with tag and attribute allow-lists. This is what pages lacks (PG3).
- `approval-gate` sends only `{outcome, resolution}`; it does not put the approver's identity in the request, and requires confirmation with a reason by default.
- README documents every component with tag, package and purpose. Tests are substantial for the busiest components (channel-activity 6.3k, work-item-inbox 2k, notification-inbox 2.6k).

### Findings

| ID | Sev | Theme | Where | Note | Status |
|---|---|---|---|---|---|
| M1 | S1 | T-attribution (W1) | `work-item-detail.ts` (claim, start, reject, suspend, resume, cancel, release, accept/decline delegation) | Every lifecycle call puts the acting identity in the URL from a component property: `/claim?claimant=${identity.userId}`, `/start?actor=...`. This is the client half of W1/W2: UI and API agree that the caller names the actor. Value is not URI-encoded (a user id containing `&` adds parameters). `approval-gate` does not do this, so the two paths to completing a gate differ. | open |
| M2 | S1 | auth | all components (104 `fetch` calls in 41 files) | No request carries credentials: no `Authorization` header, no `credentials` option, no shared client. Pages attaches a bearer token from `sessionStorage` in its own data calls; mosaic components call raw `fetch(endpoint + ...)`. Against an authenticated backend these calls fail; they work only where the API is open (W1, O1, SC1). Only `case-explorer` accepts an injectable `fetchFn`. | open |
| M3 | S1 | XSS | `document-workbench/src/document-diff.ts` | `marked.parse(content)` assigned to `innerHTML` with no sanitiser, and `err.message` interpolated into `innerHTML`. Documents here are the things agents and contributors write. The sanitising renderer in channel-activity is not shared. | open |
| M4 | S2 | T-ambient-tenancy | `audit-trail-viewer` (`?tenancyId=`), `notification-inbox` (subscription, mute bodies), `agent-relationship-editor` (`tenancy-id` default `default`) | Tenant is sent by the client from an identity property. Harmless only if every server ignores it. | open |
| M5 | S2 | privacy | `channel-activity/markdown.ts` | Allow-list includes `img` with `src`, and `target` without forcing `rel=noopener`. An agent message can embed a remote image whose URL carries data from the conversation (exfiltration by render) and learns the viewer's IP. Proxy or block remote images. | open |
| M6 | S2 | design | components | No shared API client: 41 files build URLs by string concatenation, each with its own error handling and response-shape guessing (`raw.item ?? raw`). One typed client (auth, encoding, errors, tenancy from token) would fix M1, M2, M4 in one place. | open |
| M7 | S2 | control UX | `approval-gate` | "Already decided" and quorum state are computed from properties supplied by the host; fine as display, but the component trusts `history`/`quorum.voters` it is given and offers no way to show the server's authoritative decision record (ledger entry id, who was authenticated). For a governance UI the receipt matters. | open |
| M8 | S3 | tests | `packages/agent-avatar-2d` (12.7k lines, 717 test), `document-workbench` (3.6k, 418), `work-item-detail` (1.8k, 346) | Largest package and two control-relevant components are thinly tested. | open |
| M9 | S3 | hygiene | repo root | Eight screenshot PNGs committed at root; no LICENSE (T22); pages dependency ranges `*` (PG9). | open |

### Carry-over answers
- PG3: partly answered. Mosaic sanitises channel messages but not documents; pages' own html/markdown components remain unsanitised.
- W1/W2: confirmed end to end. The client supplies the actor and the server accepts it.

### Not yet reviewed
agent-viewer, agent-avatar-2d, graph stencils, notification inbox internals, evolution and personality workbenches, trust components, gdpr-erasure-action beyond its request, plugins, lsp-schemas, mosaic-schema generation.

## claudony

First pass, commit a47e6ac. ~13k main Java lines (app 5.5k, casehub 6.8k, core 0.6k), 23k test; web UI (xterm.js, Lit, mosaic channel-activity). Runs Claude Code CLI sessions in tmux on one machine and exposes them through a browser workspace (terminals, channels, case browser, inbox). `casehub/` makes those sessions CaseHub workers: provisioner, agent pools, fleet of peer nodes, budgets, mesh messaging. Two modes from one binary: server (owns tmux, WebSocket streaming, REST) and agent (local MCP endpoint for a controller Claude). Clone: `/home/user/casehubio/claudony`.

Strengths:
- **Security posture is deliberate, the best of the deployable apps**: binds to localhost by default; passkeys via the Quarkus WebAuthn extension (not hand-rolled); path policy requires authentication on `/api/*`, `/ws/*`, `/app/*`; API key compared in constant time; cookie encryption key generated to a 0600 file; auth rate limiter; invite tokens with TTL.
- Worker launch is explicit about agent permissions: `--permission-mode`, `--tools`, `--allowedTools`, `--disallowedTools`, `--add-dir` come from per-provider config; arguments are single-quote escaped correctly (`shellQuote`).
- tmux `send-keys -l` (literal) used throughout, with a test for it.
- Tests are about twice the main code.

### Findings

| ID | Sev | Theme | Where | Note | Status |
|---|---|---|---|---|---|
| CL1 | S1 | injection | `casehub/fleet/TmuxAgentSession.query`, `TmuxService.sendKeys` | A prompt is delivered by typing `prompt + "\n"` into the session's terminal. Nothing strips newlines or control characters. A prompt assembled from case data (emails, messages, documents) with embedded newlines becomes several separately submitted inputs, and in the Claude Code TUI a line starting with `!` is a shell command and `/` a slash command. That path bypasses the configured permission mode. Not tested here; needs a test with hostile case content. Bracketed paste or a file/stdin hand-off would close it. | open |
| CL2 | S2 | contract | `TmuxAgentSession.query` | Emits `InvocationComplete` immediately with zero tokens, cost and duration, and no text. Callers of the platform `AgentSession` contract (engine workers, agency patterns, budgets, judgment) see a finished, free, empty turn before the agent has started. Results come back out of band (MCP, channels). The mismatch should be explicit in the type, not hidden behind the shared interface. | open |
| CL3 | S2 | budget | `WorkerCommandBuilder.budgetReportingPrompt`, MCP `report_cost` | Cost accounting depends on the agent choosing to call `report_cost` because a system-prompt line asks it to. Budgets built on this are advisory (compare A8). Claude Code's own usage output or API-side metering would be authoritative. | open |
| CL4 | S2 | authz | `ApiKeyAuthMechanism`, all `Claudony*Api`, `TerminalWebSocket` | Two roles are assigned (`user` for the agent key and passkey users, `fleet` for peers) but nothing checks them: no `@RolesAllowed`, and the path policy is only `authenticated`. A peer holding the fleet key can open any terminal and call every API, including "Generate a fleet key". | open |
| CL5 | S3 | secrets | `ApiKeyService` | Generated API key is printed in a WARN banner (ends up in log files and aggregators); key file is written before its permissions are tightened. One shared key for all agents. | open |
| CL6 | S3 | web | `TerminalWebSocket`, config | No Origin check on the WebSocket upgrade and no CSRF configuration; protection rests on the session cookie's SameSite default. `/q/*` is open. Add an explicit Origin allow-list since the socket is a shell. FIFO at a predictable `/tmp/claudony-<conn>.pipe`. | open |
| CL7 | S3 | duplication | `core/TmuxService`, `TerminalWebSocket` vs pages `backend/terminal*` | Pages carries a copy of this terminal stack without the authentication (PG1). One module, owned here, with auth mandatory. | open |
| CL8 | S3 | docs | repo root | README is the title and two badges. No LICENSE. CLAUDE.md holds the description and still names Quarkus 3.32.2 (parent is 3.39.3). | open |
| CL9 | S3 | design | product shape | Driving a vendor TUI by keystrokes and screen capture is brittle against CLI updates; single machine; one vendor. An SDK/headless path (stream-json) alongside tmux would give real results, usage and completion (fixes CL2, CL3). | open |

### Carry-over answers
- T19 (agent permissions): the only repo where agent tool permissions are a first-class, per-provider setting.
- Ops `claudony/` module provisions these as a desired-state domain; not cross-checked.

### Not yet reviewed
`casehub/fleet` (72 files: pools, scaling, scripts, budgets), provisioner and lineage, inbox, case browser, peer registry and mesh, expiry policies, push, web UI, agent-mode iTerm2/clipboard integration.

## ras (casehub-ras)

First pass, commit c179222. ~9k main Java lines, 18.5k test. "Reticular Activating System": observes CloudEvents, routes them to detection strategies ("ganglia": expression rules, naive Bayes, Java switch, Drools CEP), accumulates detections per (situation, correlation key, tenant), combines them with a chain mode (and/or/threshold/sequence/count/streak/rate), and on trigger starts a case or notifies. Feedback loop: case outcome labels feed precision/noise/recall statistics, suppression after dismissals, and automatic tuning of thresholds and Bayes priors. Clone: `/home/user/casehubio/casehub-ras`.

Strengths:
- Small, focused, well-typed: sealed `ChainMode`, `TriggerAction`, `TriggerMode`, `GanglionDescriptor`; YAML situation definitions.
- **The only repo that handles multi-node correctly at its critical point**: optimistic versions on the situation store with bounded retry, and `tryClaimTrigger` before firing so two nodes do not both start the case; claim is reset on failure.
- Event-time handling (reorder buffer, flush job), expiry job, replay runner for testing definitions against recorded streams.
- Metrics throughout (routed, filtered, race lost, trigger timers, drift gauges).
- Tests are twice the main code. Drools session persistence via drools-reliability with orphan cleanup.
- Quality loop is a real idea: per-ganglion attribution of outcomes, drift classification (over/under sensitive), `BOTH_DRIFTING` blocks auto-tuning.

### Findings

| ID | Sev | Theme | Where | Note | Status |
|---|---|---|---|---|---|
| R1 | S1 | bug / safety | `DefaultTuningStrategy.adjustThreshold`, `FeedbackUpdateJob` (every 5 min) | The threshold only ever moves up, by `learningRate * (noiseRate - limit)`, and the job re-applies that on every run using the same retention-window statistics, with no new outcomes needed. A burst of noise closures (10 minimum) ratchets the threshold to its cap of 1.0 within hours, i.e. the detector stops firing for that tenant. `UNDER_SENSITIVE` is classified but nothing lowers the threshold. Needs: adjust once per new evidence, a floor/ceiling per situation, and a downward path. | open |
| R2 | S1 | T-authz / attribution | `MissedDetectionResource` (`/api/ras/feedback/missed`) | No authentication; `tenancyId` and `reportedBy` come from the request body. Anyone can file missed-detection reports for any tenant, which moves recall, flips drift to `BOTH_DRIFTING` (disabling tuning) and pollutes per-ganglion statistics. | open |
| R3 | S2 | governance | feedback loop as a whole | Whoever can close cases with a "noise" label controls suppression (cooldown) and tuning for a detector. In a SOC or AML setting, silencing alerts is the attacker's goal. Outcome labels need an authorised actor, tuning changes need a ledger entry and ideally an approval for decreases in sensitivity. None of the tuning is written to the ledger. | open |
| R4 | S2 | state | `FeedbackState` | Threshold and prior overrides live in two `ConcurrentHashMap`s: lost on restart, different on each node. A tuned detector reverts silently; two replicas apply different thresholds to the same tenant. | open |
| R5 | S2 | tenancy | `RasEngine.extractTenancyId`, `DefaultCaseTrigger.fire` | Tenant is the `tenancyid` CloudEvent extension, trusted as given. The case is started with `hub.startCase(inputData)`; the tenant is only a key in the input map, so the case's actual tenant is whatever the engine resolves on the async observer thread. Needs checking against engine's system principal behaviour (G23). | open |
| R6 | S2 | delivery | `RasEngine.onCloudEvent` (`@ObservesAsync`), `SituationEvaluator` | Events are at-most-once: an exception is logged and counted, the event is gone. Between a successful `startCase` and the post-fire save there is no idempotency key, so a crash there can produce a duplicate case on retry of a later event. | open |
| R7 | S2 | T-fail-open | `RasEngine` event filter | A filter that throws is treated as pass-through. For a filter used to exclude events (e.g. by tenant or source) the safe default is to drop. | open |
| R8 | S3 | docs / build | `ras-llm/`, README | `ras-llm` is a module in the reactor and in the README ("LlmGanglion — narrative detection") but contains only a `pom.xml`. README design-spec link points to a `docs/superpowers/` path. No LICENSE. | open |
| R9 | S3 | expressions | YAML definitions | Correlation keys, filters and dynamic case data are platform expressions (MVEL/JQ); same P2 caveat if definitions are ever tenant-authored. | open |

### Carry-over answers
- D3/G2 (single node): ras shows the pattern the others need: versioned store plus an explicit claim before a side effect.
- Used by desiredstate (`ras-adapter`), ops scaling and adaptation, engine situation response.

### Not yet reviewed
`SituationEvaluator` in full, chain mode evaluation, `NaiveBayesGanglion` maths, Drools ganglion and session store, JPA stores, replay runner, YAML provider, registry.

## Cross-cutting conclusions (update as repos are added)

1. **Identity is asserted, not authenticated, at every API edge** (L1, L2, W1, Q1, Q2). One fix pattern: actor and tenant from `CurrentPrincipal` only, via `@ContextParam`; request-supplied actor only for a trusted-service role.
2. **The ledger write path has four implementations** (ledger x2, work, qhorus) with different guarantees. Ledger should own one `append` service; consumers should only supply subclass fields.
3. **`CurrentPrincipal` and `LedgerEntryRepository` resolution depends on which jars are present.** Needs one documented precedence table and a composition test in an app that includes everything.
4. **Erasure and retention both mutate or delete hashed data without verification knowing** (L8, L10, W5, Q8). Verification needs a defined model for tombstones and pruned ranges.
10. **W1/W2 is now the highest-leverage fix in the codebase.** Engine's human-in-the-loop (action gates, quorum approvals, judgments) is delivered as WorkItems, and work does not check who claims or completes them (G28). Confirmed from the UI side (M1): mosaic sends `?actor=` / `?claimant=` from a client property.
11. **Autonomy needs one governance statement.** Self-set goals, belief revision, personality change, unprompted contact (neocortex), swarm provisioning and self-improvement including code (engine) are each bounded in code but explained nowhere together; two defaults are open (G22, G25).
6. **Safety controls exist as types but are not wired** (C1 confirmation, P16 circuit breaker, N40 journal to ledger). Each needs an end-to-end test proving the control fires.
8. **Playbooks are three languages today** (interpreter in the test runner; compiler in engine; step-file bridge), with the plugin-step vocabulary available only in the first (P21, P32, P41, G6, G7). The "every API is a step" strategy depends on making engine's path accept plugin steps.
9. **Engine's API edge is the reference implementation** (`@ContextParam` tenant, `@AclCheck`, service-level re-check). Ledger, work, qhorus and neocortex's corpus API should adopt it.
7. **Agent-reachable tools lack an egress policy** (C2, C3, C8; P7 process execution). One shared URL/host policy and budget would cover them.
5. **Canonical hash input is ambiguous** (L3, Q3). Needs a versioned, length-prefixed encoding before data accumulates.

12. **Agency models its controls and stops one step short of enforcing them** (A1, A2, A14, A15): pattern governance is not compiled, annotations are not wired, decision scope is never checked, human judges cannot be dispatched. Graduated autonomy therefore has no runtime effect. Needed: a real `AgentCapabilityGuard` called on every agent action; governance specs compiled into engine gates and trust routing; a WorkItem-backed judgment dispatcher; autonomy changes driven by ledger trust and judgments, persisted and attested.

13. **Approval gates are bypassed or forgotten on secondary paths** (D1, D4; compare G31 ReAct tools). Every control needs a test that tries each execution path, not only the main one.

14. **The outermost layers are the least protected** (O1 to O6, SC1). Engine checks at its API edge; ops and scaffold, which sit in front of it and can change what runs on a cluster, check nothing. The deployable app needs a default-deny HTTP policy and the ops APIs need engine's pattern.

15. **The UI layer needs a content trust model before mosaic builds on it** (PG3, PG4, PG9). Agent output is untrusted text; it will be rendered next to approval buttons.

16. **Self-tuning needs the same governance as self-improvement** (R1, R3, R4; compare A3, N-autonomy, engine evolution loop). Any loop that changes its own sensitivity must be bounded, durable, attributable and recorded.

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
- Eidos: "agent identity" as a structured, queryable, vocabulary-grounded descriptor with health and behavioural contracts. Neighbours: A2A agent cards, AGNTCY/OASF agent schemas, MCP server metadata, agent registries in CrewAI/AutoGen (name + role + backstory strings). Eidos is richer than all of them on capability semantics (graded matching, epistemic domains, exclusions, learned exclusions) and is the only one that treats the descriptor as a testable behavioural contract. That is a strong, defensible position. The personality vocabularies are the weakest part for an enterprise audience (E1, E2); capability and compliance are the strongest.
- Engine: this is the product. Nearest neighbours by category: Camunda/Flowable CMMN (case management, but human-centric and model-driven), Temporal (durable execution, code-first, no goals), LangGraph/CrewAI/AutoGen (agent orchestration, little durability, governance or human tasks), Drools/blackboard lineage (reactive rules). Engine's combination, goal-driven blackboard + durable execution + human tasks + agents as workers + self-healing plans + audit ledger, is not something any one of those offers. The claim to lead with is "case management for mixed human and agent work, with accountability", not "agent framework".
- Engine risk for that claim: single-node state (G1, G2) is the first thing an enterprise architect will probe, before any feature.

- Agency: the category is "organisational operating model for agents" rather than an agent framework. Neighbours: CrewAI/AutoGen/LangGraph (patterns, no org model, no durability), Microsoft Agent Framework and Google ADK (patterns + enterprise hosting), Salesforce Agentforce and ServiceNow (agents inside one vendor's org model). Agency's edge: policy-composed patterns, graduated and budgeted autonomy, trust-weighted routing, negotiation and coalition protocols, all on a durable case engine with a ledger. No neighbour has graduated autonomy as a first-class runtime concept. The edge is real only once A1 to A4 are closed, because "declared oversight that does not fire" is the first thing a risk officer will test.

- Desiredstate: neighbours are Kubernetes controllers/Crossplane (reconciliation, K8s-only), Terraform/Pulumi/OpenTofu (plan/apply, no continuous loop), Ansible, and Flux/Argo (GitOps). The distinct idea is reconciliation as a domain-neutral primitive with human gates, fault escalation and CBR, applied to agent fleets and org structure as well as infrastructure. "Continuous compliance posture" (ops) rests on it. The Terraform bridge is the credibility test: it must hold state (D2) and detect in-place drift (D8) before the "augments Terraform" claim can be shown to an infra team.

- Ops: continuous compliance competes with Vanta, Drata, Secureframe (evidence collection via hundreds of SaaS integrations, auditor workflow) and with policy engines (OPA/Kyverno, Chef InSpec, OpenSCAP). The CaseHub angle, posture as a reconciled desired state with every evidence check on a tamper-evident ledger and remediation as a governed case, is distinct and fits the EU AI Act / DORA "continuous" language. Today it is a skeleton (O9): the value is in the control catalogues and collectors, which do not exist yet. Agent-fleet deployment (the stated primary target) has no direct competitor and is the better first proof.

- Pages: neighbours are low-code/internal-tool builders (Retool, Appsmith, Budibase, Tooljet), dashboarding (Grafana, Superset, the Dashbuilder lineage this resembles), and microfrontend shells. Distinct points: declarative component tree shared by a TypeScript DSL and YAML, one reactive data and event bus, hosted Web Components, and tooling (LSP, IDE plugin, builder). With mosaic it becomes the operator console for agents: approvals, audit trails, org diagrams, agent workbenches. That console is what makes the governance story visible to a buyer; no agent framework ships one. Its credibility depends on the UI being safe to show untrusted agent output (PG3, PG4).

- Claudony: neighbours are remote/managed coding-agent products (Claude Code on the web and remote control, Cursor background agents, Devin, OpenHands) and tmux-based session managers for coding agents. What is different: a session is a governed CaseHub worker with lineage, channels, commitments, a human inbox and a ledger, on hardware the user owns. It is also the most convincing demo in the ecosystem, because the agents do real work. Constraint: it drives one vendor's terminal UI.

- Ras: neighbours are CEP and stream processors (Drools Fusion, Flink CEP, Esper), alert correlation in SIEM/AIOps (Splunk ES, Elastic, PagerDuty, Moogsoft-style), and event-driven automation (Event-Driven Ansible, StackStorm). Distinct: detection is pluggable and mixed (rules, Bayes, CEP, later LLM), the unit of response is a governed case rather than an alert or a script, and case outcomes feed back into detector quality with per-detector attribution. That closed loop (detect, act through a case, learn from the outcome) is uncommon and fits SOC, AML and ops well. It is credible only when the learning cannot silence the detector (R1, R3).

## Open questions

- Ras: is automatic threshold tuning meant to be one step per new batch of outcomes (R1)? Who is allowed to label an outcome as noise (R3)? Is `ras-llm` planned or dropped (R8)?

- Claudony: is keystroke delivery of prompts intended long term, or is a headless/SDK path planned (CL1, CL2, CL9)? Should fleet peers be restricted to a peer API (CL4)?

- Mosaic: how are component requests meant to be authenticated (cookie session, host-patched fetch, or a client to be written) (M2)? Should work-item actions stop sending `actor`/`claimant` once work derives it from the principal (M1)?

- Pages: who may author pages and markdown/html content at runtime (trusted developers only, or tenant users)? Are the terminal and playbook-control modules meant for dev use only (PG1, PG2)? Is the platform <-> pages dependency cycle intended (PG7)?

- Ops: are the `Ops*Api` classes expected to sit behind a gateway, or should they adopt engine's `@AclCheck` pattern (O1, O2)? Is the `actorId` override on approve meant for a trusted-service caller only (O3)?

- Desiredstate: is the type-filtered resync meant to skip plan approval (D1)? Is the bridge state store intentionally unwired pending a JPA store (D2)? Is multi-replica operation expected (D3)?

- Agency: is pattern-level `governance:` meant to compile into engine action gates and `TrustRoutingPolicyProvider`, and is that work scheduled? Is the annotations module known to be unwired?
- Agency: should graduation be driven by ledger trust and judgment outcomes, and should scope changes be attested?
- Agency: are protocol advisories meant to stay advisory, with enforcement in qhorus channel governance?

- Engine: is multi-node operation a goal, and if so via sticky routing, a distributed cache, or stateless reload per event?
- Engine: should playbook workers accept plugin steps (pass the plugin registry to the compiler), or is the compiler dialect intentionally narrower?

- Connectors: is confirmation meant to be enforced by the calling layer (engine/agency) rather than by decorators?

- Qhorus: are agents expected to authenticate (agent cards, DIDs) before posting, and where is that enforced?

- Work: is the lifecycle API expected to sit behind a trusted gateway that injects the actor? If not, W1/W2 are the top fix.
- Work: was `TenantScopedPrincipal` priority 150 meant to beat OIDC?

- Ledger: is the append/attest API meant for trusted services only? If so it needs a role, not network trust.
- Ledger: should the erasure receipt hold a hash of the actor id rather than the raw value?

- Is the callback dispatch endpoint meant to sit behind network-level trust only?
- Is MVEL in subscription filters intended for end users or admins only?
- Which modules are considered stable today?
