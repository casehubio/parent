# Agent Identity & Cognition

*Agents that are someone, not just something.*

Every AI agent on the CaseHub platform has a structured, machine-readable
identity. Not a role string. Not a system prompt paragraph. A typed,
vocabulary-grounded descriptor that the platform uses for dispatch,
compliance, trust, prompt rendering, and personality evolution.

No competitor has this. LangChain, CrewAI, and AutoGen define agents
with ad-hoc strings — "you are a helpful research assistant." CaseHub
defines agents with typed descriptors covering identity, capabilities,
disposition, goals, constraints, voice, and organisational membership.
The descriptor IS the contract. Compliance is tracked, enforced, and
auditable.

The production capabilities alone are unmatched. The cognitive
architecture — goal cognition, emotional appraisal, progressive
attention — extends this foundation toward agents that reason about
their own state and adapt their behaviour through experience. That
work is research-grade and actively developed, positioned as trajectory
rather than headline.

---

## Production Capabilities

### Structured Agent Identity

Four-layer typed descriptor model:

| Layer | What it captures | Key types |
|-------|-----------------|-----------|
| **Identity** | Who the agent is — name, role, vocabulary-grounded classification | `AgentDescriptor`, `AgentIdentity` |
| **Capabilities** | What the agent can do — typed capabilities with health status | `AgentCapability`, `CapabilityHealth` |
| **Disposition** | How the agent behaves — personality, communication style, decision patterns | `AgentDisposition`, `DispositionHealth` |
| **Goals & Constraints** | What the agent aims for and what it must not do | `AgentGoals`, `BehaviouralConstraint` |

Every field is vocabulary-grounded. Classification uses XKOS-style
subsumption matching across 12+ vocabulary systems: Jungian cognitive
functions, MBTI, DISC, Belbin team roles, Big Five personality traits,
Enneagram, SDI, Thomas-Kilmann conflict modes, archetypes, model tiers,
capability taxonomies, and slot classifications.

This means agent matching is semantic, not string comparison. When the
engine needs "an agent suited for mediating a conflict between two
teams," it doesn't search for the word "mediator" — it traverses
vocabulary hierarchies to find agents whose disposition subsumes
mediation capability, using OWLS-MX-inspired matching modes (Exact,
Plugin, Specialization).

**Capability health probing** evaluates agent readiness at dispatch
time through a 7-step sealed status hierarchy: Ready → Degraded →
Overloaded → Unavailable → Excluded → EpistemicallyWeak →
BehavioralViolation. The engine's WorkOrchestrator calls
`CapabilityHealth.probe()` before every dispatch decision — agents
that are overloaded, behaviourally non-compliant, or epistemically
weak are filtered before routing even begins.

**Multi-format prompt rendering** serves one descriptor to multiple
LLM providers: MARKDOWN format for Claude, PROSE format for
OpenAI/Gemini, and A2A_CARD format for machine-to-machine
communication. A two-stage pipeline with optional LLM semantic
enrichment ensures each provider receives identity information in its
preferred format.

**Agent Team DSL** — fluent Java DSL for multi-descriptor composition
with shared defaults. Compose agent teams declaratively: define a
team with shared capabilities, individual specialisations, and
coordination rules in a single expression.

14 modules. 303 Java source files. Full JPA persistence with Flyway
migrations.

### Personality Evolution

Agents don't just have static personality profiles — they evolve.

The Jungian Personality Assessment Framework (JPAF) models 8 cognitive
functions across 16 MBTI types with disposition health probing and
three forms of personality evolution:

- **Drift detection** — gradual shifts in cognitive function activation
  patterns, detected through accumulated signal analysis
- **Function swap** — a secondary function moves into the primary
  position based on sustained activation
- **Structural reorganisation** — fundamental personality restructuring
  triggered by significant behavioural events

Evolution is experience-driven. As agents execute tasks, their outcomes
feed back into disposition health scores. An agent that consistently
succeeds at analytical tasks will see its Thinking function strengthen.
An agent that receives repeated compliance violations will see its
behavioural health degrade, triggering personality review.

The 60-archetype personality system (faceted framework intersection
across Jungian, MBTI, DISC, Belbin, Big Five) provides a rich
vocabulary for personality configuration. Model selection via eidos
vocabulary enables identity-scoped LLM routing — a "meticulous
analyst" archetype selects different model parameters than a "creative
explorer." Archetypes drive avatar code generation — agents don't
just have personality, they have visual identity that reflects it.

### Voice Profiles

Structured speech characteristics that define how an agent communicates:

- **Register and accent** — formal/informal, regional patterns
- **Vocabulary preferences** — technical depth, jargon affinity
- **Catchphrases and quirks** — distinctive speech patterns
- **Persona inheritance** — voice profiles compose hierarchically

Voice profiles feed into prompt rendering, ensuring that an agent's
communication style is consistent across all interactions — whether
the agent is chatting in Slack, responding to an MCP tool call, or
participating in a multi-agent debate.

### Behavioural Contracts

The descriptor IS the contract. Compliance isn't hoped for — it's
tracked and enforced.

Learned signal accumulation monitors four signal types: DECLINE,
SUCCESS, COMPLIANT, and VIOLATED. Per-tenancy thresholds (resolved
via the platform's PreferenceProvider ancestor-chain walk) define when
accumulated violations trigger enforcement. Detection operates at
two levels:

- **Per-dimension** — individual behavioural constraints checked
  independently
- **Aggregate** — overall compliance health across all dimensions

Compliance attestations flow to the ledger, creating a tamper-evident
record of every behavioural assessment. When an agent's disposition
health drops below threshold, the CapabilityHealth status moves to
BehavioralViolation — and the engine excludes it from dispatch until
compliance is restored.

### BDI Agent Intelligence

Belief-Desire-Intention architecture integrated into the orchestration
framework. Not academic abstractions — practical primitives that
compose with routing and execution:

**Beliefs** — structured belief sets with consistency checking. When an
agent acquires a new belief that contradicts an existing one, the
ConsistencyChecker detects the conflict. Beliefs feed decomposition
context, giving agents grounded knowledge for decision-making.

**Intentions** — joint intentions with reconsideration signals. When
conditions change during multi-agent execution, ReconsiderationSignal
triggers re-evaluation of shared commitments. IntentionMonitor tracks
which agents hold which intentions and detects divergence.

**Coalitions** — capability-coverage evaluation for team formation.
CoalitionEvaluator assesses whether a proposed group of agents covers
the required capabilities. CapabilityCoverageEvaluator computes
coverage scores across the coalition.

**Judgment** — JudgmentDispatcher routes judgment calls through 5
AgreementPolicy variants with CompositeVerifier for multi-criteria
assessment. Judgment is an explicit step, not an implicit LLM call.

25 modules in the blocks repo support BDI alongside the orchestration
patterns. 903 Java source files total.

### Speech Pipeline

Agents don't just have personality — they can speak it. The speech
pipeline integrates sherpa-onnx via Foreign Function Memory (FFM) for
on-device speech-to-text and text-to-speech processing.

- **AvatarCognition SPI** — social cognition (mood, drives,
  personality) feeds into speech generation. An anxious agent speaks
  differently from a confident one.
- **Per-phoneme timing** — lip-sync animation data generated alongside
  audio for visual avatar rendering
- **Social cognition integration** — speech delivery adapts to the
  agent's current emotional state and personality disposition

Multiple TTS backends beyond sherpa-onnx: Dia TTS (dialogue-native
with emotional rendering), CosyVoice TTS, Audio8 TTS. Streaming
LLM-to-TTS pipeline for real-time speech generation. Speaker
identification via voiceprint (ECAPA-TDNN neural embeddings).
Two-pass STT accuracy pipeline with contextual correction.

This completes the identity → personality → voice → speech chain:
agents defined with structured descriptors, personalised through
experience, voiced through profiles, and rendered through
mood-modulated speech synthesis.

### Affordance & World Model

Agents perceive and interact with a typed world model, not raw data
streams. `ObservableEntity`, `Affordance`, `ActionDescriptor`, and
`PerceptionFilter` compose a formal environment perception layer.
YAML-declarable. Agents don't just react to events — they perceive
affordances in their environment and select actions based on what the
environment allows. No competing framework offers typed affordance
perception as infrastructure.

### Drive Architecture & Intrinsic Motivation

Agents have intrinsic motivation. The drive architecture creates
goals autonomously — not just responding to external task
assignments. Drive signals translate into concrete `AgentGoal`
instances for the engine's goal lifecycle. This is the bridge between
social cognition (mood, drives) and concrete execution: an agent's
internal motivational state produces real work through the case
engine.

Combined with autonomous goal generation, this means CaseHub agents
self-direct. They observe their environment (affordances), feel
intrinsic motivation (drives), generate goals, and pursue them
through the case lifecycle. This is a fundamentally different agent
model from "receive task, execute task, return result."

### Agent Learning & Memory Architecture

Cross-cutting architecture bridging agent-level memory, reflection,
and goal lifecycle across neocortex, eidos, and blocks. Agents
remember individual experiences, synthesise insights, and form and
revise goals based on accumulated experience. Three-tier memory model:
episodic events (Tier 1) → experience consolidation (Tier 2) →
structured knowledge graph (Tier 3). Agents graduate lived experience
into persistent understanding.

### Social Cognition Framework

90+ types implementing a full social intelligence stack. Nothing
comparable exists in any competing framework.

| Capability | What it does |
|-----------|-------------|
| **Mood** | PAD (Pleasure-Arousal-Dominance) emotional state that modulates all downstream cognition |
| **Drives** | 4 axes — curiosity, competence, affiliation, autonomy — with drive modulation pipeline (raw → mood → personality → clamping → composition) |
| **Mental Model** | BDI Theory of Mind — what this agent believes other agents believe, desire, and intend |
| **User Model** | Familiarity tracking, relationship stage progression |
| **Narrative Identity** | First-person autobiography construction — agents build coherent self-narrative from accumulated experience |
| **Goal Proposal** | Drive-to-goal mapping with escalation rules, cross-axis composition, narrative alignment |
| **Social Emergence** | Norm detection, collective goal formation from group interaction patterns |
| **Needs Pyramid** | Hierarchical need model driving attention allocation |
| **Strategy Learning** | Accumulated interaction patterns informing future coordination behaviour |
| **Inner Life** | Proactive initiation — agents that start interactions based on internal state, not just external triggers |
| **Engagement Tracking** | Interaction quality measurement feeding back into relationship models |
| **Consolidation Mediation** | Cross-store memory consolidation during cognitive downtime |

The entire stack renders as PromptSections for LLM consumption. Social
cognition is infrastructure, not application logic — any agent on the
platform can activate social cognition modules and gain mood-aware,
narrative-grounded, socially intelligent behaviour.

JPA persistence for all social cognition stores. Quarkus and Spring
Boot support.

---

### Cognitive Observability

Three-layer observability makes cognitive agent behaviour inspectable
and debuggable — no competing framework offers this:

- **Layer 1: Live View** — real-time MCP tools for graph inspection,
  delta tracking, health monitoring, and cognitive trace. Watch an
  agent's beliefs, goals, and social cognition state change in real
  time.
- **Layer 2: Snapshot Infrastructure** — point-in-time cognitive state
  capture for comparison and regression testing.
- **Layer 3: Temporal Observation** — tools for understanding how
  cognitive state evolves over time, identifying patterns in
  belief revision, goal formation, and emotional appraisal.

You can observe and debug what an agent thinks, not just what it does.

---

## Horizon: Cognitive Architecture

The production capabilities above establish who agents ARE. The
cognitive architecture extends this toward agents that reason about
their own cognitive state. This work is research-grade — actively
developed, not yet proven at scale. Credibility matters more than
hype, so it's positioned as trajectory.

### Goal Cognition

Five-phase cognitive lifecycle for goal processing:

```
Recognition → Affect → Prioritization → Resolution → Decay
```

Goals are recognised from environmental signals, appraised
emotionally (how does this goal make me feel?), prioritised against
competing goals, resolved through action selection, and decayed when
no longer relevant. Goal horizons span from IMMEDIATE through
ASPIRATIONAL, giving agents temporal depth in their planning.

### OCC Emotional Model

Appraisal-based emotional responses grounded in the Ortony, Clore &
Collins framework. Agent-based emotions include Pride, Shame,
Admiration, and Reproach. Compound emotions (Gratitude, Anger,
Remorse, Gratification) emerge from combinations. Personality-prior
calibration derives appraisal weights from the JPAF personality
framework — a Thinking-dominant agent appraises events differently
from a Feeling-dominant one.

### Progressive Attention

Per-principal threshold accumulator that detects urgency spikes,
priority shifts, and decay in attention allocation. Cognitive
attention signals bridge to the orchestration layer — an agent paying
attention to a specific domain will be preferentially routed work in
that domain.

### Personality Calibration

Behaviour tuning through accumulated experience. As the cognitive
architecture observes patterns in goal resolution, emotional
appraisal, and attention allocation, it calibrates the personality
model — closing the loop between experience and identity.

**Vision items** in active development:

- Emergent behavioural synthesis — crystallised behaviours from memory
  and disposition (#406)
- Multi-agent "Inside Out" model with sub-LLMs per cognitive domain
  (#392)
- Cause-effect decision graph engine (#408)
- Memory seeding for fabricated backstory (#398)
- Runtime gut feeling — affect similarity probe (#409)

---

## Differentiation: Why This Matters

### vs LangChain / CrewAI / AutoGen

| Dimension | CaseHub | Competitors |
|-----------|---------|-------------|
| Agent definition | Typed 4-layer descriptors | String role descriptions |
| Capability matching | Subsumption across 12+ vocabularies | String equality |
| Personality | Evolves through experience (JPAF) | Static profile |
| Behavioural compliance | Tracked, enforced, auditable | Not tracked |
| Social cognition | 90+ types, mood-modulated, drive-driven | Not present |
| BDI reasoning | Beliefs, intentions, coalitions, judgment | Not present |
| Multi-format rendering | Claude, OpenAI, A2A machine-readable | Single format |

The production capabilities alone — structured identity, personality
evolution, behavioural contracts, BDI, social cognition — have no
equivalent in any competing framework. The cognitive architecture
extends this into territory no competitor is approaching.

### The Trajectory

Structured identity (production) → Social cognition (production) →
Cognitive architecture (horizon) → Emergent behaviour (vision).

Each stage builds on the previous. Personality evolution requires
structured identity. Social cognition requires personality. Cognitive
architecture requires social cognition signals. Emergent behaviour
requires all three. The platform is building toward agents that
develop genuine behavioural patterns through experience — but the
foundation is already deployed and delivering value.

---

## Platform Consistency

Agent identity is not a separate system — it's woven through the
platform:

- **Trust integration** — ledger reputation scores feed personality
  evolution and compliance tracking. Compliance attestations produce
  tamper-evident audit entries.
- **Orchestration integration** — social cognition renders as
  PromptSections during multi-agent coordination. Disposition-aware
  routing uses JPAF personality for agent selection. BDI beliefs
  feed decomposition context.
- **CBR integration** — agent experience feeds case-based reasoning.
  CBR retrieval is trust-weighted via the AgentTrustProvider SPI,
  bridging ledger trust scores into similarity-based retrieval.
- **Tenancy** — every identity query, every registration, every
  compliance check is tenant-scoped through the platform's
  CurrentPrincipal model.
- **CDI conventions** — NoOp → InMemory → JPA bean ladder follows
  platform conventions. PreferenceProvider-based thresholds use the
  standard ancestor-chain walk.
- **Organisational model** — hierarchical units with typed
  relationships (SUPERVISES, DELEGATES_TO, ESCALATES_TO, REPORTS_TO,
  BACKS_UP). YAML surface. Desiredstate integration for
  organisational drift detection.

---

## Extent

| Component | Modules | Source files | Key metric |
|-----------|---------|-------------|------------|
| Eidos (identity) | 14 | 303 | 12+ vocabulary systems, 48 archetypes |
| Blocks (BDI + social cognition) | ~10 of 25 | ~400 of 903 | 90+ social cognition types |
| Neocortex (cognitive) | 7 | 60+ classes in cognitive-index alone | 5-phase goal lifecycle |
| **Total** | **~31** | **~760+** | |

Full JPA persistence. Flyway migrations. Eval harness with 10 judges
and 18 profiles. Contract test suites. Dual-framework support
(Quarkus + Spring Boot).

---

*Next: [The Shared Foundation](08-shared-foundation.md) — 178 modules
of homogeneous consistency underneath everything.*
