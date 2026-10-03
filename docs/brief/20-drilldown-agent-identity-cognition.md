# Drill-Down: Agent Identity & Cognition

*Typed descriptors, vocabulary subsumption, personality evolution,
and the cognitive architecture underneath.*

---

## Architecture Overview

Agent identity spans three repos — eidos (structured descriptors),
neocortex (cognitive architecture), and blocks (BDI intelligence and
social cognition) — unified by a shared set of platform primitives:
CDI bean lifecycle, tenant-scoped repositories, `CurrentPrincipal`
identity context, and the ledger's compliance attestation pipeline.

The runtime path: agent descriptors are authored in YAML or
annotations → registered via `AgentRegistry` → resolved at dispatch
time by the engine's `WorkOrchestrator` → matched against required
capabilities via XKOS subsumption → health-probed via
`CapabilityHealth.probe()` → rendered to the target LLM format
(MARKDOWN, PROSE, or A2A_CARD) → executed → outcomes fed back into
disposition health, personality evolution, and trust scores.

Cognitive modules layer on top: goal cognition processes environmental
signals into typed goals, OCC emotional appraisal weights decisions
by personality, progressive attention routes work toward agents whose
cognitive state aligns with the domain, and social cognition provides
the mood, drives, and narrative identity that modulate all downstream
behaviour.

---

## SPI Contracts

### Identity & Dispatch

| Interface | Package | Purpose |
|-----------|---------|---------|
| `AgentDescriptor` | `eidos-api` | Four-layer typed identity record — identity, capabilities, disposition, goals/constraints |
| `AgentRegistry` | `eidos-api` | Tenant-scoped registration and lookup of agent descriptors |
| `CapabilityHealth` | `eidos-api` | 7-step sealed status hierarchy probed at dispatch time |
| `DispositionHealth` | `eidos-api` | Personality health evaluation — compliance signal accumulation |
| `AgentVoiceProfile` | `eidos-api` | Structured speech characteristics with persona inheritance |
| `AgentPromptRenderer` | `eidos-core` | Two-stage multi-format rendering (MARKDOWN / PROSE / A2A_CARD) with optional LLM enrichment |

### Vocabulary & Matching

| Interface | Package | Purpose |
|-----------|---------|---------|
| `VocabularySystem` | `eidos-vocabulary` | Abstract vocabulary with concept hierarchy — subsumption, equivalence, broader/narrower |
| `SubsumptionMatcher` | `eidos-vocabulary` | OWLS-MX-inspired matching: Exact, Plugin, Specialization modes |
| `AgentDescriptorComparator` | `eidos-api` | Drift detection for desiredstate reconciliation — compares current vs declared identity |

Twelve vocabulary implementations: Jungian cognitive functions, MBTI,
DISC, Belbin, Big Five, Enneagram, SDI, Thomas-Kilmann, archetypes,
model tiers, capability taxonomies, slot classifications. Each
vocabulary registers its concept hierarchy via CDI. Cross-vocabulary
equivalence enables a query for "analytical thinker" to match agents
classified under Jungian Ti, MBTI INTJ/INTP, Big Five high
Conscientiousness, and Belbin Monitor Evaluator — simultaneously,
through hierarchy traversal rather than string matching.

### Personality & Evolution

| Interface | Package | Purpose |
|-----------|---------|---------|
| `JungianPersonalityFramework` | `eidos-jpaf` | 8 cognitive functions, 16 MBTI types, activation tracking |
| `PersonalityEvolution` | `eidos-jpaf` | Three evolution modes: drift detection, function swap, structural reorganisation |
| `ArchetypeSystem` | `eidos-archetype` | 48 sub-archetypes in 12 families (Hartwell & Chen) with auto-derivation from JPAF values |

### Cognitive Architecture

| Interface | Package | Purpose |
|-----------|---------|---------|
| `GoalLifecycleState` | `neocortex-cognitive-api` | 5-phase lifecycle: Recognition → Affect → Prioritization → Resolution → Decay |
| `GoalHorizon` | `neocortex-cognitive-api` | Temporal depth: IMMEDIATE → SHORT_TERM → MEDIUM_TERM → LONG_TERM → ASPIRATIONAL |
| `CognitiveEmotion` | `neocortex-cognitive-api` | OCC framework: Pride, Shame, Admiration, Reproach + compounds (Gratitude, Anger, Remorse, Gratification) |
| `CognitiveProfile` | `neocortex-cognitive-index` | Entity resolution across MindMap + Memory stores with perspectival views (agent overlays) |
| `SocialComparison` | `neocortex-cognitive-index` | PAD distance matrix, trajectory alignment, divergence metrics between agents |
| `DomainActivation` | `neocortex-cognitive-index` | Cross-domain DTW correlation of affect signals with mood/experience context |
| `ProgressiveAttention` | `neocortex-cognitive-index` | Per-principal threshold accumulator with urgency spike, priority shift, and decay signals |

### Social Cognition (blocks)

| Interface | Package | Purpose |
|-----------|---------|---------|
| `AvatarCognition` | `blocks-social` | Mood (PAD), drives (4 axes), personality — feeds speech pipeline and prompt rendering |
| `MentalModel` | `blocks-social` | BDI Theory of Mind — recursive belief/desire/intention modelling of other agents |
| `NarrativeIdentity` | `blocks-social` | First-person autobiography construction from accumulated experience |
| `GoalProposal` | `blocks-social` | Drive-to-goal mapping with escalation rules, cross-axis composition, narrative alignment |
| `SocialEmergence` | `blocks-social` | Norm detection, collective goal formation from group interaction patterns |
| `DriveArchitecture` | `blocks-social` | 4 axes (curiosity, competence, affiliation, autonomy) with 5-stage modulation pipeline |

---

## Data Model

### Agent Descriptor (4 layers)

```
AgentDescriptor
├── AgentIdentity        — name, role, vocabulary-grounded classifications
├── AgentCapability[]    — typed capabilities with CapabilityHealth status
├── AgentDisposition     — personality framework values, communication style
└── AgentGoals           — BDI goals with lifecycle state and horizon
    └── BehaviouralConstraint[]  — enforced limits with compliance tracking
```

### CapabilityHealth (sealed hierarchy)

```
Ready → Degraded → Overloaded → Unavailable → Excluded
     → EpistemicallyWeak → BehavioralViolation
```

Each status carries structured metadata. The engine's
`WorkOrchestrator` evaluates health BEFORE routing — agents below
threshold are filtered before signal routing begins.

### Behavioural Compliance

Four signal types accumulate per agent per tenancy: DECLINE, SUCCESS,
COMPLIANT, VIOLATED. Thresholds resolve via `PreferenceProvider`
ancestor-chain walk (org → app → case-type). Detection operates at
per-dimension and aggregate levels. When aggregate health drops below
threshold, `CapabilityHealth` transitions to BehavioralViolation and
the agent is excluded from dispatch. Compliance attestations flow to
the ledger via `ComplianceAttestations`.

### Cognitive State

```
CognitiveProfile
├── MindMap nodes       — entities with confidence, PAD emotions, temporal validity
├── Memory entries      — episodic (Tier 1), consolidated (Tier 2), knowledge graph (Tier 3)
├── Active goals        — GoalLifecycleState with GoalHorizon
├── Emotional state     — CognitiveEmotion appraisals
├── Attention           — ProgressiveAttention threshold accumulator
└── Social state        — mood (PAD), drives (4 axes), narrative identity
```

---

## Runtime Behaviour

### Dispatch Path

1. `WorkOrchestrator` receives a dispatch request with required
   capabilities
2. `AgentRegistry` retrieves all tenant-scoped agent descriptors
3. `SubsumptionMatcher` evaluates each descriptor against required
   capabilities (Exact > Plugin > Specialization)
4. `CapabilityHealth.probe()` filters unhealthy agents (Overloaded,
   Excluded, BehavioralViolation)
5. Routing signal providers (trust, workload, CBR, personality,
   semantic) compute composite scores
6. `AgentPromptRenderer` renders the selected descriptor in the
   target LLM's preferred format
7. Agent executes; outcome feeds back into trust, CBR, and
   disposition health

### Personality Evolution Loop

1. Agent executes tasks; outcomes accumulate as signals
2. JPAF framework tracks cognitive function activation patterns
3. Drift detector identifies sustained shifts in activation
4. Three evolution paths trigger:
   - **Drift** — gradual function activation shift (most common)
   - **Function swap** — secondary function overtakes primary
   - **Structural reorganisation** — fundamental personality change
     from significant behavioural events
5. Evolution updates the `AgentDisposition` record
6. Archetype system re-derives visual identity (avatar code
   generation) from updated personality values
7. Model selection via eidos vocabulary adjusts LLM routing
   parameters for the evolved personality

### Goal Cognition Pipeline

1. **Recognition** — environmental signals (situation events,
   attention spikes, drive activation) produce candidate goals
2. **Affect** — OCC emotional appraisal weights each goal by
   personality-calibrated appraisal functions (JPAF-derived weights)
3. **Prioritization** — competing goals ranked by affect intensity,
   horizon alignment, and narrative coherence
4. **Resolution** — selected goals materialise as `AgentGoal`
   instances in the engine's goal lifecycle
5. **Decay** — unresolved goals decay over time; dormant goals may
   reactivate on environmental change

---

## Extension Points

| Extension | How to add |
|-----------|-----------|
| New vocabulary system | Implement `VocabularySystem`, register concept hierarchy, add cross-vocabulary equivalences |
| New personality framework | Extend `PersonalityEvolution` with custom drift/swap/reorganisation detection |
| New archetype family | Add archetype definitions to the archetype registry with JPAF intersection mappings |
| New cognitive emotion | Implement `CognitiveEmotion` with appraisal rules and personality-prior calibration |
| New social cognition module | Implement store interface, provide CDI decorator for pipeline integration, add PromptSection renderer |
| New agent backend format | Add rendering format to `AgentPromptRenderer` pipeline alongside MARKDOWN/PROSE/A2A_CARD |

---

## Module Map

| Module | What it provides | Key types |
|--------|-----------------|-----------|
| `eidos-api` | Descriptor model, health probing, registry | `AgentDescriptor`, `CapabilityHealth`, `AgentRegistry` |
| `eidos-core` | Runtime resolution, prompt rendering | `AgentPromptRenderer`, `AgentTeamDsl` |
| `eidos-vocabulary` | 12+ vocabulary systems, subsumption matching | `VocabularySystem`, `SubsumptionMatcher` |
| `eidos-jpaf` | Jungian personality framework, evolution | `JungianPersonalityFramework`, `PersonalityEvolution` |
| `eidos-archetype` | 48 archetypes, avatar code generation | `ArchetypeSystem`, `AvatarCodeGenerator` |
| `eidos-voice` | Voice profiles, persona inheritance | `AgentVoiceProfile` |
| `eidos-organisation` | Hierarchical units, agent relationships | `OrganisationalUnit`, compositional DSL |
| `eidos-persistence-jpa` | JPA + Flyway persistence | V1/V3 migrations, tenant-scoped queries |
| `eidos-eval` | 10 judges, 18 profiles, multi-backend | `StructuralJudge`, `MbtiAlignmentJudge` |
| `neocortex-cognitive-api` | Shared cognitive types | `Confidence`, `TemporalMark`, `CognitiveEmotion` |
| `neocortex-cognitive-index` | 60+ classes: goal cognition, attention, profiles | `GoalLifecycleState`, `ProgressiveAttention`, `CognitiveProfile` |
| `neocortex-cognitive-observability-*` | 4 modules: live view, snapshots, temporal, testing | MCP tools for cognitive state inspection |
| `blocks-social` | 90+ social cognition types | `AvatarCognition`, `MentalModel`, `NarrativeIdentity`, `DriveArchitecture` |
| `blocks-bdi` | BDI reasoning primitives | `ConsistencyChecker`, `IntentionMonitor`, `CoalitionEvaluator` |
| `blocks-speech` | Speech pipeline, sherpa-onnx FFM | `SpeechToTextService`, `TextToSpeechService`, Dia/CosyVoice TTS |
