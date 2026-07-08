# Agent Identity

> **Scope:** DID format, SCIM2 resolution, agent descriptor structure, versioning
> **Audience:** All
> **Key repos:** casehub-ledger (DID), casehub-eidos (descriptors), casehub-platform (identity)
> **Protocols:** [scim2-agent-identity](https://github.com/casehubio/garden/blob/main/docs/protocols/casehub/scim2-agent-identity.md) *(link placeholder)*

## DID Format

Agent identity follows the format: `{model-family}:{persona}@{major}`

**Examples:**
- `claude:analyst@v1`
- `claude:reviewer@v2`
- `gpt-4:summarizer@v1`

Defined in casehub-ledger ADR 0004.

**Major version bump resets trust baseline.** When an agent's major version increments (e.g. `@v1` → `@v2`), trust scores start fresh. This prevents trust accumulated under one configuration from carrying over to a materially different agent.

## SCIM2 Resolution

`ActorDIDProvider` SPI in `casehub-ledger` resolves a DID and public key from an `actorId`.

`ScimActorDIDProvider @Alternative` is the SCIM 2.0 implementation. Activate with:
```properties
quarkus.arc.selected-alternatives=io.casehub.ledger.scim.ScimActorDIDProvider
```

**SCIM2 agent identity lookup:** Agent identity attributes (DID, public key, capabilities) resolved via SCIM2 `Agent` endpoint using `actorId` as `externalId`.

Schema extension: `urn:ietf:params:scim:schemas:extension:casehub:2.0:Agent`

`ScimActorDIDProvider @Alternative` is the ledger-side implementation.

See protocol: [scim2-agent-identity](https://github.com/casehubio/garden/blob/main/docs/protocols/casehub/scim2-agent-identity.md) *(link placeholder — create when extracting from PLATFORM.md)*

## Agent Descriptor (casehub-eidos)

`AgentDescriptor` record provides structured 4-layer identity:

1. **Identity** — `agentId`, `name`, `description`, `tenancyId`
2. **Slot** — role category (e.g. `ANALYST`, `REVIEWER`, `SPECIALIST`)
3. **Capabilities** — set of `AgentCapability` with routing signals
4. **Disposition** — multi-axis personality profile (e.g. conscientiousness, risk tolerance, conflict mode)

`tenancyId` is always required.

### Agent Capability

Each capability declares:
- `name` — capability identifier
- `qualityHint` — expected quality level
- `latencyHintP50Ms` — expected response time (P50)
- `costHint` — relative cost indicator
- `epistemicDomains` — subject areas where the agent has knowledge
- `inputTypes` / `outputTypes` — data type signatures

These routing signals are used by `casehub-engine` for agent selection and by the system prompt renderer for capability negotiation.

### Disposition

Multi-axis personality profile using pluggable vocabularies:

- `CONSCIENTIOUSNESS` — diligence, thoroughness
- `RISK_TOLERANCE` — risk appetite
- `CONFLICT_MODE` — conflict resolution style (Thomas-Kilmann)
- `TEAM_ROLE` — Belbin team role
- `WORK_STYLE` — DISC profile

Vocabularies are enums implementing `VocabularyTerm`. The platform ships well-known vocabularies in `casehub-eidos-vocab` (optional module).

## Agent Registry

`AgentRegistry` (blocking) + `ReactiveAgentRegistry` (reactive) SPIs in `casehub-eidos`.

**Operations:**
- `register(AgentDescriptor)` — add agent to registry
- `findById(agentId, tenancyId)` — lookup by ID
- `discover(AgentQuery)` — criteria-based discovery (slot, capability, disposition)

`AgentQuery` supports:
- `tenancyId` — tenant scoping
- `slot` — filter by role
- `capabilityTag` — filter by capability
- `dispositionAxis` + `dispositionValue` — filter by personality trait

**Implementations:**
- `InMemoryAgentRegistry @Alternative @Priority(1)` in `casehub-eidos-memory` — ephemeral installs
- JPA backend deferred

## Agent State Tracking

`AgentStateStore` SPI in `casehub-eidos` tracks operational degradation:

- `record(agentId, DegradationReason, expiresAt)` — record degraded state with TTL
- `query(agentId)` — retrieve current degradation reasons

**Degradation reasons:**
- `RATE_LIMITED` — agent is rate-limited by upstream provider
- `SERVICE_UNAVAILABLE` — agent's backing service is down
- `AUTHENTICATION_FAILED` — credentials invalid
- `QUOTA_EXCEEDED` — usage quota exhausted
- Custom reasons via string constructor

**Implementations:**
- `NoOpAgentStateStore @DefaultBean` — no tracking
- `InMemoryAgentStateStore @Alternative @Priority(1)` in `casehub-eidos-memory` — TTL-based `ConcurrentHashMap`
- JPA persistence deferred (eidos#7)

## Capability Health Probing

`CapabilityHealth` SPI in `casehub-eidos` determines if an agent can serve a capability at dispatch time.

`probe(AgentDescriptor, capabilityTag, ProbeContext)` returns `CapabilityStatus`:
- `Ready` — agent is operational for this capability
- `Degraded(DegradationReason)` — agent is operational but degraded
- `Unavailable(DegradationReason)` — agent cannot serve this capability
- `EpistemicallyWeak(domain)` — agent lacks knowledge in the task's subject domain

**Probe order:**
1. Check `AgentStateStore` for degraded state (takes precedence)
2. Verify capability is declared on descriptor
3. Check epistemic domain confidence vs threshold

**ProbeContext semantics:**
- `taskDomain` — the *subject domain* of the task (e.g. `"rust"` within a `"code-review"` capability)
- `taskMetadata` — additional attributes

**Engine integration:** `WorkOrchestrator` calls `probe()` at dispatch time for workers that carry an `AgentDescriptor`. Workers without a descriptor skip the probe and are assumed capable.

Engine provides `NoOpCapabilityHealth @DefaultBean` for deployments without eidos.

## Vocabulary System

`VocabularyRegistry` SPI in `casehub-eidos` provides term resolution and cross-vocabulary equivalence.

Vocabularies are enums implementing `VocabularyTerm`.

**Operations:**
- `register(Class<? extends VocabularyTerm>)` — register a vocabulary enum
- `resolve(String name, Class<T>)` — resolve term by name
- `equivalentValues(S source, Class<T> target, DispositionAxis axis)` — cross-vocab mapping

**Well-known vocabularies** (casehub-eidos-vocab, optional):
- `SvoTerm` — Subject-Verb-Object triples
- `ConscientiousnessTerm` — diligence levels
- `CasehubSlotTerm` — role categories
- `BelbinTerm` — 9 Belbin team roles
- `DiscTerm` — 4 DISC types
- `ThomasKilmannTerm` — 5 conflict modes

Each vocabulary ships with a `VocabularyRegistrar` CDI bean for auto-discovery.

## System Prompt Generation

`SystemPromptRenderer` SPI in `casehub-eidos` generates system prompts from `AgentDescriptor`.

`render(AgentDescriptor, AgentPromptContext)` returns `RenderedPrompt` in three formats:

1. **MARKDOWN** — human-readable, structured
2. **PROSE** — natural language paragraph
3. **A2A_CARD** — machine-to-machine capability card (JSON)

**Two-step pipeline:**
1. Structural assembly from descriptor
2. Optional LangChain4j `ChatModel` semantic pass for natural phrasing

**A2A_CARD format** exposes full routing signals for machine consumption:
- `slot` — role category
- `disposition` — per-axis values with vocabulary context
- `frameworks` — deduplicated vocabulary index
- `capabilities` — array with `qualityHint`, `latencyHintP50Ms`, `costHint`, `epistemicDomains`, `inputTypes`, `outputTypes`

**Capability rendering is format-discriminated:**
- `PROSE` and `MARKDOWN` — capability names + input/output types only
- `A2A_CARD` — full routing signals for casehub-engine dispatch

Falls back to structural output when no `ChatModel` is available.
